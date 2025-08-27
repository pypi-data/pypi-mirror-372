from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from pydantic import BaseModel, Field, TypeAdapter, field_validator, model_validator
from pydantic import ValidationError as PydanticValidationError

from haizelabs.models.common import ChatCompletionMessage
from haizelabs.models.data_types import DataPyType, DataTypeName

MIN_COLUMN_NAME_LENGTH = 1
MAX_COLUMN_NAME_LENGTH = 255


class ColumnType(str, Enum):
    SYSTEM_INPUT_PARAM = "system_input_param"
    LABEL = "label"
    OTHER = "other"

    # TODO[Jack]: These types are a little weird since they are only ever used in the standard columns
    SYSTEM_INPUT_MESSAGE = "system_input_message"
    SYSTEM_OUTPUT = "system_output"
    EXPECTED_OUTPUT = "expected_output"


T = TypeVar("T", bound=DataPyType)


class BaseDataColumn(BaseModel, Generic[T], ABC):
    name: str = Field(
        min_length=MIN_COLUMN_NAME_LENGTH, max_length=MAX_COLUMN_NAME_LENGTH
    )
    data_type_name: DataTypeName
    formatted_name: Optional[str] = Field(
        default=None,
        min_length=MIN_COLUMN_NAME_LENGTH,
        max_length=MAX_COLUMN_NAME_LENGTH,
    )
    column_type: ColumnType
    is_system_input_param: bool = Field(
        default=False,
        description="Restricts this column to be only for formatting AI system inputs",
    )

    model_config = {"frozen": True}

    @classmethod
    @model_validator(mode="before")
    def set_formatted_name(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if "formatted_name" not in values:
            values["formatted_name"] = values["name"]
        return values

    @classmethod
    @field_validator("name")
    def validate_name(cls, value: str) -> str:
        if not value.isidentifier():
            raise ValueError("Column name must be a valid Python variable name")
        return value

    @classmethod
    @abstractmethod
    def validate_type(cls, value: DataPyType, coerce: bool = True) -> T:
        pass

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return (
                self.name == other.name and self.data_type_name == other.data_type_name
            )
        return False

    def __hash__(self) -> int:
        return hash((self.name, self.data_type_name))


class StrColumn(BaseDataColumn[str]):
    data_type_name: Literal[DataTypeName.STR] = DataTypeName.STR

    @classmethod
    def validate_type(cls, value: DataPyType, coerce: bool = True) -> str:
        if isinstance(value, str):
            return value
        if coerce and isinstance(value, (int, float, bool)):
            return str(value)
        raise PydanticValidationError(f"Value {value} is not a string")


class IntColumn(BaseDataColumn[int]):
    data_type_name: Literal[DataTypeName.INT] = DataTypeName.INT

    @classmethod
    def validate_type(cls, value: DataPyType, coerce: bool = True) -> int:
        if isinstance(value, int):
            return value
        if coerce and isinstance(value, str):
            try:
                return int(value)
            except ValueError as e:
                raise PydanticValidationError(
                    f"Value {value} is not a valid integer"
                ) from e
        raise PydanticValidationError(f"Value {value} is not a valid integer")


class FloatColumn(BaseDataColumn[float]):
    data_type_name: Literal[DataTypeName.FLOAT] = DataTypeName.FLOAT

    @classmethod
    def validate_type(cls, value: DataPyType, coerce: bool = True) -> float:
        if isinstance(value, float):
            return value
        if coerce and isinstance(value, (int, str)):
            return float(value)
        raise PydanticValidationError(f"Value {value} is not a float")


class BoolColumn(BaseDataColumn[bool]):
    data_type_name: Literal[DataTypeName.BOOL] = DataTypeName.BOOL

    @classmethod
    def validate_type(cls, value: DataPyType, coerce: bool = True) -> bool:
        if isinstance(value, bool):
            return value
        if coerce and isinstance(value, str):
            try:
                return bool(value)
            except ValueError as e:
                raise PydanticValidationError(
                    f"Value {value} is not a valid boolean"
                ) from e
        raise PydanticValidationError(f"Value {value} is not a boolean")


class ChatCompletionMessageColumn(BaseDataColumn[ChatCompletionMessage]):
    data_type_name: Literal[DataTypeName.CHAT_COMPLETION_MESSAGE] = (
        DataTypeName.CHAT_COMPLETION_MESSAGE
    )

    @classmethod
    def validate_type(
        cls, value: DataPyType, coerce: bool = True
    ) -> ChatCompletionMessage:
        if isinstance(value, ChatCompletionMessage):
            return value

        if coerce and isinstance(value, dict):
            try:
                return ChatCompletionMessage.model_validate(value)
            except PydanticValidationError as e:
                raise PydanticValidationError(
                    f"Value {value} is not a valid ChatCompletionMessage"
                ) from e

        raise PydanticValidationError(
            f"Value {value} is not a valid ChatCompletionMessage, got {type(value)}"
        )


class ListChatCompletionMessageColumn(BaseDataColumn[List[ChatCompletionMessage]]):
    data_type_name: Literal[DataTypeName.LIST_CHAT_COMPLETION_MESSAGE] = (
        DataTypeName.LIST_CHAT_COMPLETION_MESSAGE
    )

    @classmethod
    def validate_type(
        cls, value: DataPyType, coerce: bool = True
    ) -> List[ChatCompletionMessage]:
        if not isinstance(value, list):
            raise PydanticValidationError(f"Value {value} is not a list")
        return [
            ChatCompletionMessageColumn.validate_type(item, coerce=coerce)
            for item in value
        ]


DataColumn = Union[
    StrColumn,
    IntColumn,
    FloatColumn,
    BoolColumn,
    ChatCompletionMessageColumn,
    ListChatCompletionMessageColumn,
]


def get_data_column_class(obj: Any) -> Type[DataColumn]:
    if isinstance(obj, str):
        return StrColumn
    elif isinstance(obj, int):
        return IntColumn
    elif isinstance(obj, float):
        return FloatColumn
    elif isinstance(obj, bool):
        return BoolColumn
    elif isinstance(obj, ChatCompletionMessage):
        return ChatCompletionMessageColumn
    elif isinstance(obj, List) and all(
        isinstance(item, ChatCompletionMessage) for item in obj
    ):
        return ListChatCompletionMessageColumn
    else:
        # Big assumption here, but we're just going to assume that the column can be stringified
        return StrColumn


@dataclass(frozen=True)
class DataColumns(Iterable[DataColumn]):
    columns: Tuple[DataColumn, ...]
    _column_indexes: Dict[str, int] = field(init=False)

    def __post_init__(self) -> None:
        if len(set(column.name for column in self.columns)) != len(self.columns):
            raise ValueError("DataColumns must have unique column names")

        if StandardColumns.SYSTEM_INPUT in self.columns and any(
            column.column_type == ColumnType.SYSTEM_INPUT_PARAM
            for column in self.columns
        ):
            raise ValueError(
                f"Cannot have both system input param columns and the {StandardColumns.SYSTEM_INPUT.name} column"
            )

        output_columns = filter(
            lambda c: c.column_type == ColumnType.SYSTEM_OUTPUT, self.columns
        )
        if len(list(output_columns)) > 1:
            raise ValueError("DataColumns must have at most one system output column")

        input_columns = filter(
            lambda c: c.column_type == ColumnType.SYSTEM_INPUT_MESSAGE, self.columns
        )
        if len(list(input_columns)) > 1:
            raise ValueError("DataColumns must have at most one system input column")

        expected_output_columns = filter(
            lambda c: c.column_type == ColumnType.EXPECTED_OUTPUT, self.columns
        )
        if len(list(expected_output_columns)) > 1:
            raise ValueError("DataColumns must have at most one expected output column")

        label_columns = filter(
            lambda c: c.column_type == ColumnType.LABEL, self.columns
        )
        if len(list(label_columns)) > 1:
            raise ValueError("DataColumns must have at most one label column")

        object.__setattr__(
            self,
            "_column_indexes",
            {column.name: idx for idx, column in enumerate(self.columns)},
        )

    @classmethod
    def from_list(cls, columns: Iterable[DataColumn]) -> "DataColumns":
        return cls(
            tuple(
                [TypeAdapter(DataColumn).validate_python(column) for column in columns]
            )
        )

    def get_index(self, column_name: str) -> int:
        return self._column_indexes[column_name]

    def has_column_name(self, column_name: str) -> bool:
        return column_name in self._column_indexes

    def has_column(self, column: DataColumn) -> bool:
        return (
            self.has_column_name(column.name)
            and self.columns[self.get_index(column.name)] == column
        )

    def is_subset_of(self, other: "DataColumns") -> bool:
        return set(self.columns) <= set(other.columns)

    def filter_by_type(self, column_type: ColumnType) -> Union["DataColumns", None]:
        columns = tuple(
            column for column in self.columns if column.column_type == column_type
        )
        if len(columns) == 0:
            return None
        return DataColumns(columns)

    def __iter__(self) -> Iterator[DataColumn]:
        return iter(self.columns)

    def __len__(self) -> int:
        return len(self.columns)

    def __getitem__(self, key: Union[str, int]) -> DataColumn:
        if isinstance(key, str):
            return self.columns[self.get_index(key)]
        elif isinstance(key, int):
            return self.columns[key]
        else:
            raise ValueError(f"Invalid key type for DataColumns: {type(key)}")


class StandardColumns:
    SYSTEM_INPUT = ListChatCompletionMessageColumn(
        name="system_input",
        formatted_name="System Input",
        column_type=ColumnType.SYSTEM_INPUT_MESSAGE,
    )
    SYSTEM_OUTPUT = ChatCompletionMessageColumn(
        name="system_output",
        formatted_name="System Output",
        column_type=ColumnType.SYSTEM_OUTPUT,
    )
    EXPECTED_OUTPUT = ChatCompletionMessageColumn(
        name="expected_output",
        formatted_name="Expected Output",
        column_type=ColumnType.EXPECTED_OUTPUT,
    )
    ENUM_LABEL = StrColumn(
        name="enum_label",
        formatted_name="Enum Label",
        column_type=ColumnType.LABEL,
    )
    CONTINUOUS_LABEL = FloatColumn(
        name="continuous_label",
        formatted_name="Continuous Label",
        column_type=ColumnType.LABEL,
    )
