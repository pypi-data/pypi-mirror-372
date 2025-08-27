from enum import Enum
from typing import List, Literal, Optional, Type, Union

from pydantic import BaseModel, Field, create_model


class LabelTypeType(str, Enum):
    ENUM = "enum"
    CONTINUOUS = "continuous"


class ContinuousLabelValue(BaseModel):
    score: float


class EnumLabelValue(BaseModel):
    option: str


LabelValue = Union[ContinuousLabelValue, EnumLabelValue]


class EnumLabelType(BaseModel):
    type: Literal[LabelTypeType.ENUM] = LabelTypeType.ENUM
    options: List[str]

    def compatible_with(self, other: "EnumLabelType") -> bool:
        return isinstance(other, EnumLabelType) and self.is_subset_of(other)

    def is_subset_of(self, other: "EnumLabelType") -> bool:
        return set(self.options) <= set(other.options)

    def build_pydantic_model(self) -> Type[EnumLabelValue]:
        options_field = (
            str,
            Field(
                description=f"A label from the given options: [{', '.join(self.options)}]",
                pattern=f"^({'|'.join(self.options)})$",
            ),
        )
        return create_model(
            "CustomEnumLabelValue",
            option=options_field,
            __base__=EnumLabelValue,
        )


class ContinuousLabelType(BaseModel):
    type: Literal[LabelTypeType.CONTINUOUS] = LabelTypeType.CONTINUOUS
    # None == No limit
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    def compatible_with(self, other: "ContinuousLabelType") -> bool:
        return isinstance(other, ContinuousLabelType) and self.is_subset_of(other)

    def is_subset_of(self, other: "ContinuousLabelType") -> bool:
        min_value = self.min_value if self.min_value is not None else float("-inf")
        max_value = self.max_value if self.max_value is not None else float("inf")
        other_min_value = (
            other.min_value if other.min_value is not None else float("-inf")
        )
        other_max_value = (
            other.max_value if other.max_value is not None else float("inf")
        )
        return min_value >= other_min_value and max_value <= other_max_value

    def build_pydantic_model(self) -> Type[ContinuousLabelValue]:
        min_value = self.min_value if self.min_value is not None else float("-inf")
        max_value = self.max_value if self.max_value is not None else float("inf")
        score_field = (
            float,
            Field(
                description=f"A float score bewteen range {min_value} and {max_value} (inclusive)",
                ge=min_value,
                le=max_value,
            ),
        )
        return create_model(
            "CustomContinuousLabelValue",
            score=score_field,
            __base__=ContinuousLabelValue,
        )


LabelType = Union[EnumLabelType, ContinuousLabelType]
