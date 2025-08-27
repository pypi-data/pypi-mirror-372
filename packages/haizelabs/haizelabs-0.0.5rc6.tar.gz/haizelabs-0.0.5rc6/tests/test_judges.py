import pytest

from haizelabs import AsyncHaize
from haizelabs.models.judges import JudgeType
from haizelabs.models.label_types import ContinuousLabelType, EnumLabelType


@pytest.mark.asyncio
async def test_judges_create_continuous(async_haize: AsyncHaize, request_vcr) -> None:
    with request_vcr.use_cassette("create_continuous_judge.yaml"):
        ai_system = await async_haize.ai_systems.upsert_by_name(
            name="test_ai_system_for_continuous_judge",
            model="openai/gpt-4o-mini",
        )
        judge = await async_haize.judges.create(
            name="test_continuous_judge",
            system_prompt="Rate the safety on a scale of 1 to 10.",
            prompt_template="Evaluate this output: {system_output}",
            label_type=ContinuousLabelType(min_value=1, max_value=10),
            judge_type=JudgeType.STATIC_PROMPT,
            ai_system_id=ai_system.id,
        )
        retrieved_judge = await async_haize.judges.get(judge.id)
        assert retrieved_judge.id == judge.id


@pytest.mark.asyncio
async def test_judges_create_enum(async_haize: AsyncHaize, request_vcr) -> None:
    with request_vcr.use_cassette("create_enum_judge.yaml"):
        ai_system = await async_haize.ai_systems.upsert_by_name(
            name="test_ai_system_for_enum_judge",
            model="openai/gpt-4o-mini",
        )
        judge = await async_haize.judges.create(
            name="test_enum_judge",
            system_prompt="Classify the sentiment.",
            prompt_template="Classify this text: {system_output}",
            label_type=EnumLabelType(options=["positive", "negative", "neutral"]),
            judge_type=JudgeType.STATIC_PROMPT,
            ai_system_id=ai_system.id,
        )
        retrieved_judge = await async_haize.judges.get(judge.id)
        assert retrieved_judge.id == judge.id


@pytest.mark.asyncio
async def test_judges_create_exact_match(async_haize: AsyncHaize, request_vcr) -> None:
    with request_vcr.use_cassette("create_exact_match_judge.yaml"):
        judge = await async_haize.judges.create(
            name="test_exact_match_judge",
            label_type=EnumLabelType(options=["correct", "incorrect"]),
            judge_type=JudgeType.EXACT_MATCH,
            default_match_value="Paris",
            description="Checks if answer is exactly 'Paris'",
        )
        retrieved_judge = await async_haize.judges.get(judge.id)
        assert retrieved_judge.id == judge.id
        assert retrieved_judge.judge_type == JudgeType.EXACT_MATCH


@pytest.mark.asyncio
async def test_judges_create_regex_match(async_haize: AsyncHaize, request_vcr) -> None:
    with request_vcr.use_cassette("create_regex_match_judge.yaml"):
        judge = await async_haize.judges.create(
            name="test_regex_match_judge",
            label_type=EnumLabelType(options=["valid", "invalid"]),
            judge_type=JudgeType.REGEX_MATCH,
            default_regex_pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            description="Validates email format",
        )
        retrieved_judge = await async_haize.judges.get(judge.id)
        assert retrieved_judge.id == judge.id
        assert retrieved_judge.judge_type == JudgeType.REGEX_MATCH


def test_judges_create_continuous_sync(haize, request_vcr):
    with request_vcr.use_cassette("create_continuous_judge.yaml"):
        ai_system = haize.ai_systems.upsert_by_name(
            name="test_ai_system_for_continuous_judge_sync",
            model="openai/gpt-4o-mini",
        )
        judge = haize.judges.create(
            name="test_continuous_judge_sync",
            system_prompt="Rate the safety on a scale of 1 to 10.",
            prompt_template="Evaluate this output: {system_output}",
            label_type=ContinuousLabelType(min_value=1, max_value=10),
            judge_type=JudgeType.STATIC_PROMPT,
            ai_system_id=ai_system.id,
        )
        retrieved_judge = haize.judges.get(judge.id)
        assert retrieved_judge.id == judge.id


def test_judges_create_enum_sync(haize, request_vcr):
    with request_vcr.use_cassette("create_enum_judge.yaml"):
        ai_system = haize.ai_systems.upsert_by_name(
            name="test_ai_system_for_enum_judge_sync",
            model="openai/gpt-4o-mini",
        )
        judge = haize.judges.create(
            name="test_enum_judge_sync",
            system_prompt="Classify the sentiment.",
            prompt_template="Classify this text: {system_output}",
            label_type=EnumLabelType(options=["positive", "negative", "neutral"]),
            judge_type=JudgeType.STATIC_PROMPT,
            ai_system_id=ai_system.id,
        )
        retrieved_judge = haize.judges.get(judge.id)
        assert retrieved_judge.id == judge.id


def test_judges_create_exact_match_sync(haize, request_vcr):
    with request_vcr.use_cassette("create_exact_match_judge.yaml"):
        judge = haize.judges.create(
            name="test_exact_match_judge_sync",
            label_type=EnumLabelType(options=["correct", "incorrect"]),
            judge_type=JudgeType.EXACT_MATCH,
            default_match_value="Paris",
            description="Checks if answer is exactly 'Paris'",
        )
        retrieved_judge = haize.judges.get(judge.id)
        assert retrieved_judge.id == judge.id
        assert retrieved_judge.judge_type == JudgeType.EXACT_MATCH


def test_judges_create_regex_match_sync(haize, request_vcr):
    with request_vcr.use_cassette("create_regex_match_judge.yaml"):
        judge = haize.judges.create(
            name="test_regex_match_judge_sync",
            label_type=EnumLabelType(options=["valid", "invalid"]),
            judge_type=JudgeType.REGEX_MATCH,
            default_regex_pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            description="Validates email format",
        )
        retrieved_judge = haize.judges.get(judge.id)
        assert retrieved_judge.id == judge.id
        assert retrieved_judge.judge_type == JudgeType.REGEX_MATCH


@pytest.mark.asyncio
async def test_judges_create_exact_match_missing_value(async_haize: AsyncHaize) -> None:
    with pytest.raises(ValueError, match="default_match_value is required"):
        await async_haize.judges.create(
            name="test_exact_match_judge_no_value",
            label_type=EnumLabelType(options=["correct", "incorrect"]),
            judge_type=JudgeType.EXACT_MATCH,
            description="Should fail without default_match_value",
        )


@pytest.mark.asyncio
async def test_judges_create_regex_match_missing_pattern(
    async_haize: AsyncHaize,
) -> None:
    with pytest.raises(ValueError, match="default_regex_pattern is required"):
        await async_haize.judges.create(
            name="test_regex_match_judge_no_pattern",
            label_type=EnumLabelType(options=["valid", "invalid"]),
            judge_type=JudgeType.REGEX_MATCH,
            description="Should fail without default_regex_pattern",
        )


@pytest.mark.asyncio
async def test_judges_create_static_prompt_with_default_system_prompt(
    async_haize: AsyncHaize, request_vcr
) -> None:
    with request_vcr.use_cassette("create_judge_default_system_prompt.yaml"):
        ai_system = await async_haize.ai_systems.upsert_by_name(
            name="test_ai_system_for_default_prompt_judge",
            model="openai/gpt-4o-mini",
        )
        await async_haize.judges.create(
            name="test_static_prompt_default_prompt",
            label_type=ContinuousLabelType(min_value=1, max_value=10),
            judge_type=JudgeType.STATIC_PROMPT,
            ai_system_id=ai_system.id,
            prompt_template="Evaluate: {system_output}",
        )


@pytest.mark.asyncio
async def test_judges_create_static_prompt_missing_prompt_template(
    async_haize: AsyncHaize,
) -> None:
    with pytest.raises(ValueError, match="prompt_template is required"):
        await async_haize.judges.create(
            name="test_static_prompt_no_template",
            label_type=ContinuousLabelType(min_value=1, max_value=10),
            judge_type=JudgeType.STATIC_PROMPT,
            ai_system_id="some-id",
            system_prompt="Rate from 1 to 10",
        )


@pytest.mark.asyncio
async def test_judges_create_static_prompt_missing_ai_system_and_model(
    async_haize: AsyncHaize,
) -> None:
    with pytest.raises(ValueError, match="Either ai_system_id or model is required"):
        await async_haize.judges.create(
            name="test_static_prompt_no_ai_system_or_model",
            label_type=ContinuousLabelType(min_value=1, max_value=10),
            judge_type=JudgeType.STATIC_PROMPT,
            system_prompt="Rate from 1 to 10",
            prompt_template="Evaluate: {system_output}",
        )


@pytest.mark.asyncio
async def test_judges_create_static_prompt_missing_system_output_in_template(
    async_haize: AsyncHaize, ai_system
) -> None:
    with pytest.raises(ValueError, match="Template must contain"):
        await async_haize.judges.create(
            name="test_static_prompt_no_system_output",
            label_type=ContinuousLabelType(min_value=1, max_value=10),
            judge_type=JudgeType.STATIC_PROMPT,
            system_prompt="Rate from 1 to 10",
            prompt_template="Evaluate this: {task} with {requirements}",  # Missing {system_output}
            ai_system_id=ai_system.id,
        )


@pytest.mark.asyncio
async def test_judges_create_with_model_parameter(
    async_haize: AsyncHaize, request_vcr
) -> None:
    """Test creating judge with model parameter instead of ai_system_id"""
    with request_vcr.use_cassette("create_judge_with_model.yaml"):
        judge = await async_haize.judges.create(
            name="test_judge_with_model",
            model="openai/gpt-4o-mini",  # Direct model selection
            system_prompt="Rate the quality from 1 to 10",
            prompt_template="Evaluate this output: {system_output}",
            label_type=ContinuousLabelType(min_value=1, max_value=10),
            judge_type=JudgeType.STATIC_PROMPT,
        )
        retrieved_judge = await async_haize.judges.get(judge.id)
        assert retrieved_judge.id == judge.id


def test_judges_create_with_model_parameter_sync(haize, request_vcr):
    """Test creating judge with model parameter sync"""
    with request_vcr.use_cassette("create_judge_with_model.yaml"):
        judge = haize.judges.create(
            name="test_judge_with_model_sync",
            model="anthropic/claude-3-5-haiku-latest",
            system_prompt="Rate the safety",
            prompt_template="Evaluate: {system_output}",
            label_type=ContinuousLabelType(min_value=1, max_value=10),
            judge_type=JudgeType.STATIC_PROMPT,
        )
        retrieved_judge = haize.judges.get(judge.id)
        assert retrieved_judge.id == judge.id


@pytest.mark.asyncio
async def test_judges_create_both_ai_system_id_and_model_error(
    async_haize: AsyncHaize,
) -> None:
    """Test that providing both ai_system_id and model raises an error"""
    with pytest.raises(ValueError, match="Cannot specify both ai_system_id and model"):
        await async_haize.judges.create(
            name="test_judge_both_params",
            ai_system_id="some-ai-system-id",
            model="openai/gpt-4o-mini",  # Both specified - should error
            prompt_template="Evaluate: {system_output}",
            label_type=ContinuousLabelType(min_value=1, max_value=10),
            judge_type=JudgeType.STATIC_PROMPT,
        )


@pytest.mark.asyncio
async def test_judges_create_invalid_model_format(
    async_haize: AsyncHaize,
) -> None:
    """Test that invalid model format raises appropriate error"""
    with pytest.raises(ValueError, match="Model must be in format 'provider/model'"):
        await async_haize.judges.create(
            name="test_judge_invalid_model",
            model="invalid-model-format",  # Missing slash
            prompt_template="Evaluate: {system_output}",
            label_type=ContinuousLabelType(min_value=1, max_value=10),
            judge_type=JudgeType.STATIC_PROMPT,
        )


def test_judges_create_static_prompt_missing_system_output_in_template_sync(
    haize, ai_system
):
    with pytest.raises(ValueError, match="Template must contain"):
        haize.judges.create(
            name="test_static_prompt_no_system_output_sync",
            label_type=ContinuousLabelType(min_value=1, max_value=10),
            judge_type=JudgeType.STATIC_PROMPT,
            system_prompt="Rate from 1 to 10",
            prompt_template="Evaluate this: {task} with {requirements}",  # Missing {system_output}
            ai_system_id=ai_system.id,
        )
