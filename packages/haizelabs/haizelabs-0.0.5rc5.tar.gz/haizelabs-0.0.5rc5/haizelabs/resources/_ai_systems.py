from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, List, Union

from pydantic import TypeAdapter

from haizelabs._resource import AsyncAPIResource, SyncAPIResource
from haizelabs.models import ChatCompletionMessage
from haizelabs.models.ai_system import (
    AISystem,
    AISystemType,
    CreateAISystemResponse,
    CreateSelfHostedAISystemRequest,
    CreateThirdPartyAISystemRequest,
    GetAISystemResponse,
    GetThirdPartyModelsResponse,
    LLMProviderSecrets,
    SelfHostedConfig,
    ThirdPartyProvider,
    UpdateAISystemResponse,
    UpdateSelfHostedAISystemRequest,
    UpdateThirdPartyAISystemRequest,
)


def _parse_model(model: str) -> tuple[ThirdPartyProvider, str]:
    """Parse model format 'provider/model' into provider and model_id.

    Args:
        model: Model string in format 'provider/model'

    Returns:
        Tuple of (provider_enum, model_id)

    Raises:
        ValueError: If model format is invalid or provider is unsupported
    """
    if "/" not in model:
        raise ValueError(f"Model must be in format 'provider/model', got: {model}")

    provider_str, model_id = model.split("/", 1)
    provider_str = provider_str.lower()

    if not provider_str or not model_id:
        raise ValueError(
            f"Both provider and model must be non-empty in format 'provider/model', got: {model}"
        )

    provider_map = {
        "openai": ThirdPartyProvider.OPENAI,
        "anthropic": ThirdPartyProvider.ANTHROPIC,
        "cohere": ThirdPartyProvider.COHERE,
        "gemini": ThirdPartyProvider.GEMINI,
        "mistral": ThirdPartyProvider.MISTRAL,
        "xai": ThirdPartyProvider.XAI,
    }

    if provider_str not in provider_map:
        supported_providers = ", ".join(provider_map.keys())
        raise ValueError(
            f"Unsupported provider '{provider_str}'. Supported providers: {supported_providers}"
        )

    return (
        provider_map[provider_str],
        provider_map[provider_str].value.lower() + "/" + model_id,
    )


AISystemFunction = Callable[[List[ChatCompletionMessage]], Union[str, Awaitable[str]]]


class SyncAISystems(SyncAPIResource):
    prefix: str = "/ai_systems"

    def create(
        self,
        name: str,
        model: str | None = None,
        api_key: str | None = None,
        self_hosted_config: SelfHostedConfig | None = None,
        system_config: Dict[str, Any] | None = None,
        system_prompt: str | None = None,
    ) -> str:
        """Create a new AI system.

        Args:
            name: Name of the AI system
            model: Model in format 'provider/model' (e.g. 'openai/gpt-4o-mini')
            api_key: API key for third-party systems
            self_hosted_config: Self-hosted configuration
            system_config: System configuration
            system_prompt: System prompt

        Returns:
            The ID of the created AI system
        """
        if model and self_hosted_config:
            raise ValueError("Cannot specify both 'model' and 'self_hosted_config'")

        if not model and not self_hosted_config:
            raise ValueError(
                "Either 'model' (for third-party systems) or 'self_hosted_config' "
                "(for self-hosted systems) must be specified"
            )

        if api_key:
            provider_secrets = LLMProviderSecrets(api_key=api_key)
        else:
            provider_secrets = None

        if self_hosted_config:
            request = CreateSelfHostedAISystemRequest(
                self_hosted_config=self_hosted_config,
                provider_secrets=provider_secrets,
                ai_system_type=AISystemType.SELF_HOSTED,
                name=name,
                system_config=system_config,
                system_prompt=system_prompt,
            )
        else:
            provider, model_id = _parse_model(model)
            request = CreateThirdPartyAISystemRequest(
                ai_system_type=AISystemType.THIRD_PARTY,
                name=name,
                provider=provider,
                model_id=model_id,
                provider_secrets=provider_secrets,
                system_config=system_config,
                system_prompt=system_prompt,
            )

        response = self._client.post(f"{self.prefix}", json=request.model_dump())
        create_response = CreateAISystemResponse.model_validate(response)
        return create_response.id

    def get(self, ai_system_id: str) -> AISystem:
        """Get an AI system by ID.

        Args:
            ai_system_id: ID of the AI system

        Returns:
            Details of the AI system
        """
        response = self._client.get(f"{self.prefix}/{ai_system_id}")
        response_model = GetAISystemResponse.model_validate(response)
        ai_system_dict = response_model.ai_system.model_dump(exclude_none=True)
        return TypeAdapter(AISystem).validate_python(ai_system_dict)

    def update(
        self,
        ai_system_id: str,
        name: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
    ) -> AISystem:
        """Update an AI system.

        Args:
            ai_system_id: ID of the AI system
            name: New name for the AI system
            model: New model in format 'provider/model'
            api_key: New API key

        Returns:
            Updated details of the AI system
        """
        if model:
            provider, model_id = _parse_model(model)
        else:
            provider, model_id = None, None

        if api_key:
            provider_secrets = LLMProviderSecrets(api_key=api_key)
        else:
            provider_secrets = None

        request = UpdateThirdPartyAISystemRequest(
            name=name,
            provider=provider,
            model_id=model_id,
            provider_secrets=provider_secrets,
        )
        response = self._client.post(
            f"{self.prefix}/{ai_system_id}/update", json=request.model_dump()
        )
        response_model = GetAISystemResponse.model_validate(response)
        ai_system_dict = response_model.ai_system.model_dump(exclude_none=True)
        return TypeAdapter(AISystem).validate_python(ai_system_dict)

    def upsert_by_name(
        self,
        name: str,
        model: str | None = None,
        api_key: str | None = None,
        self_hosted_config: SelfHostedConfig | None = None,
        system_config: Dict[str, Any] | None = None,
        system_prompt: str | None = None,
    ) -> AISystem:
        """Get or create an AI system by name.

        Args:
            name: Name of the AI system
            model: Model in format 'provider/model' (e.g. 'openai/gpt-4o-mini')
            api_key: API key for third-party systems
            self_hosted_config: Self-hosted configuration
            system_config: System configuration
            system_prompt: System prompt

        Returns:
            Details of the AI system
        """
        if model and self_hosted_config:
            raise ValueError("Cannot specify both 'model' and 'self_hosted_config'")

        if not model and not self_hosted_config:
            raise ValueError(
                "Either 'model' (for third-party systems) or 'self_hosted_config' "
                "(for self-hosted systems) must be specified"
            )

        if api_key:
            provider_secrets = LLMProviderSecrets(api_key=api_key)
        else:
            provider_secrets = None

        if self_hosted_config:
            request = CreateSelfHostedAISystemRequest(
                self_hosted_config=self_hosted_config,
                provider_secrets=provider_secrets,
                ai_system_type=AISystemType.SELF_HOSTED,
                name=name,
                system_config=system_config,
                system_prompt=system_prompt,
            )
        else:
            provider, model_id = _parse_model(model)
            request = CreateThirdPartyAISystemRequest(
                ai_system_type=AISystemType.THIRD_PARTY,
                name=name,
                provider=provider,
                model_id=model_id,
                provider_secrets=provider_secrets,
                system_config=system_config,
                system_prompt=system_prompt,
            )

        response = self._client.post(
            f"{self.prefix}/upsert_by_name", json=request.model_dump()
        )
        response_model = UpdateAISystemResponse.model_validate(response)

        return TypeAdapter(AISystem).validate_python(
            response_model.ai_system.model_dump(exclude_none=True)
        )

    def get_supported_models(self) -> list[str]:
        """Get supported third-party models.

        Returns:
            List of supported models in 'provider/model' format that can be used directly
            with create() and upsert_by_name() methods
        """
        response = self._client.get(f"{self.prefix}/supported_models")
        parsed_response = GetThirdPartyModelsResponse.model_validate(response)
        models = []
        for provider, provider_models in parsed_response.supported_models.items():
            for model in provider_models:
                models.append(f"{provider.value.lower()}/{model}")
        return models


class AsyncAISystems(AsyncAPIResource):
    prefix: str = "/ai_systems"

    async def create(
        self,
        name: str,
        model: str | None = None,
        api_key: str | None = None,
        self_hosted_config: SelfHostedConfig | None = None,
        system_config: Dict[str, Any] | None = None,
        system_prompt: str | None = None,
    ) -> str:
        """Create a new AI system.

        Args:
            name: Name of the AI system
            model: Model in format 'provider/model' (e.g. 'openai/gpt-4o-mini')
            api_key: API key for third-party systems
            self_hosted_config: Self-hosted configuration
            system_config: System configuration
            system_prompt: System prompt

        Returns:
            The ID of the created AI system
        """
        if model and self_hosted_config:
            raise ValueError("Cannot specify both 'model' and 'self_hosted_config'")

        if not model and not self_hosted_config:
            raise ValueError(
                "Either 'model' (for third-party systems) or 'self_hosted_config' "
                "(for self-hosted systems) must be specified"
            )

        if api_key:
            provider_secrets = LLMProviderSecrets(api_key=api_key)
        else:
            provider_secrets = None

        if self_hosted_config:
            request = CreateSelfHostedAISystemRequest(
                self_hosted_config=self_hosted_config,
                provider_secrets=provider_secrets,
                ai_system_type=AISystemType.SELF_HOSTED,
                name=name,
                system_config=system_config,
                system_prompt=system_prompt,
            )
        else:
            provider, model_id = _parse_model(model)
            request = CreateThirdPartyAISystemRequest(
                ai_system_type=AISystemType.THIRD_PARTY,
                name=name,
                provider=provider,
                model_id=model_id,
                provider_secrets=provider_secrets,
                system_config=system_config,
                system_prompt=system_prompt,
            )

        response = await self._client.post(f"{self.prefix}", json=request.model_dump())
        return CreateAISystemResponse.model_validate(response).id

    async def get(self, ai_system_id: str) -> AISystem:
        """Get an AI system by ID.

        Args:
            ai_system_id: ID of the AI system

        Returns:
            Details about the AI system
        """
        response = await self._client.get(f"{self.prefix}/{ai_system_id}")

        response_model = GetAISystemResponse.model_validate(response)
        ai_system_dict = response_model.ai_system.model_dump(exclude_none=True)
        return TypeAdapter(AISystem).validate_python(ai_system_dict)

    async def update(
        self,
        ai_system_id: str,
        name: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        description: str | None = None,
        system_prompt: str | None = None,
        self_hosted_config: SelfHostedConfig | None = None,
        delete_key: bool = False,
    ) -> AISystem:
        """Update an AI system.

        Args:
            ai_system_id: ID of the AI system
            name: New name for the AI system
            model: New model in format 'provider/model'
            api_key: New API key
            description: New description
            system_prompt: New system prompt
            self_hosted_config: New self-hosted configuration
            delete_key: Whether to delete the API key

        Returns:
            Updated Details about the AI system
        """
        if model:
            provider, model_id = _parse_model(model)
        else:
            provider, model_id = None, None

        if api_key:
            provider_secrets = LLMProviderSecrets(api_key=api_key)
        else:
            provider_secrets = None

        if provider:
            request = UpdateThirdPartyAISystemRequest(
                name=name,
                provider=provider,
                model_id=model_id,
                provider_secrets=provider_secrets,
                description=description,
                system_prompt=system_prompt,
                delete_key=delete_key,
            )
        else:
            request = UpdateSelfHostedAISystemRequest(
                name=name,
                self_hosted_config=self_hosted_config,
                provider_secrets=provider_secrets,
                description=description,
                system_prompt=system_prompt,
                delete_key=delete_key,
            )
        response = await self._client.post(
            f"{self.prefix}/{ai_system_id}/update", json=request.model_dump()
        )
        response_model = GetAISystemResponse.model_validate(response)
        ai_system_dict = response_model.ai_system.model_dump(exclude_none=True)
        return TypeAdapter(AISystem).validate_python(ai_system_dict)

    async def upsert_by_name(
        self,
        name: str,
        model: str | None = None,
        api_key: str | None = None,
        self_hosted_config: SelfHostedConfig | None = None,
        system_config: Dict[str, Any] | None = None,
        system_prompt: str | None = None,
    ) -> AISystem:
        """Get or create an AI system by name.

        Args:
            name: Name of the AI system
            model: Model in format 'provider/model' (e.g. 'openai/gpt-4o-mini')
            api_key: API key for third-party systems
            self_hosted_config: Self-hosted configuration
            system_config: System configuration
            system_prompt: System prompt

        Returns:
            Details about the AI system
        """
        if model and self_hosted_config:
            raise ValueError("Cannot specify both 'model' and 'self_hosted_config'")

        if not model and not self_hosted_config:
            raise ValueError(
                "Either 'model' (for third-party systems) or 'self_hosted_config' "
                "(for self-hosted systems) must be specified"
            )

        if api_key:
            provider_secrets = LLMProviderSecrets(api_key=api_key)
        else:
            provider_secrets = None

        if self_hosted_config:
            request = CreateSelfHostedAISystemRequest(
                self_hosted_config=self_hosted_config,
                provider_secrets=provider_secrets,
                ai_system_type=AISystemType.SELF_HOSTED,
                name=name,
                system_config=system_config,
                system_prompt=system_prompt,
            )
        else:
            provider, model_id = _parse_model(model)
            request = CreateThirdPartyAISystemRequest(
                ai_system_type=AISystemType.THIRD_PARTY,
                name=name,
                provider=provider,
                model_id=model_id,
                provider_secrets=provider_secrets,
                system_config=system_config,
                system_prompt=system_prompt,
            )

        response = await self._client.post(
            f"{self.prefix}/upsert_by_name", json=request.model_dump()
        )
        response_model = UpdateAISystemResponse.model_validate(response)

        return TypeAdapter(AISystem).validate_python(
            response_model.ai_system.model_dump(exclude_none=True)
        )

    async def get_supported_models(self) -> list[str]:
        """Get supported third-party models.

        Returns:
            List of supported models in 'provider/model' format that can be used directly
            with create() and upsert_by_name() methods
        """
        response = await self._client.get(f"{self.prefix}/supported_models")
        parsed_response = GetThirdPartyModelsResponse.model_validate(response)
        models = []
        for provider, provider_models in parsed_response.supported_models.items():
            for model in provider_models:
                models.append(f"{provider.value.lower()}/{model}")
        return models
