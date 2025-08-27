# server.py
import asyncio
import json
import logging
import sys
from typing import Callable, Any, Dict, Optional, Set
from websockets.server import serve, ServerConnection

from .client import ServerClientWS  # wrapper class
from .protocol import Message, InteractionCommand, InteractionResponse


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

class Server:
    def __init__(self, host="127.0.0.1", port=8000, auth_required=False):
        self.host = host
        self.port = port
        self.auth_required = auth_required

        self.server: Optional[asyncio.AbstractServer] = None
        self.unauthenticated_clients: Set[ServerClientWS] = set()
        self.authenticated_clients: Set[ServerClientWS] = set()

        self._listeners: Dict[str, Callable[..., Any]] = {
            "on_connect": self._default_listener,
            "on_disconnect": self._default_listener,
            "on_error": self._default_listener,
            "on_message": self._default_listener,
            "on_auth": self._default_listener,
            "on_auth_fail": self._default_listener,
            "on_ready": self._default_listener,
            "on_shutdown": self._default_listener,
        }

        self.commands: Dict[str, Dict[str, Any]] = {}
        if self.auth_required:
            self.register_command("auth", self._default_auth_handler, requires_auth=False)

    # ----------------- Listener system -----------------
    def register_listener(self, event: str, callback: Callable[..., Any]):
        if event not in self._listeners:
            raise ValueError(f"Invalid event listener: {event}")
        self._listeners[event] = callback

    async def _emit(self, event: str, *args, **kwargs):
        func = self._listeners.get(event)
        if not func:
            return
        try:
            if asyncio.iscoroutinefunction(func):
                await func(*args, **kwargs)
            else:
                func(*args, **kwargs)
        except Exception as e:
            logging.exception(f"Listener '{event}' raised: {e}")

    async def _default_listener(self, *args, **kwargs):
        pass

    # ----------------- Auth system -----------------
    async def _default_auth_handler(self, client, id, params, data):
        await client.reply_to_command(command_or_id=id, status="error", message = "Auth not implemented on server.")

    async def _on_auth_success(self, client: ServerClientWS, id: str):
        if client in self.unauthenticated_clients:
            self.unauthenticated_clients.remove(client)
            self.authenticated_clients.add(client)
            client.is_authenticated = True
            await self._emit("on_auth", client)
            await client.reply_to_command(command_or_id=id, status="ok", message="Authenticated successfully")
        else:
            logging.info("Duplicate auth attempt ignored.")

    async def _on_auth_fail(self, client: ServerClientWS, id: str):
        await self._emit("on_auth_fail", client)
        await client.reply_to_command(command_or_id=id, status="failed", message="Authentication failed")

    def register_command(self, name: str, handler_func: Callable[..., Any], requires_auth=True):
        if not self.auth_required:
            requires_auth = False
        self.commands[name] = {"handler": handler_func, "requires_auth": requires_auth}
        logging.info(f"Command '{name}' registered. Requires auth: {requires_auth}")

    # ----------------- Client handling -----------------
    async def _handle_client(self, ws: ServerConnection):
        client = ServerClientWS(ws, server=self)
        logging.info(f"New connection from {client.remote_address}")

        if self.auth_required:
            self.unauthenticated_clients.add(client)
            await client.send_json({"type": "info", "message": "Authentication required"})
        else:
            self.authenticated_clients.add(client)
            await client.send_json({"type": "info", "message": "Welcome!"})

        await self._emit("on_connect", client)

        try:
            async for raw_msg in ws:
                try:
                    msg = json.loads(raw_msg)
                    await self._process_message(client, msg)
                except json.JSONDecodeError:
                    logging.warning(f"Invalid JSON from {client.remote_address}: {raw_msg}")
        except Exception as e:
            logging.error(f"Error with client {client.remote_address}: {e}")
            await self._emit("on_error", client, e)
        finally:
            self.unauthenticated_clients.discard(client)
            self.authenticated_clients.discard(client)
            await self._emit("on_disconnect", client)

    async def _process_message(self, client: ServerClientWS, msg: dict):
        msg_type = msg.get("type")

        if msg_type == "message":
            message_obj = Message.from_dict(msg)
            await self._emit("on_message", client, message_obj)

        elif msg_type == "interaction-cmd":
            command_obj = InteractionCommand.from_dict(msg)
            await self._handle_command(client, command_obj)

        else:
            logging.warning(f"Unknown message type from {client.remote_address}: {msg_type}")

    async def _handle_command(self, client: ServerClientWS, command_obj: InteractionCommand):
        cmd = command_obj.params.get("command")
        id = command_obj.id
        data = command_obj.data
        params = command_obj.params

        if not id:
            await client.send_command_response(None, "error", "Missing command ID")
            return

        if not cmd:
            await client.send_command_response(id, "error", "Missing command name")
            return

        if cmd not in self.commands:
            await client.send_command_response(id, "not found", f"Unknown command: {cmd}")
            return

        info = self.commands[cmd]
        if info["requires_auth"] and client not in self.authenticated_clients:
            await client.send_command_response(id, "auth required", "Authentication required")
            return

        try:
            # Pass the class object directly to the handler
            await info["handler"](client, command_obj)
        except Exception as e:
            logging.exception(f"Command '{cmd}' failed: {e}")
            await client.send_command_response(id, "error", f"Exception: {e}")
            await self._emit("on_error", client, e)

    async def broadcast(self, message_obj: dict, exclude=None, include_unauthenticated=False):
        if exclude is None:
            exclude = set()
        
        if include_unauthenticated:
            clients = self.authenticated_clients | self.unauthenticated_clients
        else:
            clients = self.authenticated_clients
        
        tasks = [c.send_message(message_obj) for c in clients if c not in exclude]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    # ----------------- Server lifecycle -----------------
    async def run(self, blocking: bool = True):
        self.server = await serve(self._handle_client, self.host, self.port)
        logging.info(f"Server started on {self.host}:{self.port}")
        await self._emit("on_ready")

        if blocking:
            async with self.server:
                await self.server.serve_forever()
            logging.info("Server stopped.")
        else:
            self._serve_task = asyncio.create_task(self.server.serve_forever())
            logging.info("Server running in background (non-blocking).")

    async def shutdown(self):
        logging.info("Shutting down server...")
        for c in self.authenticated_clients | self.unauthenticated_clients:
            await c.close()

        if self.server:
            self.server.close()
            await self.server.wait_closed()
        await self._emit("on_shutdown")
        logging.info("Server shutdown complete.")
