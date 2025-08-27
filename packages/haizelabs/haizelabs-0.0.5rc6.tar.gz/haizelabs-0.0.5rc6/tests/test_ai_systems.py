import pytest

from haizelabs import AsyncHaize, Haize
from haizelabs.models.ai_system import (
    AISystemConfig,
    FireworksConfig,
    ThirdPartyProvider,
    TogetherConfig,
)


@pytest.mark.asyncio
async def test_ai_systems_upsert_by_name(async_haize: AsyncHaize, request_vcr) -> None:
    """Test creating/getting AI system by name"""
    with request_vcr.use_cassette("upsert_ai_system.yaml"):
        ai_system = await async_haize.ai_systems.upsert_by_name(
            name="corporate_assistant_v1",
            model="openai/gpt-4o-mini",
        )
        assert ai_system.id is not None
        assert ai_system.name == "corporate_assistant_v1"
        assert ai_system.model_id == "openai/gpt-4o-mini"
        assert ai_system.provider == ThirdPartyProvider.OPENAI

        ai_system2 = await async_haize.ai_systems.upsert_by_name(
            name="corporate_assistant_v1",
            model="openai/gpt-4o-mini",
        )
        assert ai_system2.id == ai_system.id


@pytest.mark.asyncio
async def test_ai_systems_get(async_haize: AsyncHaize, request_vcr, ai_system) -> None:
    """Test getting AI system by ID"""
    with request_vcr.use_cassette("get_ai_system.yaml"):
        retrieved_system = await async_haize.ai_systems.get(ai_system.id)
        assert retrieved_system.id == ai_system.id
        assert retrieved_system.name == ai_system.name
        assert retrieved_system.model_id == ai_system.model_id


@pytest.mark.asyncio
async def test_ai_systems_update(async_haize: AsyncHaize, request_vcr) -> None:
    """Test updating AI system"""
    with request_vcr.use_cassette("update_ai_system.yaml"):
        ai_system = await async_haize.ai_systems.upsert_by_name(
            name="system_to_be_updated",
            model="openai/gpt-4o-mini",
        )
        updated_name = "updated"
        updated_system = await async_haize.ai_systems.update(
            ai_system_id=ai_system.id,
            name=updated_name,
            model="openai/gpt-4o-mini",
        )
        returned_updated_system = await async_haize.ai_systems.get(updated_system.id)
        assert returned_updated_system.id == ai_system.id == updated_system.id
        assert returned_updated_system.name == updated_name == updated_system.name


@pytest.mark.asyncio
async def test_self_hosted_ai_systems_upsert(
    async_haize: AsyncHaize, request_vcr
) -> None:
    """Test self-hosted AI systems with various providers"""
    with request_vcr.use_cassette("upsert_self_hosted_ai_systems.yaml"):
        together_config = TogetherConfig(model_id="meta-llama/Llama-2-7b-chat-hf")
        together_system = await async_haize.ai_systems.upsert_by_name(
            name="test_together_system",
            self_hosted_config=together_config,
            api_key="test_together_api_key",
            system_config={"temperature": 0.7, "max_tokens": 1000},
            system_prompt="You are a helpful assistant.",
        )
        assert together_system.id is not None

        fireworks_config = FireworksConfig(model_id="llama-v2-7b-chat")
        fireworks_system = await async_haize.ai_systems.upsert_by_name(
            name="test_fireworks_system",
            self_hosted_config=fireworks_config,
            api_key="test_fireworks_api_key",
            system_config={"temperature": 0.7, "max_tokens": 1000},
            system_prompt="You are a helpful assistant.",
        )
        assert fireworks_system.id is not None


def test_ai_systems_upsert_by_name_sync(haize: Haize, request_vcr):
    """Sync: Test creating/getting AI system by name"""
    with request_vcr.use_cassette("upsert_ai_system.yaml"):
        ai_system = haize.ai_systems.upsert_by_name(
            name="corporate_assistant_v1",
            model="openai/gpt-4o-mini",
        )
        assert ai_system.id is not None
        assert ai_system.name == "corporate_assistant_v1"
        assert ai_system.model_id == "openai/gpt-4o-mini"
        assert ai_system.provider == ThirdPartyProvider.OPENAI

        ai_system2 = haize.ai_systems.upsert_by_name(
            name="corporate_assistant_v1",
            model="openai/gpt-4o-mini",
        )
        assert ai_system2.id == ai_system.id


def test_ai_systems_get_sync(haize: Haize, request_vcr, ai_system):
    """Sync: Test getting AI system by ID"""
    with request_vcr.use_cassette("get_ai_system.yaml"):
        retrieved_system = haize.ai_systems.get(ai_system.id)
        assert retrieved_system.id == ai_system.id
        assert retrieved_system.name == ai_system.name
        assert retrieved_system.model_id == ai_system.model_id


def test_ai_systems_update_sync(haize: Haize, request_vcr):
    """Sync: Test updating AI system"""
    with request_vcr.use_cassette("update_ai_system.yaml"):
        ai_system = haize.ai_systems.upsert_by_name(
            name="system_to_be_updated",
            model="openai/gpt-4o-mini",
        )
        updated_name = "updated"
        updated_system = haize.ai_systems.update(
            ai_system_id=ai_system.id,
            name=updated_name,
            model="openai/gpt-4o-mini",
        )
        returned_updated_system = haize.ai_systems.get(updated_system.id)
        assert returned_updated_system.id == ai_system.id == updated_system.id
        assert returned_updated_system.name == updated_name == updated_system.name


def test_self_hosted_ai_systems_sync(haize: Haize, request_vcr):
    """Sync: Test self-hosted AI systems with various providers"""
    with request_vcr.use_cassette("upsert_self_hosted_ai_systems.yaml"):
        together_config = TogetherConfig(model_id="meta-llama/Llama-2-7b-chat-hf")
        together_system = haize.ai_systems.upsert_by_name(
            name="test_together_system",
            self_hosted_config=together_config,
            api_key="test_together_api_key",
            system_config={"temperature": 0.7, "max_tokens": 1000},
            system_prompt="You are a helpful assistant.",
        )
        assert together_system.id is not None

        fireworks_config = FireworksConfig(model_id="llama-v2-7b-chat")
        fireworks_system = haize.ai_systems.upsert_by_name(
            name="test_fireworks_system",
            self_hosted_config=fireworks_config,
            api_key="test_fireworks_api_key",
            system_config={"temperature": 0.7, "max_tokens": 1000},
            system_prompt="You are a helpful assistant.",
        )
        assert fireworks_system.id is not None


@pytest.mark.asyncio
async def test_ai_systems_create(async_haize: AsyncHaize, request_vcr) -> None:
    """Test creating AI system directly"""
    with request_vcr.use_cassette("create_ai_system.yaml"):
        ai_system_id = await async_haize.ai_systems.create(
            name="created_ai_system",
            model="openai/gpt-4o-mini",
            system_prompt="You are a helpful assistant.",
            system_config={"temperature": 0.7},
        )
        ai_system = await async_haize.ai_systems.get(ai_system_id)
        assert ai_system.id == ai_system_id
        assert ai_system.name == "created_ai_system"
        assert ai_system.model_id == "openai/gpt-4o-mini"
        assert ai_system.provider == ThirdPartyProvider.OPENAI
        assert ai_system.system_prompt == "You are a helpful assistant."
        assert ai_system.system_config == AISystemConfig(temperature=0.7)


@pytest.mark.asyncio
async def test_ai_systems_create_self_hosted(
    async_haize: AsyncHaize, request_vcr
) -> None:
    """Test creating self-hosted AI system directly"""
    with request_vcr.use_cassette("create_self_hosted_ai_systems.yaml"):
        together_config = TogetherConfig(model_id="meta-llama/Llama-2-7b-chat-hf")
        ai_system_id = await async_haize.ai_systems.create(
            name="self-hosted-ai-system",
            self_hosted_config=together_config,
            api_key="test_api_key",
            system_prompt="You are a helpful assistant.",
            system_config={"temperature": 0.5, "max_tokens": 500},
        )
        ai_system = await async_haize.ai_systems.get(ai_system_id)
        assert ai_system.id == ai_system_id
        assert ai_system.name == "self-hosted-ai-system"
        assert ai_system.system_prompt == "You are a helpful assistant."
        assert ai_system.system_config == AISystemConfig(
            temperature=0.5, max_tokens=500
        )
        assert ai_system.self_hosted_config == together_config


def test_ai_systems_create_sync(haize: Haize, request_vcr):
    """Sync: Test creating AI system directly"""
    with request_vcr.use_cassette("create_ai_system.yaml"):
        ai_system_id = haize.ai_systems.create(
            name="created_ai_system",
            model="openai/gpt-4o-mini",
            system_prompt="You are a helpful assistant.",
            system_config={"temperature": 0.7},
        )
        ai_system = haize.ai_systems.get(ai_system_id)
        assert ai_system.id == ai_system_id
        assert ai_system.name == "created_ai_system"
        assert ai_system.model_id == "openai/gpt-4o-mini"
        assert ai_system.provider == ThirdPartyProvider.OPENAI
        assert ai_system.system_prompt == "You are a helpful assistant."
        assert ai_system.system_config == AISystemConfig(temperature=0.7)


def test_ai_systems_create_self_hosted_sync(haize: Haize, request_vcr):
    """Sync: Test creating self-hosted AI system directly"""
    with request_vcr.use_cassette("create_self_hosted_ai_systems.yaml"):
        together_config = TogetherConfig(model_id="meta-llama/Llama-2-7b-chat-hf")
        ai_system_id = haize.ai_systems.create(
            name="self-hosted-ai-system",
            self_hosted_config=together_config,
            api_key="test_api_key",
            system_prompt="You are a helpful assistant.",
            system_config={"temperature": 0.5, "max_tokens": 500},
        )
        ai_system = haize.ai_systems.get(ai_system_id)
        assert ai_system.id == ai_system_id
        assert ai_system.name == "self-hosted-ai-system"
        assert ai_system.system_prompt == "You are a helpful assistant."
        assert ai_system.system_config == AISystemConfig(
            temperature=0.5, max_tokens=500
        )
        assert ai_system.self_hosted_config == together_config


@pytest.mark.asyncio
async def test_ai_systems_get_supported_models(
    async_haize: AsyncHaize, request_vcr
) -> None:
    """Test getting supported models"""
    with request_vcr.use_cassette("get_third_party_models.yaml"):
        models = await async_haize.ai_systems.get_supported_models()
        assert isinstance(models, list)
        assert len(models) > 0, "Should have at least one model"

        for model in models:
            assert isinstance(model, str), f"Model {model} should be a string"
            assert "/" in model, f"Model {model} should be in provider/model format"
            provider_part = model.split("/")[0]
            assert provider_part.lower() in [
                "openai",
                "anthropic",
                "cohere",
                "gemini",
                "xai",
            ], f"Provider {provider_part} should be supported"


def test_ai_systems_get_supported_models_sync(haize: Haize, request_vcr) -> None:
    """Test getting supported models synchronously"""
    with request_vcr.use_cassette("get_third_party_models.yaml"):
        models = haize.ai_systems.get_supported_models()
        print(models)
        assert isinstance(models, list)
        assert len(models) > 0, "Should have at least one model"

        for model in models:
            assert isinstance(model, str), f"Model {model} should be a string"
            assert "/" in model, f"Model {model} should be in provider/model format"
            provider_part = model.split("/")[0]
            assert provider_part.lower() in [
                "openai",
                "anthropic",
                "cohere",
                "gemini",
                "xai",
            ], f"Provider {provider_part} should be supported"
