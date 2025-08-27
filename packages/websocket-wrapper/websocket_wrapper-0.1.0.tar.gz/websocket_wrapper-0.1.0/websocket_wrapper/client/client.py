# client.py
import asyncio
import json
import logging
import sys
import threading
import uuid
from typing import Callable, Any, Dict, Optional, List
import websockets
from websockets.client import WebSocketClientProtocol
from typing import Union

class InteractionCommand:
    def __init__(self, id: str, command: str, params: dict = None, data: dict = None):
        self.id = id
        self.command = command
        self.params = params or {}
        self.data = data or {}
    
    def __repr__(self):
        return f"<InteractionCommand id={self.id} command={self.command} params={self.params} data={self.data}>"


class InteractionResponse:
    def __init__(self, id: str, status: str, message: str, data: dict = None):
        self.id = id
        self.status = status
        self.message = message
        self.data = data or {}
    
    def __repr__(self):
        return f"<InteractionResponse id={self.id} status={self.status} message={self.message} data={self.data}>"
    

class Message:
    def __init__(self, id: str, content: str, data: dict = None, attachments: list = None):
        self.id = id
        self.content = content
        self.data = data or {}
        self.attachments = attachments or []
        
    def __repr__(self):
        return f"<Message id={self.id} content={self.content} data={self.data} attachments={self.attachments}>"
        
        
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

class Client:
    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        self.host = host
        self.port = port
        self.uri = f"ws://{host}:{port}"

        self.websocket: Optional[WebSocketClientProtocol] = None
        self.is_connected = False
        self._stop_flag = threading.Event()

        self._listeners: Dict[str, List[Callable[..., Any]]] = {
            "on_connect": [],
            "on_disconnect": [],
            "on_message": [],
            "on_error": [],
            "on_command_response": [],
        }

        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None

        # registry of pending command futures
        self._pending: Dict[str, asyncio.Future] = {}

    # ---------------- Listener API ----------------
    def register_listener(self, event: str, callback: Callable[..., Any]):
        if event not in self._listeners:
            raise ValueError(f"Invalid event listener: {event}")
        self._listeners[event].append(callback)

    async def _emit(self, event: str, *args, **kwargs):
        for func in self._listeners.get(event, []):
            try:
                if asyncio.iscoroutinefunction(func):
                    await func(*args, **kwargs)
                else:
                    func(*args, **kwargs)
            except Exception as e:
                logging.exception(f"Listener '{event}' raised: {e}")

    # ---------------- Public API ----------------
    def send_json(self, message: dict):
        if not self._loop or not self.is_connected:
            logging.warning("Not connected.")
            return
        fut = asyncio.run_coroutine_threadsafe(self._send_json(message), self._loop)
        return fut

    async def send_command(self, command: str, params: Optional[dict] = None,
                        data: Optional[dict] = None, timeout: float = 10.0):
        if not self._loop:
            raise RuntimeError("Client loop not initialized")

        cmd_id = str(uuid.uuid4())
        message = {
            "type": "interaction-cmd",
            "id": cmd_id,
            "params": params or {},
            "data": data or {},
        }
        message["params"]["command"] = command

        # ✅ create future on *current* loop (the caller’s loop)
        loop = asyncio.get_running_loop()
        fut = loop.create_future()
        self._pending[cmd_id] = fut

        # schedule send in background loop
        asyncio.run_coroutine_threadsafe(self._send_json(message), self._loop)

        try:
            return await asyncio.wait_for(fut, timeout)
        finally:
            self._pending.pop(cmd_id, None)

    def send_message(self, message: Union[str, Message], data: Optional[dict] = None, attachments: Optional[List[bytes]] = None):
        if isinstance(message, Message):
            payload = {
                "type": "message",
                "id": message.id,
                "message": message.content,
                "data": message.data,
                "attachments": message.attachments
            }
        else:
            payload = {
                "type": "message",
                "id": str(uuid.uuid4()),
                "message": message,
                "data": data or {},
                "attachments": attachments or []
            }
        self.send_json(payload)

    def stop(self):
        if self._loop:
            asyncio.run_coroutine_threadsafe(self._stop_async(), self._loop)
        self._stop_flag.set()
    async def wait_until_ready(self, timeout: float = 10.0):
        start = asyncio.get_event_loop().time()
        while (not self._loop or not self.is_connected) and (asyncio.get_event_loop().time() - start < timeout):
            await asyncio.sleep(0.05)
        if not self._loop or not self.is_connected:
            raise TimeoutError("Client not ready within timeout")

    # ---------------- Internals ----------------
    async def _send_json(self, message: dict):
        if not self.is_connected or not self.websocket:
            logging.warning("Cannot send, not connected.")
            return
        try:
            if message.get("attachments"):
                message["attachments"] = []
            await self.websocket.send(json.dumps(message))
        except Exception as e:
            logging.error(f"Send failed: {e}")
            await self.disconnect()

    async def _stop_async(self):
        self._stop_flag.set()
        await self.disconnect()

    async def disconnect(self):
        if self.is_connected and self.websocket:
            try:
                await self.websocket.close()
            except Exception:
                pass
            finally:
                self.is_connected = False
                self.websocket = None
                await self._emit("on_disconnect")
                logging.info("Disconnected.")

    async def _process_message(self, msg_obj: dict):
        msg_type = msg_obj.get("type")

        if msg_type == "interaction-response":
            resp_obj = InteractionResponse(
                id=msg_obj.get("id"),
                status=msg_obj.get("status"),
                message=msg_obj.get("message"),
                data=msg_obj.get("data")
            )

            # Complete pending future
            cmd_id = resp_obj.id
            if cmd_id in self._pending:
                fut = self._pending[cmd_id]
                if not fut.done():
                    loop = fut.get_loop()
                    loop.call_soon_threadsafe(fut.set_result, resp_obj)
            await self._emit("on_command_response", resp_obj)

        elif msg_type == "message":
            msg_obj = Message(
                id=msg_obj.get("id"),
                content=msg_obj.get("message"),
                data=msg_obj.get("data"),
                attachments=msg_obj.get("attachments")
            )
            await self._emit("on_message", msg_obj)

    async def _read_messages(self):
        try:
            async for message in self.websocket:
                try:
                    msg_obj = json.loads(message)
                    await self._process_message(msg_obj)
                except json.JSONDecodeError:
                    logging.warning(f"Received non-JSON: {message[:80]!r}")
        except (websockets.ConnectionClosed, asyncio.CancelledError):
            pass
        finally:
            self.is_connected = False
            self.websocket = None
            await self._emit("on_disconnect")

    async def _connect_and_run(self):
        delay = 1
        while not self._stop_flag.is_set():
            try:
                self.websocket = await websockets.connect(self.uri)
                self.is_connected = True
                logging.info(f"Connected to {self.uri}")
                await self._emit("on_connect")

                await self._read_messages()
            except websockets.ConnectionClosed:
                logging.info("Connection closed by server.")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Connection failed: {e}")
                await self._emit("on_error", e)

            if not self._stop_flag.is_set():
                logging.info(f"Retrying in {delay}s...")
                await asyncio.sleep(delay)
                delay = min(delay * 2, 60)

        await self.disconnect()

    # ---------------- Thread Management ----------------
    def run_in_background(self):
        if self._thread and self._thread.is_alive():
            logging.warning("Client already running.")
            return

        def _thread_main():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            try:
                self._loop.run_until_complete(self._connect_and_run())
            finally:
                self._loop.close()
                self._loop = None

        self._thread = threading.Thread(target=_thread_main, daemon=True)
        self._thread.start()
        logging.info("Client started in background thread.")

    async def reply_to_command(self, command_or_id: Union[InteractionCommand, str], status="ok", message="OK", data=None):
        resp = InteractionResponse(
            id=command_or_id.id if isinstance(command_or_id, InteractionCommand) else command_or_id,
            status=status,
            message=message,
            data=data
        )
        await self.send_json({
            "type": "interaction-response",
            "id": resp.id,
            "status": resp.status,
            "message": resp.message,
            "data": resp.data
        })