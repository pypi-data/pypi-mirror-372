import json
import logging
from websockets.server import ServerConnection
import uuid
from typing import Callable, Any, Dict, Optional, Union
from .protocol import Message, InteractionCommand, InteractionResponse

class ServerClientWS:
    def __init__(self, ws: ServerConnection, server):
        self.ws = ws
        self.is_authenticated = False
        self.server = server



    @property
    def remote_address(self):
        return self.ws.remote_address if hasattr(self.ws, "remote_address") else "unknown"

    async def send_json(self, obj: dict):
        try:
            await self.ws.send(json.dumps(obj))
        except Exception as e:
            logging.error(f"Failed to send JSON to {self.remote_address}: {e}")

    async def send_command_response(self, response: Union[InteractionResponse, dict] = None,
                                    *, id: str = None, status: str = None, message: str = None, data: dict = None):
        if isinstance(response, InteractionResponse):
            payload = response.to_dict()
        else:
            payload = {
                "type": "interaction-response",
                "id": id,
                "status": status,
                "message": message,
                "data": data or {},
            }
        await self.send_json(payload)

    async def send_message(self, message_obj: Union[Message, dict] = None, *, id: str = None,
                           message: str = None, data: dict = None, attachments: list = None):
        if isinstance(message_obj, Message):
            payload = message_obj.to_dict()
        else:
            payload = {
                "type": "message",
                "id": id or str(uuid.uuid4()),
                "message": message or "",
                "data": data or {},
                "attachments": attachments or [],
            }
        await self.send_json(payload)

    # async def reply_to_command(self, command_or_id: Union[str, "InteractionCommand"], status="ok",
    #                            message="OK", data=None):
    #     cmd_id = command_or_id.id if hasattr(command_or_id, "id") else command_or_id
    #     resp = InteractionResponse(id=cmd_id, status=status, message=message, data=data)
    #     await self.send_command_response(resp)
    async def reply_to_command(self, command_or_id, status="ok", message="OK", data=None):
        if isinstance(command_or_id, InteractionCommand):
            cmd_id = command_or_id.id
        else:
            cmd_id = command_or_id
        resp = InteractionResponse(id=cmd_id, status=status, message=message, data=data)
        await self.send_command_response(resp)


