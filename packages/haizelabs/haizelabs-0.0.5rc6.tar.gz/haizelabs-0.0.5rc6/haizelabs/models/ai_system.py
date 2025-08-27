from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Literal, Union

try:
    from typing import TypeAlias  # py>=3.10
except ImportError:
    from typing_extensions import TypeAlias  # py<3.10

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator

DEFAULT_TIMEOUT_SECONDS = 120.0


HUGGINGFACE_HOST = "endpoints.huggingface.cloud"
AZURE_HOST = "openai.azure.com"


class AISystemType(str, Enum):
    THIRD_PARTY = "THIRD_PARTY"
    SELF_HOSTED = "SELF_HOSTED"


class AISystemConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")  # ignore any extra fields when parsing

    temperature: float | None = None
    top_p: float | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    max_tokens: int | None = None

    model_config = {"frozen": True}


class LLMProviderSecrets(BaseModel):
    api_key: str


class BaseAISystem(BaseModel):
    id: str
    creator_id: int
    created_at: AwareDatetime | None = Field(default=None)
    ai_system_type: AISystemType
    name: str
    description: str | None = None
    system_prompt: str | None = None
    url: str | None = None
    model_id: str | None = None
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    system_config: AISystemConfig = AISystemConfig()


class ThirdPartyProvider(str, Enum):
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"
    COHERE = "COHERE"
    GEMINI = "GEMINI"
    MISTRAL = "MISTRAL"
    XAI = "XAI"


class ThirdPartyAISystem(BaseAISystem):
    ai_system_type: Literal[AISystemType.THIRD_PARTY] = AISystemType.THIRD_PARTY
    provider: ThirdPartyProvider = Field(default=ThirdPartyProvider.OPENAI)
    provider_secrets: LLMProviderSecrets | None = None
    model_id: str


class SelfHostedProvider(str, Enum):
    TOGETHER = "TOGETHER"
    FIREWORKS = "FIREWORKS"
    BEDROCK = "BEDROCK"
    OPENAI_AZURE = "OPENAI_AZURE"
    VERTEX = "VERTEX"
    # Value should be "HUGGINGFACE_INFERENCE_ENDPOINT", but left for backwards compatibility
    HUGGINGFACE_INFERENCE_ENDPOINT = "HUGGINGFACE_INFERENCE"
    HUGGINGFACE_INFERENCE_PROVIDER = "HUGGINGFACE_INFERENCE_PROVIDER"


class BedrockConfig(BaseModel):
    self_hosted_provider: Literal[SelfHostedProvider.BEDROCK] = (
        SelfHostedProvider.BEDROCK
    )
    access_key_id: str
    region_name: str
    model_id: str


class TogetherConfig(BaseModel):
    self_hosted_provider: Literal[SelfHostedProvider.TOGETHER] = (
        SelfHostedProvider.TOGETHER
    )
    model_id: str


class FireworksConfig(BaseModel):
    self_hosted_provider: Literal[SelfHostedProvider.FIREWORKS] = (
        SelfHostedProvider.FIREWORKS
    )
    model_id: str


class OpenAIAzureConfig(BaseModel):
    self_hosted_provider: Literal[SelfHostedProvider.OPENAI_AZURE] = (
        SelfHostedProvider.OPENAI_AZURE
    )
    azure_endpoint: str
    api_version: str
    deployment_name: str

    @field_validator("azure_endpoint")
    @classmethod
    def validate_endpoint(cls, value: str) -> str:
        if AZURE_HOST not in value:
            raise ValueError(f"Azure Endpoint must contain '{AZURE_HOST}'")
        return value


class VertexConfig(BaseModel):
    self_hosted_provider: Literal[SelfHostedProvider.VERTEX] = SelfHostedProvider.VERTEX
    model_id: str


class HuggingFaceInferenceEndpointConfig(BaseModel):
    self_hosted_provider: Literal[SelfHostedProvider.HUGGINGFACE_INFERENCE_ENDPOINT] = (
        SelfHostedProvider.HUGGINGFACE_INFERENCE_ENDPOINT
    )
    inference_endpoint: str

    @field_validator("inference_endpoint")
    @classmethod
    def validate_endpoint(cls, value: str) -> str:
        if HUGGINGFACE_HOST not in value:
            raise ValueError(
                f"Huggingface Inference Endpoint must contain '{HUGGINGFACE_HOST}'"
            )
        return value


class HuggingFaceInferenceProvider(str, Enum):
    AUTO = "auto"

    CEREBRAS = "cerebras"
    COHERE = "cohere"
    FAL_AI = "fal-ai"
    FEATHERLESS_AI = "featherless-ai"
    FIREWORKS = "fireworks-ai"
    GROQ = "groq"
    HUGGINGFACE_INFERENCE = "hf-inference"
    HYPERBOLIC = "hyperbolic"
    NEBIUS = "nebius"
    NOVITA = "novita"
    NSCALE = "nscale"
    REPLICATE = "replicate"
    SAMBANOVA = "sambanova"
    TOGETHER = "together"


class HuggingFaceInferenceProviderConfig(BaseModel):
    self_hosted_provider: Literal[SelfHostedProvider.HUGGINGFACE_INFERENCE_PROVIDER] = (
        SelfHostedProvider.HUGGINGFACE_INFERENCE_PROVIDER
    )
    hf_provider: HuggingFaceInferenceProvider = HuggingFaceInferenceProvider.AUTO
    model_id: str
    hf_bill_to_org: str | None = None


SelfHostedConfig = Annotated[
    Union[
        BedrockConfig,
        TogetherConfig,
        FireworksConfig,
        OpenAIAzureConfig,
        VertexConfig,
        HuggingFaceInferenceEndpointConfig,
        HuggingFaceInferenceProviderConfig,
    ],
    Field(discriminator="self_hosted_provider"),
]


class SelfHostedAISystem(BaseAISystem):
    ai_system_type: Literal[AISystemType.SELF_HOSTED] = AISystemType.SELF_HOSTED
    self_hosted_config: SelfHostedConfig


AISystem: TypeAlias = Union[ThirdPartyAISystem, SelfHostedAISystem]


class AISystemResponse(BaseModel):
    id: str
    creator_id: int
    created_at: AwareDatetime
    ai_system_type: AISystemType
    name: str
    description: str | None = None
    system_prompt: str | None = None
    model_id: str | None = None
    custom_secrets: bool = False
    api_key_suffix: str | None = None
    timeout_seconds: float | None = None
    is_judge: bool = False
    system_config: dict[str, Any] | None = None
    self_hosted_config: SelfHostedConfig | None = None


class BaseCreateAISystemRequest(BaseModel):
    ai_system_type: AISystemType
    name: str
    description: str | None = None
    system_prompt: str | None = None
    is_judge: bool = False
    system_config: dict[str, Any] | None = None
    provider_secrets: LLMProviderSecrets | None = None


class CreateThirdPartyAISystemRequest(BaseCreateAISystemRequest):
    ai_system_type: Literal[AISystemType.THIRD_PARTY] = AISystemType.THIRD_PARTY
    provider: ThirdPartyProvider
    model_id: str


class CreateSelfHostedAISystemRequest(BaseCreateAISystemRequest):
    ai_system_type: Literal[AISystemType.SELF_HOSTED] = AISystemType.SELF_HOSTED
    self_hosted_config: SelfHostedConfig


CreateAISystemRequest: TypeAlias = Union[
    CreateThirdPartyAISystemRequest, CreateSelfHostedAISystemRequest
]


class CreateAISystemResponse(BaseModel):
    id: str


class GetAISystemResponse(BaseModel):
    ai_system: AISystemResponse


class BaseUpdateAISystemRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    delete_key: bool = False

    provider_secrets: LLMProviderSecrets | None = None


class UpdateThirdPartyAISystemRequest(BaseUpdateAISystemRequest):
    model_id: str | None = None
    provider: ThirdPartyProvider | None = None


class UpdateSelfHostedAISystemRequest(BaseUpdateAISystemRequest):
    self_hosted_config: SelfHostedConfig | None = None


UpdateAISystemRequest: TypeAlias = Union[
    UpdateThirdPartyAISystemRequest, UpdateSelfHostedAISystemRequest
]

UpdateAISystemResponse = GetAISystemResponse


class GetThirdPartyModelsResponse(BaseModel):
    """Response containing third-party models grouped by provider"""

    supported_models: dict[ThirdPartyProvider, list[str]]
