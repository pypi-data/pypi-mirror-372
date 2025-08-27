from __future__ import annotations

import logging
from typing import List, Optional

from haizelabs._resource import AsyncAPIResource, SyncAPIResource
from haizelabs.models.data_columns import ColumnType
from haizelabs.models.data_types import DataTypeName
from haizelabs.models.datasets import (
    AddDatasetRowsRequest,
    AddDatasetRowsResponse,
    BaseDataRow,
    DataColumn,
    DataColumnParams,
    DataColumns,
    DatasetRowParams,
    GetDatasetAndRowsResponse,
    UpsertDatasetRequest,
    UpsertDatasetResponse,
)

logger = logging.getLogger(__name__)


def get_and_validate_column_names_from_rows(data: List[dict]) -> List[str]:
    column_names = list(data[0].keys())
    for i, row in enumerate(data):
        if set(row.keys()) != set(column_names):
            raise ValueError(f"Row {i} has different columns than first row")
    return column_names


def create_add_dataset_rows_request(
    existing_columns: List[DataColumn], data: List[dict]
) -> AddDatasetRowsRequest:
    columns = DataColumns(columns=tuple(existing_columns))
    rows = [
        BaseDataRow(
            columns=columns,
            data=tuple(
                str(row.get(col_name, ""))
                for col_name in [col.name for col in existing_columns]
            ),
        )
        for row in data
    ]
    return AddDatasetRowsRequest(rows=rows, is_synthetic=False)


class SyncDatasets(SyncAPIResource):
    prefix: str = "/datasets"

    def create(
        self,
        name: str,
        data: List[dict],
        description: Optional[str] = None,
    ) -> UpsertDatasetResponse:
        """Create a new dataset.

        Args:
            name: Dataset name
            data: List of dictionaries where keys are column names and values are data
            description: Optional description

        Returns:
            Information about the created dataset
        """
        if not data:
            raise ValueError("Data cannot be empty")

        column_names = get_and_validate_column_names_from_rows(data)

        columns = [
            DataColumnParams(
                name=col_name,
                data_type_name=DataTypeName.STR,
                column_type=ColumnType.OTHER,
            )
            for col_name in column_names
        ]
        rows = [
            DatasetRowParams(values=[str(row[col]) for col in column_names])
            for row in data
        ]
        request = UpsertDatasetRequest(
            name=name,
            columns=columns,
            rows=rows,
            description=description,
        )
        response = self._client.post(
            f"{self.prefix}/create", json=request.model_dump(exclude_none=True)
        )
        return UpsertDatasetResponse.model_validate(response)

    def get(
        self, dataset_id: str, version: Optional[int] = None
    ) -> GetDatasetAndRowsResponse:
        """Get a dataset by ID, optionally specifying version.

        Args:
            dataset_id: ID of the dataset
            version: Optional specific version to retrieve (latest if None)

        Returns:
            Information about the dataset and its rows
        """
        if version is None:
            response = self._client.get(f"{self.prefix}/{dataset_id}/latest")
        else:
            response = self._client.get(f"{self.prefix}/{dataset_id}/{version}")
        return GetDatasetAndRowsResponse.model_validate(response)

    def update(
        self,
        dataset_id: str,
        name: str,
        data: List[dict],
        description: Optional[str] = None,
    ) -> UpsertDatasetResponse:
        """Update an existing dataset (creates new version).

        Args:
            dataset_id: ID of the dataset to update
            name: Dataset name
            data: List of dictionaries where keys are column names and values are data
            description: Optional description

        Returns:
            Information about the updated dataset
        """
        if not data:
            raise ValueError("Data cannot be empty")

        column_names = get_and_validate_column_names_from_rows(data)

        columns = [
            DataColumnParams(
                name=col_name,
                data_type_name=DataTypeName.STR,
                column_type=ColumnType.OTHER,
            )
            for col_name in column_names
        ]
        rows = [
            DatasetRowParams(values=[str(row[col]) for col in column_names])
            for row in data
        ]

        request = UpsertDatasetRequest(
            name=name,
            columns=columns,
            rows=rows,
            description=description,
        )
        response = self._client.post(
            f"{self.prefix}/{dataset_id}/update",
            json=request.model_dump(exclude_none=True),
        )
        return UpsertDatasetResponse.model_validate(response)

    def add_rows(
        self,
        dataset_id: str,
        dataset_version: int,
        data: List[dict],
    ) -> AddDatasetRowsResponse:
        """Add rows to a specific version of a dataset.

        Args:
            dataset_id: ID of the dataset to add rows to
            dataset_version: Version of the dataset to add rows to
            data: List of dictionaries where keys are column names and values are data

        Returns:
            List of row IDs
        """
        if not data:
            raise ValueError("Data cannot be empty")

        existing_columns = (self.get(dataset_id, dataset_version)).dataset_info.columns

        response = self._client.post(
            f"{self.prefix}/{dataset_id}/{dataset_version}/add_rows",
            json=create_add_dataset_rows_request(existing_columns, data).model_dump(
                mode="json"
            ),
        )
        return AddDatasetRowsResponse.model_validate(response)


class AsyncDatasets(AsyncAPIResource):
    prefix: str = "/datasets"

    async def create(
        self,
        name: str,
        data: List[dict],
        description: Optional[str] = None,
    ) -> UpsertDatasetResponse:
        """Create a new dataset.

        Args:
            name: Dataset name
            data: List of dictionaries where keys are column names and values are data
            description: Optional description

        Returns:
            Information about the created dataset
        """
        if not data:
            raise ValueError("Data cannot be empty")

        column_names = get_and_validate_column_names_from_rows(data)
        columns = [
            DataColumnParams(
                name=col_name,
                data_type_name=DataTypeName.STR,
                column_type=ColumnType.OTHER,
            )
            for col_name in column_names
        ]

        rows = [
            DatasetRowParams(values=[str(row[col]) for col in column_names])
            for row in data
        ]

        request = UpsertDatasetRequest(
            name=name,
            columns=columns,
            rows=rows,
            description=description,
        )
        response = await self._client.post(
            f"{self.prefix}/create", json=request.model_dump(exclude_none=True)
        )
        return UpsertDatasetResponse.model_validate(response)

    async def get(
        self, dataset_id: str, version: Optional[int] = None
    ) -> GetDatasetAndRowsResponse:
        """Get a dataset by ID, optionally specifying version.

        Args:
            dataset_id: ID of the dataset
            version: Optional specific version to retrieve (defaults to latest)

        Returns:
            GetDatasetAndRowsResponse with dataset info and rows
        """
        if version is None:
            response = await self._client.get(f"{self.prefix}/{dataset_id}/latest")
        else:
            response = await self._client.get(f"{self.prefix}/{dataset_id}/{version}")
        return GetDatasetAndRowsResponse.model_validate(response)

    async def update(
        self,
        dataset_id: str,
        name: str,
        data: List[dict],
        description: Optional[str] = None,
    ) -> UpsertDatasetResponse:
        """Update an existing dataset (creates new version).

        Args:
            dataset_id: ID of the dataset to update
            name: Dataset name
            data: List of dictionaries where keys are column names and values are data
            description: Optional description

        Returns:
            Information about the updated dataset
        """
        if not data:
            raise ValueError("Data cannot be empty")

        column_names = get_and_validate_column_names_from_rows(data)

        columns = [
            DataColumnParams(
                name=col_name,
                data_type_name=DataTypeName.STR,
                column_type=ColumnType.OTHER,
            )
            for col_name in column_names
        ]

        rows = [
            DatasetRowParams(values=[str(row[col]) for col in column_names])
            for row in data
        ]

        request = UpsertDatasetRequest(
            name=name,
            columns=columns,
            rows=rows,
            description=description,
        )
        response = await self._client.post(
            f"{self.prefix}/{dataset_id}/update",
            json=request.model_dump(exclude_none=True),
        )
        return UpsertDatasetResponse.model_validate(response)

    async def add_rows(
        self,
        dataset_id: str,
        dataset_version: int,
        data: List[dict],
    ) -> AddDatasetRowsResponse:
        """Add rows to a specific version of a dataset.

        Args:
            dataset_id: ID of the dataset to add rows to
            dataset_version: Version of the dataset to add rows to
            data: List of dictionaries where keys are column names and values are data

        Returns:
            List of row IDs
        """
        if not data:
            raise ValueError("Data cannot be empty")

        existing_columns = (
            await self.get(dataset_id, dataset_version)
        ).dataset_info.columns

        response = await self._client.post(
            f"{self.prefix}/{dataset_id}/{dataset_version}/add_rows",
            json=create_add_dataset_rows_request(existing_columns, data).model_dump(
                mode="json"
            ),
        )
        return AddDatasetRowsResponse.model_validate(response)
