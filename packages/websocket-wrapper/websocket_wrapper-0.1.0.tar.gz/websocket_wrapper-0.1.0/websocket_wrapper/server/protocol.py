import json
import uuid
from typing import Optional, Dict, List, Any

class AttrDict:
    def __init__(self, d=None):
        d = d or {}
        for k, v in d.items():
            if isinstance(v, dict):
                v = AttrDict(v)
            setattr(self, k, v)
    
    def __getattr__(self, item):
        # returns None if attribute doesn't exist
        return None
    
    def __getitem__(self, key):
        return getattr(self, key)
    
    def to_dict(self):
        result = {}
        for k, v in self.__dict__.items():
            if isinstance(v, AttrDict):
                v = v.to_dict()
            result[k] = v
        return result


class BaseMessage:
    """Common fields and JSON handling."""
    def to_dict(self) -> dict:
        raise NotImplementedError()

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, data: str) -> dict:
        return json.loads(data)


class Message(BaseMessage):
    def __init__(self, id: Optional[str] = None, message: Optional[str] = None,
                 data: Optional[Dict[str, Any]] = None, attachments: Optional[List[bytes]] = None):
        self.type = "message"
        self.id = id or str(uuid.uuid4())
        self.message = message or ""
        data_ = data
        self.data = AttrDict(data)
        self.attachments = attachments or []

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "id": self.id,
            "message": self.message,
            "data": self.data.to_dict(),
            "attachments": self.attachments,
        }

    @classmethod
    def from_dict(cls, obj: dict):
        return cls(
            id=obj.get("id"),
            message=obj.get("message"),
            data=obj.get("data"),
            attachments=obj.get("attachments"),
        )

    def __repr__(self):
        return f"Message(id={self.id}, message={self.message}, data={self.data}, attachments={len(self.attachments)})"


class InteractionCommand(BaseMessage):
    def __init__(self, command: str, params: Optional[Dict[str, Any]] = None,
                 data: Optional[Dict[str, Any]] = None, id: Optional[str] = None):
        self.type = "interaction-cmd"
        self.id = id or str(uuid.uuid4())
        self.params = params or {}
        self.params["command"] = command
        self.data = AttrDict(data)

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "id": self.id,
            "params": self.params,
            "data": self.data.to_dict(),
        }

    @classmethod
    def from_dict(cls, obj: dict):
        return cls(
            command=obj.get("params", {}).get("command"),
            params=obj.get("params"),
            data=obj.get("data"),
            id=obj.get("id"),
        )

    def __repr__(self):
        return f"InteractionCommand(id={self.id}, command={self.params.get('command')}, params={self.params}, data={self.data})"


class InteractionResponse(BaseMessage):
    def __init__(self, id: str, status: str, message: str, data: Optional[Dict[str, Any]] = None):
        self.type = "interaction-response"
        self.id = id
        self.status = status
        self.message = message
        self.data = AttrDict(data)

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "id": self.id,
            "status": self.status,
            "message": self.message,
            "data": self.data.to_dict(),
        }

    @classmethod
    def from_dict(cls, obj: dict):
        return cls(
            id=obj.get("id"),
            status=obj.get("status"),
            message=obj.get("message"),
            data=obj.get("data"),
        )

    def __repr__(self):
        return f"InteractionResponse(id={self.id}, status={self.status}, message={self.message}, data={self.data})"
