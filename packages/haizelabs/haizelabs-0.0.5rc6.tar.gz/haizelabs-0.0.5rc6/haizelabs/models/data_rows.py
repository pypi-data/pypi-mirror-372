from typing import Tuple, TypeVar

from pydantic import BaseModel, ValidationError, model_validator

from haizelabs.models.data_columns import DataColumns
from haizelabs.models.data_types import DataPyType

T = TypeVar("T", bound=DataPyType)


class DataRow(BaseModel):
    columns: DataColumns
    data: Tuple[DataPyType, ...]

    @model_validator(mode="after")
    def validate_data(self) -> "DataRow":
        if len(self.columns) != len(self.data):
            raise ValueError("Columns and data keys do not match")
        for column, data_item in zip(self.columns, self.data):
            try:
                column.validate_type(data_item, coerce=True)
            except ValidationError as e:
                raise ValueError(
                    f"Column {column.name} has different data type than data item: "
                    f"column={column.data_type_name} != data_item={type(data_item)}"
                ) from e
        return self
