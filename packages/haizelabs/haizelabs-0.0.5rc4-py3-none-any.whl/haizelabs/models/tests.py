from __future__ import annotations

from abc import ABC
from enum import Enum
from typing import Literal

from pydantic import AwareDatetime, BaseModel, Field

from haizelabs.models.behaviors import BehaviorRequest, BehaviorResponse
from haizelabs.models.common import ChatCompletionMessage
from haizelabs.models.judges import JudgeID, JudgeLabel
from haizelabs.models.prompt_templates import PromptTemplate


class TestType(str, Enum):
    RED_TEAM_TEST = "RED_TEAM_TEST"
    FUZZ_TEST = "FUZZ_TEST"
    UNIT_TEST = "UNIT_TEST"


class CreateTestRequest(BaseModel, ABC):
    name: str
    system_id: str
    judge_ids: list[JudgeID]
    prompt_template_id: str | None = None


class CreateRedTeamTestRequest(CreateTestRequest):
    test_type: Literal[TestType.RED_TEAM_TEST] = TestType.RED_TEAM_TEST
    attack_system_id: str | None = None
    behaviors: list[BehaviorRequest]
    creativity: int = Field(default=5, ge=1, le=5)


class ExportRedTeamDatasetRequest(BaseModel):
    dataset_name: str
    dataset_description: str
    minimum_score: float


class CreateTestResponse(BaseModel):
    test_id: str


class TestStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    CANCELLING = "CANCELLING"
    CANCELLED = "CANCELLED"
    SUCCEEDED = "SUCCEEDED"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILED = "FAILED"


class RedTeamTestResponse(BaseModel):
    id: str
    creator_id: int
    name: str
    test_type: TestType
    status: TestStatus
    system_id: str
    attack_system_id: str | None = None
    judge_ids: list[JudgeID]
    started_at: AwareDatetime | None = None
    completed_at: AwareDatetime | None = None
    cancelled_at: AwareDatetime | None = None
    span_id: str | None = None
    trace_id: str | None = None
    behaviors: list[BehaviorResponse]
    creativity: int = Field(default=5, ge=1, le=5)


class RedTeamTestTimeSeriesDatum(BaseModel):
    value: float
    test_progress: float  # test routine progress (test_step/max_steps)


class RedTeamTestMetricsResponse(BaseModel):
    test_id: str
    exploration_series: list[RedTeamTestTimeSeriesDatum]
    num_successful_series: list[RedTeamTestTimeSeriesDatum]
    # to do, evan: Add `behavior_to_data`
    total_attacks: int
    average_behavior_duration: float
    average_response_length: float
    exploration_metric: float


class RedTeamTestBehaviorMetrics(BaseModel):
    num_successful_series: list[RedTeamTestTimeSeriesDatum]
    exploration_series: list[RedTeamTestTimeSeriesDatum]


class GetRedTeamTestResponse(BaseModel):
    test: RedTeamTestResponse


class StartTestResponse(BaseModel):
    success: bool


class CancelTestResponse(BaseModel):
    success: bool


class PromptTemplateType(str, Enum):
    OUTPUT_ONLY = "output_only"
    AI_SYSTEM = "ai_system"
    JUDGE = "judge"

    def is_judge_template(self) -> bool:
        return self in [PromptTemplateType.JUDGE, PromptTemplateType.OUTPUT_ONLY]


class PromptTemplateReference(BaseModel):
    """Reference to a prompt template, used in CreateUnitTestAPIRequest."""

    template: str
    prompt_template_type: PromptTemplateType


class CreateUnitTestAPIRequest(BaseModel):
    """Used exclusively by the SDK to create a unit test."""

    name: str
    system_id: str
    judge_ids: list[JudgeID]
    prompt_template: PromptTemplateReference
    dataset_id: str
    dataset_version: int


class CreateUnitTestRequest(BaseModel):
    name: str
    system_id: str
    judge_ids: list[JudgeID]
    prompt_template: PromptTemplate
    dataset_id: str
    dataset_version: int


class UnitTestAPIResponse(BaseModel):
    id: str
    creator_id: int
    name: str
    status: TestStatus
    system_id: str
    judge_ids: list[JudgeID]
    prompt_template: PromptTemplateReference
    dataset_id: str
    dataset_version: int
    started_at: AwareDatetime | None = None
    completed_at: AwareDatetime | None = None
    cancelled_at: AwareDatetime | None = None


class GetUnitTestAPIResponse(BaseModel):
    """Used exclusively by the SDK to get a unit test."""

    test: UnitTestAPIResponse


class UnitTestResponse(BaseModel):
    id: str
    creator_id: int
    name: str
    status: TestStatus
    system_id: str
    judge_ids: list[JudgeID]
    prompt_template: PromptTemplate
    dataset_id: str
    dataset_version: int
    started_at: AwareDatetime | None = None
    completed_at: AwareDatetime | None = None
    cancelled_at: AwareDatetime | None = None


class GetUnitTestResponse(BaseModel):
    test: UnitTestResponse


class JudgeInferenceResponse(BaseModel):
    judge_id: JudgeID
    label: JudgeLabel


class RedTeamTestIterationResponse(BaseModel):
    iteration_number: int
    step_number: int
    sut_input: list[ChatCompletionMessage]
    sut_output: ChatCompletionMessage
    judge_results: list[JudgeInferenceResponse]
    behavior: BehaviorResponse
    created_at: AwareDatetime
    completed_at: AwareDatetime


class GetRedTeamTestResultsResponse(BaseModel):
    """Used exclusively by the SDK to get the results of a Red Team test."""

    results: list[RedTeamTestIterationResponse]


class PlatformJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobStatusResponse(BaseModel):
    status: PlatformJobStatus
