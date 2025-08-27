from __future__ import annotations

from typing import Any

from pydantic import AwareDatetime, BaseModel

from haizelabs.models.data_columns import ColumnType, DataColumn, DataColumns
from haizelabs.models.data_types import DataPyType, DataTypeName


class DataColumnParams(BaseModel):
    name: str
    data_type_name: DataTypeName
    formatted_name: str | None = None
    column_type: ColumnType


class DatasetRowParams(BaseModel):
    values: list[Any]


class UpsertDatasetRequest(BaseModel):
    name: str
    description: str | None = None
    columns: list[DataColumnParams]
    rows: list[DatasetRowParams]


class UpsertDatasetResponse(BaseModel):
    dataset_id: str
    dataset_version: int


class DatasetInfoResponse(BaseModel):
    id: str
    version: int
    creator_id: int
    updater_id: int
    created_at: AwareDatetime
    updated_at: AwareDatetime
    name: str
    description: str | None = None
    columns: list[DataColumn]


class DatasetRowResponse(BaseModel):
    columns: DataColumns
    data: tuple[DataPyType, ...]
    id: str
    dataset_id: str
    dataset_version: int
    is_synthetic: bool | None = None


class GetDatasetAndRowsResponse(BaseModel):
    dataset_info: DatasetInfoResponse
    dataset_rows: list[DatasetRowResponse]


class BaseDataRow(BaseModel):
    columns: DataColumns
    data: tuple[DataPyType, ...]


class BaseDatasetRow(BaseDataRow):
    id: str
    dataset_id: str
    dataset_version: int
    is_synthetic: bool | None = None


class BaseDataRow(BaseModel):
    columns: DataColumns
    data: tuple[DataPyType, ...]


class AddDatasetRowsRequest(BaseModel):
    rows: list[BaseDataRow]
    is_synthetic: bool = False


class AddDatasetRowsResponse(BaseModel):
    row_ids: list[str]
