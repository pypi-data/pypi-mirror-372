from enum import Enum
from typing import Union

from pydantic import BaseModel


class Role(str, Enum):
    ASSISTANT = "assistant"
    USER = "user"
    SYSTEM = "system"
    DEVELOPER = "developer"


class ChatCompletionMessage(BaseModel):
    role: Role
    content: str

    def __init__(self, role: Union[Role, str], content: str) -> None:
        if isinstance(role, str):
            role = Role(role)
        super().__init__(role=role, content=content)
