from __future__ import annotations

from typing import Optional

from pydantic import AwareDatetime, BaseModel

from haizelabs.models.behaviors import BehaviorType, CodeOfConductBehaviorRequest


class CodeOfConductResponse(BaseModel):
    id: str
    creator_id: int
    updater_id: int
    created_at: AwareDatetime
    updated_at: AwareDatetime
    name: str
    description: str | None = None


class GetCodeOfConductResponse(BaseModel):
    coc: CodeOfConductResponse


class CodeOfConductPolicyResponse(BaseModel):
    id: str
    coc_id: str
    creator_id: int
    updater_id: int
    created_at: AwareDatetime
    updated_at: AwareDatetime
    policy: str


class GetCodeOfConductPolicyResponse(BaseModel):
    policy: CodeOfConductPolicyResponse


class GetCodeOfConductPoliciesResponse(BaseModel):
    policies: list[CodeOfConductPolicyResponse]


class CodeOfConductViolationResponse(BaseModel):
    id: str
    creator_id: int
    updater_id: int
    policy_id: str
    coc_id: str
    violation: str

    def to_behavior_request(self) -> "CodeOfConductBehaviorRequest":
        """Convert this violation response to a CodeOfConductBehaviorRequest."""
        return CodeOfConductBehaviorRequest(
            behavior=self.violation,
            violation_id=self.id,
            policy_id=self.policy_id,
            coc_id=self.coc_id,
            type=BehaviorType.CODE_OF_CONDUCT,
        )


class GetCodeOfConductViolationsResponse(BaseModel):
    violations: list[CodeOfConductViolationResponse]

    def to_behavior_requests(self) -> list["CodeOfConductBehaviorRequest"]:
        """Convert all violations to a list of CodeOfConductBehaviorRequest objects."""
        return [violation.to_behavior_request() for violation in self.violations]


class GetCodeOfConductViolationResponse(BaseModel):
    violation: CodeOfConductViolationResponse


# Request models
class CreateCodeOfConductRequest(BaseModel):
    name: str
    description: Optional[str] = None


class CreateCodeOfConductResponse(BaseModel):
    coc_id: str


class CreateCodeOfConductPolicyRequest(BaseModel):
    policy: str
    coc_id: str


class CreateCodeOfConductPolicyResponse(BaseModel):
    policy_id: str
    coc_id: str


class CreateCodeOfConductViolationRequest(BaseModel):
    violation: str
    policy_id: str
    coc_id: str


class CreateCodeOfConductViolationResponse(BaseModel):
    violation_id: str
    policy_id: str
    coc_id: str


class CreateCodeOfConductViolationsRequest(BaseModel):
    violations: list[CreateCodeOfConductViolationRequest]


class CreateCodeOfConductViolationsResponse(BaseModel):
    violations: list[CreateCodeOfConductViolationResponse]


class UpdateCodeOfConductRequest(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


class UpdateCodeOfConductResponse(BaseModel):
    coc: CodeOfConductResponse


class UpdateCodeOfConductPolicyRequest(BaseModel):
    id: str
    coc_id: str
    policy: str


class UpdateCodeOfConductPolicyResponse(BaseModel):
    policy: CodeOfConductPolicyResponse


class UpdateCodeOfConductViolationRequest(BaseModel):
    id: str
    coc_id: str
    policy_id: str
    violation: str


class UpdateCodeOfConductViolationResponse(BaseModel):
    violation: CodeOfConductViolationResponse


class DeleteResponse(BaseModel):
    success: bool
