from enum import Enum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class BehaviorType(str, Enum):
    PREDEFINED = "PREDEFINED"
    CUSTOM = "CUSTOM"
    CODE_OF_CONDUCT = "CODE_OF_CONDUCT"


class BaseBehaviorRequest(BaseModel):
    behavior: str
    type: BehaviorType


class CodeOfConductBehaviorRequest(BaseBehaviorRequest):
    violation_id: str
    policy_id: str
    coc_id: str
    type: Literal[BehaviorType.CODE_OF_CONDUCT] = Field(
        default=BehaviorType.CODE_OF_CONDUCT
    )


class PredefinedBehaviorRequest(BaseBehaviorRequest):
    source: str
    type: Literal[BehaviorType.PREDEFINED] = Field(default=BehaviorType.PREDEFINED)


class CustomBehaviorRequest(BaseBehaviorRequest):
    type: Literal[BehaviorType.CUSTOM] = Field(default=BehaviorType.CUSTOM)


BehaviorRequest = Annotated[
    Union[
        CodeOfConductBehaviorRequest, PredefinedBehaviorRequest, CustomBehaviorRequest
    ],
    Field(discriminator="type"),
]


class BaseBehaviorResponse(BaseModel):
    behavior: str
    type: BehaviorType


class CodeOfConductBehaviorResponse(BaseBehaviorResponse):
    violation_id: str
    policy_id: str
    coc_id: str
    type: Literal[BehaviorType.CODE_OF_CONDUCT] = Field(
        default=BehaviorType.CODE_OF_CONDUCT
    )


class PredefinedBehaviorResponse(BaseBehaviorResponse):
    source: str
    type: Literal[BehaviorType.PREDEFINED] = Field(default=BehaviorType.PREDEFINED)


class CustomBehaviorResponse(BaseBehaviorResponse):
    type: Literal[BehaviorType.CUSTOM] = Field(default=BehaviorType.CUSTOM)


BehaviorResponse = Annotated[
    Union[
        CodeOfConductBehaviorResponse,
        PredefinedBehaviorResponse,
        CustomBehaviorResponse,
    ],
    Field(discriminator="type"),
]
