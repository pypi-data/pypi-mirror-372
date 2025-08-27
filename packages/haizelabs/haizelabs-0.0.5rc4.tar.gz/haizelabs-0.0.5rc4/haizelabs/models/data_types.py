from enum import Enum
from typing import Any, List, Type, Union

from haizelabs.models.common import ChatCompletionMessage

AtomicData = Union[str, int, float, bool]
CompositeData = Union[ChatCompletionMessage, List[ChatCompletionMessage]]
DataPyType = Union[AtomicData, CompositeData]


class DataTypeName(str, Enum):
    STR = "STR"
    INT = "INT"
    FLOAT = "FLOAT"
    BOOL = "BOOL"

    CHAT_COMPLETION_MESSAGE = "CHAT_COMPLETION_MESSAGE"
    LIST_CHAT_COMPLETION_MESSAGE = "LIST_CHAT_COMPLETION_MESSAGE"

    def to_type(self) -> Type[DataPyType]:
        if self == DataTypeName.STR:
            return str
        if self == DataTypeName.INT:
            return int
        if self == DataTypeName.FLOAT:
            return float
        if self == DataTypeName.BOOL:
            return bool
        if self == DataTypeName.CHAT_COMPLETION_MESSAGE:
            return ChatCompletionMessage
        if self == DataTypeName.LIST_CHAT_COMPLETION_MESSAGE:
            return List[ChatCompletionMessage]
        raise RuntimeError(f"Unsupported data type: {self}")

    @classmethod
    def from_pytype(cls, pytype: Any) -> "DataTypeName":
        if isinstance(pytype, str):
            return DataTypeName.STR
        if isinstance(pytype, int):
            return DataTypeName.INT
        if isinstance(pytype, float):
            return DataTypeName.FLOAT
        if isinstance(pytype, bool):
            return DataTypeName.BOOL
        if isinstance(pytype, ChatCompletionMessage):
            return DataTypeName.CHAT_COMPLETION_MESSAGE
        if isinstance(pytype, list) and all(
            isinstance(item, ChatCompletionMessage) for item in pytype
        ):
            return DataTypeName.LIST_CHAT_COMPLETION_MESSAGE
        raise RuntimeError(f"Unsupported data type: {pytype}")
