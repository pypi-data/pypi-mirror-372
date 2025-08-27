import pytest

from haizelabs import AsyncHaize


@pytest.mark.asyncio
async def test_unit_tests_create(
    async_haize: AsyncHaize, ai_system, judge, dataset, request_vcr
) -> None:
    """Test creating unit test"""
    with request_vcr.use_cassette("create_unit_test.yaml"):
        created_test = await async_haize.unit_tests.create(
            name="test_unit_test",
            system_id=ai_system.id,
            judge_ids=[judge.id],
            prompt_template="Test: {input_text}",
            dataset_id=dataset.dataset_id,
            dataset_version=1,
        )
        assert created_test.test_id is not None


@pytest.mark.asyncio
async def test_unit_tests_get(
    async_haize: AsyncHaize, ai_system, judge, dataset, request_vcr
) -> None:
    """Test getting unit test by ID"""
    with request_vcr.use_cassette("get_unit_test.yaml"):
        created_test = await async_haize.unit_tests.create(
            name="test_unit_test_get",
            system_id=ai_system.id,
            judge_ids=[judge.id],
            prompt_template="Test: {input_text}",
            dataset_id=dataset.dataset_id,
            dataset_version=1,
        )

        retrieved_test = await async_haize.unit_tests.get(created_test.test_id)
        assert retrieved_test.id == created_test.test_id
        assert retrieved_test.system_id == ai_system.id
        assert [judge.id] == [judge_id.id for judge_id in retrieved_test.judge_ids]
        assert retrieved_test.prompt_template.template == "Test: {input_text}"
        assert retrieved_test.dataset_id == dataset.dataset_id
        assert retrieved_test.dataset_version == 1


def test_unit_tests_create_sync(haize, ai_system, judge, dataset, request_vcr):
    """Sync: Test creating unit test"""
    with request_vcr.use_cassette("create_unit_test.yaml"):
        created_test = haize.unit_tests.create(
            name="test_unit_test",
            system_id=ai_system.id,
            judge_ids=[judge.id],
            prompt_template="Test: {input_text}",
            dataset_id=dataset.dataset_id,
            dataset_version=1,
        )
        retrieved_test = haize.unit_tests.get(created_test.test_id)
        assert retrieved_test.id == created_test.test_id
        assert retrieved_test.system_id == ai_system.id
        assert [judge.id] == [judge_id.id for judge_id in retrieved_test.judge_ids]
        assert retrieved_test.prompt_template.template == "Test: {input_text}"
        assert retrieved_test.dataset_id == dataset.dataset_id
        assert retrieved_test.dataset_version == 1


@pytest.mark.asyncio
async def test_unit_tests_start(
    async_haize: AsyncHaize, ai_system, judge, dataset, request_vcr, mock_logger
):
    """Async: Test starting unit test"""
    with request_vcr.use_cassette("created_and_started_unit_test.yaml"):
        created_test = await async_haize.unit_tests.create(
            name="test_unit_test",
            system_id=ai_system.id,
            judge_ids=[judge.id],
            prompt_template="Test: {input_text}",
            dataset_id=dataset.dataset_id,
            dataset_version=1,
        )
        await async_haize.unit_tests.start(created_test.test_id)

        mock_logger.info.assert_called_with(
            f"Started test {created_test.test_id}, view at https://platform.haizelabs.com/app/unit-tests/{created_test.test_id}"
        )


@pytest.mark.asyncio
async def test_unit_tests_cancel(
    async_haize: AsyncHaize, ai_system, judge, dataset, request_vcr
):
    """Async: Test canceling unit test"""
    with request_vcr.use_cassette("cancel_unit_test.yaml"):
        created_test = await async_haize.unit_tests.create(
            name="test_unit_test",
            system_id=ai_system.id,
            judge_ids=[judge.id],
            prompt_template="Test: {input_text}",
            dataset_id=dataset.dataset_id,
            dataset_version=1,
        )
        await async_haize.unit_tests.cancel(created_test.test_id)


def test_unit_tests_start_sync(haize, ai_system, judge, dataset, request_vcr):
    """Sync: Test starting unit test"""
    with request_vcr.use_cassette("created_and_started_unit_test.yaml"):
        created_test = haize.unit_tests.create(
            name="test_unit_test",
            system_id=ai_system.id,
            judge_ids=[judge.id],
            prompt_template="Test: {input_text}",
            dataset_id=dataset.dataset_id,
            dataset_version=1,
        )
        haize.unit_tests.start(created_test.test_id)


def test_unit_tests_cancel_sync(haize, ai_system, judge, dataset, request_vcr):
    """Sync: Test canceling unit test"""
    with request_vcr.use_cassette("cancel_unit_test.yaml"):
        created_test = haize.unit_tests.create(
            name="test_unit_test",
            system_id=ai_system.id,
            judge_ids=[judge.id],
            prompt_template="Test: {input_text}",
            dataset_id=dataset.dataset_id,
            dataset_version=1,
        )
        haize.unit_tests.cancel(created_test.test_id)
