from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, TypeAdapter

from haizelabs.models.data_columns import DataColumn, DataColumns
from haizelabs.models.data_rows import DataRow
from haizelabs.models.data_types import DataPyType
from haizelabs.models.label_types import (
    ContinuousLabelValue,
    EnumLabelValue,
    LabelType,
    LabelTypeType,
    LabelValue,
)
from haizelabs.models.prompt_templates import PromptTemplate


class JudgeID(BaseModel):
    id: str
    version: Optional[int] = None


class JudgeOutputFormat(str, Enum):
    STRUCTURED_OUTPUT = "STRUCTURED_OUTPUT"
    XML_TAGS = "XML_TAGS"


class BaseJudgeLabel(BaseModel):
    value: LabelValue
    confidence: Optional[float] = None

    @classmethod
    def from_label_value(
        cls, label_type: LabelType, label_value: LabelValue
    ) -> "JudgeLabel":
        if label_type.type == LabelTypeType.ENUM:
            if not isinstance(label_value, EnumLabelValue):
                raise ValueError(f"Invalid label value: {type(label_value)}")
            return EnumJudgeLabel(value=label_value)
        elif label_type.type == LabelTypeType.CONTINUOUS:
            if not isinstance(label_value, ContinuousLabelValue):
                raise ValueError(f"Invalid label value: {type(label_value)}")
            return ContinuousJudgeLabel(value=label_value)
        else:
            raise ValueError(f"Invalid label type: {type(label_type)}")


class EnumJudgeLabel(BaseJudgeLabel):
    value: EnumLabelValue
    class_probs: Optional[Dict[str, float]] = None


class ContinuousJudgeLabel(BaseJudgeLabel):
    value: ContinuousLabelValue


JudgeLabel = Union[EnumJudgeLabel, ContinuousJudgeLabel]


class CallJudgeResponse(BaseModel):
    judge_id: JudgeID
    label: JudgeLabel


class JudgeInput(BaseModel):
    row: DataRow

    @classmethod
    def create(
        cls, columns_list: List[DataColumn], values: List[DataPyType]
    ) -> "JudgeInput":
        return JudgeInput(
            row=DataRow(columns=DataColumns.from_list(columns_list), data=tuple(values))
        )


class JudgeType(str, Enum):
    STATIC_PROMPT = "STATIC_PROMPT"
    EXACT_MATCH = "EXACT_MATCH"
    REGEX_MATCH = "REGEX_MATCH"


class JudgeBase(BaseModel):
    id: str
    name: str
    version: int
    judge_type: JudgeType
    label_type: LabelType

    @classmethod
    def from_api_response(cls, judge_dict: Dict[str, Any]) -> "Judge":
        return TypeAdapter(Judge).validate_python(judge_dict)


class StaticPromptJudge(JudgeBase):
    judge_type: Literal[JudgeType.STATIC_PROMPT] = JudgeType.STATIC_PROMPT
    ai_system_id: str
    system_prompt: str
    prompt_template: PromptTemplate
    output_format: JudgeOutputFormat = JudgeOutputFormat.STRUCTURED_OUTPUT


class ExactMatchJudge(JudgeBase):
    judge_type: Literal[JudgeType.EXACT_MATCH] = JudgeType.EXACT_MATCH
    default_match_value: str
    column_name: str | None = None


class RegexMatchJudge(JudgeBase):
    judge_type: Literal[JudgeType.REGEX_MATCH] = JudgeType.REGEX_MATCH
    default_regex_pattern: str
    column_name: str | None = None


Judge = Union[StaticPromptJudge, ExactMatchJudge, RegexMatchJudge]


class UpsertJudgeRequest(BaseModel):
    name: str
    description: str | None = None
    judge_type: JudgeType
    label_type: LabelType


class UpsertStaticPromptJudgeRequest(UpsertJudgeRequest):
    judge_type: Literal[JudgeType.STATIC_PROMPT] = JudgeType.STATIC_PROMPT
    ai_system_id: str
    system_prompt: str
    prompt_template: PromptTemplate
    output_format: JudgeOutputFormat = JudgeOutputFormat.STRUCTURED_OUTPUT
    provides_rationale: bool = False


class UpsertExactMatchJudgeRequest(UpsertJudgeRequest):
    judge_type: Literal[JudgeType.EXACT_MATCH] = JudgeType.EXACT_MATCH
    default_match_value: str
    column_name: str | None = None


class UpsertRegexMatchJudgeRequest(UpsertJudgeRequest):
    judge_type: Literal[JudgeType.REGEX_MATCH] = JudgeType.REGEX_MATCH
    default_regex_pattern: str
    column_name: str | None = None


UpsertJudgeRequestType = Union[
    UpsertStaticPromptJudgeRequest,
    UpsertExactMatchJudgeRequest,
    UpsertRegexMatchJudgeRequest,
]


class GetJudgeResponse(BaseModel):
    judge: Judge


class UpsertJudgeResponse(BaseModel):
    id: str
    version: int
