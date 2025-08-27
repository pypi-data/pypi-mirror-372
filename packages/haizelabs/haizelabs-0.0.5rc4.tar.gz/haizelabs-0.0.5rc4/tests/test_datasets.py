import pytest

from haizelabs import AsyncHaize


@pytest.mark.asyncio
async def test_datasets_create(async_haize: AsyncHaize, request_vcr) -> None:
    with request_vcr.use_cassette("create_dataset.yaml"):
        dataset = await async_haize.datasets.create(
            name="test_dataset",
            data=[
                {"input_text": "Hello world", "expected_output": "Greeting response"},
                {"input_text": "How are you?", "expected_output": "Status response"},
            ],
        )
        assert dataset.dataset_id is not None


@pytest.mark.asyncio
async def test_datasets_update(async_haize: AsyncHaize, request_vcr) -> None:
    with request_vcr.use_cassette("update_dataset.yaml"):
        created_dataset = await async_haize.datasets.create(
            name="test_dataset_update", data=[{"input_text": "Original input"}]
        )

        updated_dataset = await async_haize.datasets.update(
            dataset_id=created_dataset.dataset_id,
            name="test_dataset_updated",
            data=[{"input_text": "Updated input", "context": "New field"}],
        )
        assert updated_dataset.dataset_id == created_dataset.dataset_id
        assert updated_dataset.dataset_version > created_dataset.dataset_version


@pytest.mark.asyncio
async def test_datasets_add_rows(async_haize: AsyncHaize, request_vcr) -> None:
    with request_vcr.use_cassette("add_rows_dataset.yaml"):
        created_dataset = await async_haize.datasets.create(
            name="test_dataset_add_rows",
            data=[
                {"question": "What is AI?", "answer": "Artificial Intelligence"},
                {"question": "What is ML?", "answer": "Machine Learning"},
            ],
        )

        result = await async_haize.datasets.add_rows(
            dataset_id=created_dataset.dataset_id,
            dataset_version=created_dataset.dataset_version,
            data=[
                {"question": "What is DL?", "answer": "Deep Learning"},
                {"question": "What is NLP?", "answer": "Natural Language Processing"},
            ],
        )
        assert len(result.row_ids) == 2
        assert all(row_id for row_id in result.row_ids)


def test_datasets_create_sync(haize, request_vcr):
    with request_vcr.use_cassette("create_dataset.yaml"):
        dataset = haize.datasets.create(
            name="test_dataset_sync",
            data=[
                {"input_text": "Hello world", "expected_output": "Greeting response"},
                {"input_text": "How are you?", "expected_output": "Status response"},
            ],
        )
        assert dataset.dataset_id is not None


def test_datasets_update_sync(haize, request_vcr):
    with request_vcr.use_cassette("update_dataset.yaml"):
        created_dataset = haize.datasets.create(
            name="test_dataset_update_sync", data=[{"input_text": "Original input"}]
        )

        updated_dataset = haize.datasets.update(
            dataset_id=created_dataset.dataset_id,
            name="test_dataset_updated_sync",
            data=[{"input_text": "Updated input", "context": "New field"}],
        )
        assert updated_dataset.dataset_id == created_dataset.dataset_id
        assert updated_dataset.dataset_version > created_dataset.dataset_version


def test_datasets_add_rows_sync(haize, request_vcr):
    with request_vcr.use_cassette("add_rows_dataset.yaml"):
        created_dataset = haize.datasets.create(
            name="test_dataset_add_rows_sync",
            data=[
                {"question": "What is AI?", "answer": "Artificial Intelligence"},
                {"question": "What is ML?", "answer": "Machine Learning"},
            ],
        )

        result = haize.datasets.add_rows(
            dataset_id=created_dataset.dataset_id,
            dataset_version=created_dataset.dataset_version,
            data=[
                {"question": "What is DL?", "answer": "Deep Learning"},
                {"question": "What is NLP?", "answer": "Natural Language Processing"},
            ],
        )
        assert len(result.row_ids) == 2
        assert all(row_id for row_id in result.row_ids)


@pytest.mark.asyncio
async def test_datasets_get_by_version_and_latest(
    async_haize: AsyncHaize, request_vcr
) -> None:
    with request_vcr.use_cassette("get_dataset_by_version_and_latest.yaml"):
        created_dataset = await async_haize.datasets.create(
            name="test_dataset_versioned",
            data=[{"input": "v1 data", "output": "v1 response"}],
        )
        version1 = created_dataset.dataset_version

        updated_dataset = await async_haize.datasets.update(
            dataset_id=created_dataset.dataset_id,
            name="test_dataset_versioned_v2",
            data=[{"input": "v2 data", "output": "v2 response"}],
        )
        version2 = updated_dataset.dataset_version

        dataset_v1 = await async_haize.datasets.get(
            created_dataset.dataset_id, version=version1
        )
        assert dataset_v1.dataset_info.version == version1
        assert dataset_v1.dataset_info.name == "test_dataset_versioned"

        dataset_v2 = await async_haize.datasets.get(
            created_dataset.dataset_id, version=version2
        )
        assert dataset_v2.dataset_info.version == version2
        assert dataset_v2.dataset_info.name == "test_dataset_versioned_v2"

        dataset_latest = await async_haize.datasets.get(created_dataset.dataset_id)
        assert dataset_latest.dataset_info.version == version2


def test_datasets_get_by_version_and_latest_sync(haize, request_vcr):
    with request_vcr.use_cassette("get_dataset_by_version_and_latest.yaml"):
        created_dataset = haize.datasets.create(
            name="test_dataset_versioned",
            data=[{"input": "v1 data", "output": "v1 response"}],
        )
        version1 = created_dataset.dataset_version

        updated_dataset = haize.datasets.update(
            dataset_id=created_dataset.dataset_id,
            name="test_dataset_versioned_v2",
            data=[{"input": "v2 data", "output": "v2 response"}],
        )
        version2 = updated_dataset.dataset_version

        dataset_v1 = haize.datasets.get(created_dataset.dataset_id, version=version1)
        assert dataset_v1.dataset_info.version == version1
        assert dataset_v1.dataset_info.name == "test_dataset_versioned"

        dataset_v2 = haize.datasets.get(created_dataset.dataset_id, version=version2)
        assert dataset_v2.dataset_info.version == version2
        assert dataset_v2.dataset_info.name == "test_dataset_versioned_v2"

        dataset_latest = haize.datasets.get(created_dataset.dataset_id)
        assert dataset_latest.dataset_info.version == version2
