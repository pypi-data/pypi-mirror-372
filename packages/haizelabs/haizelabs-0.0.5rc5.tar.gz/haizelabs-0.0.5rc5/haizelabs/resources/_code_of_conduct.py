from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from haizelabs._resource import AsyncAPIResource, SyncAPIResource
from haizelabs.models.code_of_conduct import (
    CodeOfConductViolationResponse,
    CreateCodeOfConductPolicyRequest,
    CreateCodeOfConductPolicyResponse,
    CreateCodeOfConductRequest,
    CreateCodeOfConductResponse,
    CreateCodeOfConductViolationRequest,
    CreateCodeOfConductViolationResponse,
    CreateCodeOfConductViolationsRequest,
    CreateCodeOfConductViolationsResponse,
    GetCodeOfConductPoliciesResponse,
    GetCodeOfConductPolicyResponse,
    GetCodeOfConductResponse,
    GetCodeOfConductViolationResponse,
    GetCodeOfConductViolationsResponse,
    UpdateCodeOfConductPolicyRequest,
    UpdateCodeOfConductPolicyResponse,
    UpdateCodeOfConductRequest,
    UpdateCodeOfConductResponse,
    UpdateCodeOfConductViolationRequest,
    UpdateCodeOfConductViolationResponse,
)

if TYPE_CHECKING:
    pass


class SyncCodeOfConduct(SyncAPIResource):
    prefix: str = "/cocs"

    def create(
        self, name: str, description: str | None = None
    ) -> CreateCodeOfConductResponse:
        """Create a new Code of Conduct.

        Args:
            name: Name of the Code of Conduct
            description: Optional description

        Returns:
            CreateCodeOfConductResponse with coc_id
        """
        request = CreateCodeOfConductRequest(name=name, description=description)
        response = self._client.post(f"{self.prefix}/create", json=request.model_dump())
        return CreateCodeOfConductResponse.model_validate(response)

    def get(self, coc_id: str) -> GetCodeOfConductResponse:
        """Get a Code of Conduct by ID.

        Args:
            coc_id: ID of the Code of Conduct

        Returns:
            GetCodeOfConductResponse with Code of Conduct details
        """
        response = self._client.get(f"{self.prefix}/{coc_id}")
        return GetCodeOfConductResponse.model_validate(response)

    def get_policies(self, coc_id: str) -> GetCodeOfConductPoliciesResponse:
        """Get all policies for a Code of Conduct.

        Args:
            coc_id: ID of the Code of Conduct

        Returns:
            GetCodeOfConductPoliciesResponse with list of policies
        """
        response = self._client.get(f"{self.prefix}/{coc_id}/get_policies")
        return GetCodeOfConductPoliciesResponse.model_validate(response)

    def create_policy(
        self, coc_id: str, policy: str
    ) -> CreateCodeOfConductPolicyResponse:
        """Create a new policy for a Code of Conduct.

        Args:
            coc_id: ID of the Code of Conduct
            policy: Policy text

        Returns:
            CreateCodeOfConductPolicyResponse with policy_id
        """
        request = CreateCodeOfConductPolicyRequest(policy=policy, coc_id=coc_id)
        response = self._client.post(
            f"{self.prefix}/{coc_id}/create_policy", json=request.model_dump()
        )
        return CreateCodeOfConductPolicyResponse.model_validate(response)

    def get_policy(self, coc_id: str, policy_id: str) -> GetCodeOfConductPolicyResponse:
        """Get a specific policy.

        Args:
            coc_id: ID of the Code of Conduct
            policy_id: ID of the policy

        Returns:
            GetCodeOfConductPolicyResponse with policy details
        """
        response = self._client.get(f"{self.prefix}/{coc_id}/{policy_id}")
        return GetCodeOfConductPolicyResponse.model_validate(response)

    def create_violation(
        self, coc_id: str, policy_id: str, violation: str
    ) -> CreateCodeOfConductViolationResponse:
        """Create a new violation for a policy.

        Args:
            coc_id: ID of the Code of Conduct
            policy_id: ID of the policy
            violation: Violation description

        Returns:
            CreateCodeOfConductViolationResponse with violation_id
        """
        request = CreateCodeOfConductViolationRequest(
            violation=violation, policy_id=policy_id, coc_id=coc_id
        )
        response = self._client.post(
            f"{self.prefix}/{coc_id}/{policy_id}/create_violation",
            json=request.model_dump(),
        )
        return CreateCodeOfConductViolationResponse.model_validate(response)

    def get_violations(self, coc_id: str) -> GetCodeOfConductViolationsResponse:
        """Get all violations across all policies for a Code of Conduct.

        Args:
            coc_id: ID of the Code of Conduct

        Returns:
            GetCodeOfConductViolationsResponse with list of violations
        """
        policies_response = self._client.get(f"{self.prefix}/{coc_id}/get_policies")
        policy_ids = [policy["id"] for policy in policies_response["policies"]]
        violations = []
        for policy_id in policy_ids:
            violations_response = self._client.get(
                f"{self.prefix}/{coc_id}/{policy_id}/get_violations"
            )
            violations.extend(
                [
                    CodeOfConductViolationResponse.model_validate(violation)
                    for violation in violations_response["violations"]
                ]
            )
        return GetCodeOfConductViolationsResponse.model_validate(
            {"violations": violations}
        )

    def update(
        self, coc_id: str, name: str, description: str | None = None
    ) -> UpdateCodeOfConductResponse:
        """Update a Code of Conduct.

        Args:
            coc_id: ID of the Code of Conduct
            name: New name
            description: New description

        Returns:
            UpdateCodeOfConductResponse with updated details
        """
        request = UpdateCodeOfConductRequest(
            id=coc_id, name=name, description=description
        )
        response = self._client.post(
            f"{self.prefix}/{coc_id}/update", json=request.model_dump()
        )
        return UpdateCodeOfConductResponse.model_validate(response)

    def delete(self, coc_id: str) -> bool:
        """Delete a Code of Conduct.

        Args:
            coc_id: ID of the Code of Conduct

        Returns:
            True if successful
        """
        response = self._client.delete(f"{self.prefix}/{coc_id}")
        return response

    def update_policy(
        self, coc_id: str, policy_id: str, policy: str
    ) -> UpdateCodeOfConductPolicyResponse:
        """Update a Code of Conduct policy.

        Args:
            coc_id: ID of the Code of Conduct
            policy_id: ID of the policy
            policy: New policy text

        Returns:
            UpdateCodeOfConductPolicyResponse with updated details
        """
        request = UpdateCodeOfConductPolicyRequest(
            id=policy_id, coc_id=coc_id, policy=policy
        )
        response = self._client.post(
            f"{self.prefix}/{coc_id}/{policy_id}/update", json=request.model_dump()
        )
        return UpdateCodeOfConductPolicyResponse.model_validate(response)

    def delete_policy(self, coc_id: str, policy_id: str) -> bool:
        """Delete a Code of Conduct policy.

        Args:
            coc_id: ID of the Code of Conduct
            policy_id: ID of the policy

        Returns:
            True if successful
        """
        response = self._client.delete(f"{self.prefix}/{coc_id}/{policy_id}")
        return response

    def get_policy_violations(
        self, coc_id: str, policy_id: str
    ) -> GetCodeOfConductViolationsResponse:
        """Get violations for a specific policy.

        Args:
            coc_id: ID of the Code of Conduct
            policy_id: ID of the policy

        Returns:
            GetCodeOfConductViolationsResponse with list of violations
        """
        response = self._client.get(
            f"{self.prefix}/{coc_id}/{policy_id}/get_violations"
        )
        return GetCodeOfConductViolationsResponse.model_validate(response)

    def create_violations(
        self,
        coc_id: str,
        policy_id: str,
        violations: list[CreateCodeOfConductViolationRequest],
    ) -> CreateCodeOfConductViolationsResponse:
        """Create multiple violations for a policy.

        Args:
            coc_id: ID of the Code of Conduct
            policy_id: ID of the policy
            violations: List of violation requests

        Returns:
            CreateCodeOfConductViolationsResponse with created violations
        """
        request = CreateCodeOfConductViolationsRequest(violations=violations)
        response = self._client.post(
            f"{self.prefix}/{coc_id}/{policy_id}/create_violations",
            json=request.model_dump(),
        )
        return CreateCodeOfConductViolationsResponse.model_validate(response)

    def get_violation(
        self, coc_id: str, policy_id: str, violation_id: str
    ) -> GetCodeOfConductViolationResponse:
        """Get a specific violation.

        Args:
            coc_id: ID of the Code of Conduct
            policy_id: ID of the policy
            violation_id: ID of the violation

        Returns:
            GetCodeOfConductViolationResponse with violation details
        """
        response = self._client.get(
            f"{self.prefix}/{coc_id}/{policy_id}/{violation_id}"
        )
        return GetCodeOfConductViolationResponse.model_validate(response)

    def update_violation(
        self, coc_id: str, policy_id: str, violation_id: str, violation: str
    ) -> UpdateCodeOfConductViolationResponse:
        """Update a violation.

        Args:
            coc_id: ID of the Code of Conduct
            policy_id: ID of the policy
            violation_id: ID of the violation
            violation: New violation text

        Returns:
            UpdateCodeOfConductViolationResponse with updated details
        """
        request = UpdateCodeOfConductViolationRequest(
            id=violation_id, coc_id=coc_id, policy_id=policy_id, violation=violation
        )
        response = self._client.post(
            f"{self.prefix}/{coc_id}/{policy_id}/{violation_id}/update",
            json=request.model_dump(),
        )
        return UpdateCodeOfConductViolationResponse.model_validate(response)

    def delete_violation(self, coc_id: str, policy_id: str, violation_id: str) -> bool:
        """Delete a violation.

        Args:
            coc_id: ID of the Code of Conduct
            policy_id: ID of the policy
            violation_id: ID of the violation

        Returns:
            True if successful
        """
        response = self._client.delete(
            f"{self.prefix}/{coc_id}/{policy_id}/{violation_id}"
        )
        return response


class AsyncCodeOfConduct(AsyncAPIResource):
    prefix: str = "/cocs"

    async def create(
        self, name: str, description: str | None = None
    ) -> CreateCodeOfConductResponse:
        """Create a new Code of Conduct.

        Args:
            name: Name of the Code of Conduct
            description: Optional description

        Returns:
            CreateCodeOfConductResponse with coc_id
        """
        request = CreateCodeOfConductRequest(name=name, description=description)
        response = await self._client.post(
            f"{self.prefix}/create", json=request.model_dump()
        )
        return CreateCodeOfConductResponse.model_validate(response)

    async def get(self, coc_id: str) -> GetCodeOfConductResponse:
        """Get a Code of Conduct by ID.

        Args:
            coc_id: ID of the Code of Conduct

        Returns:
            GetCodeOfConductResponse with Code of Conduct details
        """
        response = await self._client.get(f"{self.prefix}/{coc_id}")
        return GetCodeOfConductResponse.model_validate(response)

    async def get_policies(self, coc_id: str) -> GetCodeOfConductPoliciesResponse:
        """Get all policies for a Code of Conduct.

        Args:
            coc_id: ID of the Code of Conduct

        Returns:
            GetCodeOfConductPoliciesResponse with list of policies
        """
        response = await self._client.get(f"{self.prefix}/{coc_id}/get_policies")
        return GetCodeOfConductPoliciesResponse.model_validate(response)

    async def create_policy(
        self, coc_id: str, policy: str
    ) -> CreateCodeOfConductPolicyResponse:
        """Create a new policy for a Code of Conduct.

        Args:
            coc_id: ID of the Code of Conduct
            policy: Policy text

        Returns:
            CreateCodeOfConductPolicyResponse with policy_id
        """
        request = CreateCodeOfConductPolicyRequest(policy=policy, coc_id=coc_id)
        response = await self._client.post(
            f"{self.prefix}/{coc_id}/create_policy", json=request.model_dump()
        )
        return CreateCodeOfConductPolicyResponse.model_validate(response)

    async def get_policy(
        self, coc_id: str, policy_id: str
    ) -> GetCodeOfConductPolicyResponse:
        """Get a specific policy.

        Args:
            coc_id: ID of the Code of Conduct
            policy_id: ID of the policy

        Returns:
            GetCodeOfConductPolicyResponse with policy details
        """
        response = await self._client.get(f"{self.prefix}/{coc_id}/{policy_id}")
        return GetCodeOfConductPolicyResponse.model_validate(response)

    async def create_violation(
        self, coc_id: str, policy_id: str, violation: str
    ) -> CreateCodeOfConductViolationResponse:
        """Create a new violation for a policy.

        Args:
            coc_id: ID of the Code of Conduct
            policy_id: ID of the policy
            violation: Violation description

        Returns:
            CreateCodeOfConductViolationResponse with violation_id
        """
        request = CreateCodeOfConductViolationRequest(
            violation=violation, policy_id=policy_id, coc_id=coc_id
        )
        response = await self._client.post(
            f"{self.prefix}/{coc_id}/{policy_id}/create_violation",
            json=request.model_dump(),
        )
        return CreateCodeOfConductViolationResponse.model_validate(response)

    async def get_violation(
        self, coc_id: str, policy_id: str, violation_id: str
    ) -> GetCodeOfConductViolationResponse:
        """Get a specific violation.

        Args:
            coc_id: ID of the Code of Conduct
            policy_id: ID of the policy
            violation_id: ID of the violation

        Returns:
            GetCodeOfConductViolationResponse with violation details
        """
        response = await self._client.get(
            f"{self.prefix}/{coc_id}/{policy_id}/{violation_id}"
        )
        return GetCodeOfConductViolationResponse.model_validate(response)

    async def get_violations(self, coc_id: str) -> GetCodeOfConductViolationsResponse:
        """Get all violations across all policies for a Code of Conduct.

        Args:
            coc_id: ID of the Code of Conduct

        Returns:
            GetCodeOfConductViolationsResponse with list of violations
        """
        policies_response = await self._client.get(
            f"{self.prefix}/{coc_id}/get_policies"
        )
        policy_ids = [policy["id"] for policy in policies_response["policies"]]

        async def get_violations(
            policy_id: str,
        ) -> list[CodeOfConductViolationResponse]:
            violations_response = await self._client.get(
                f"{self.prefix}/{coc_id}/{policy_id}/get_violations"
            )
            return [
                CodeOfConductViolationResponse.model_validate(violation)
                for violation in violations_response["violations"]
            ]

        results = await asyncio.gather(
            *(get_violations(policy_id) for policy_id in policy_ids)
        )
        all_violations = [violation for sublist in results for violation in sublist]

        return GetCodeOfConductViolationsResponse.model_validate(
            {"violations": all_violations}
        )

    async def update(
        self, coc_id: str, name: str, description: str | None = None
    ) -> UpdateCodeOfConductResponse:
        """Update a Code of Conduct.

        Args:
            coc_id: ID of the Code of Conduct
            name: New name
            description: New description

        Returns:
            UpdateCodeOfConductResponse with updated details
        """
        request = UpdateCodeOfConductRequest(
            id=coc_id, name=name, description=description
        )
        response = await self._client.post(
            f"{self.prefix}/{coc_id}/update", json=request.model_dump()
        )
        return UpdateCodeOfConductResponse.model_validate(response)

    async def delete(self, coc_id: str) -> bool:
        """Delete a Code of Conduct.

        Args:
            coc_id: ID of the Code of Conduct

        Returns:
            True if successful
        """
        response = await self._client.delete(f"{self.prefix}/{coc_id}")
        return response

    async def update_policy(
        self, coc_id: str, policy_id: str, policy: str
    ) -> UpdateCodeOfConductPolicyResponse:
        """Update a Code of Conduct policy.

        Args:
            coc_id: ID of the Code of Conduct
            policy_id: ID of the policy
            policy: New policy text

        Returns:
            UpdateCodeOfConductPolicyResponse with updated details
        """
        request = UpdateCodeOfConductPolicyRequest(
            id=policy_id, coc_id=coc_id, policy=policy
        )
        response = await self._client.post(
            f"{self.prefix}/{coc_id}/{policy_id}/update", json=request.model_dump()
        )
        return UpdateCodeOfConductPolicyResponse.model_validate(response)

    async def delete_policy(self, coc_id: str, policy_id: str) -> bool:
        """Delete a Code of Conduct policy.

        Args:
            coc_id: ID of the Code of Conduct
            policy_id: ID of the policy

        Returns:
            True if successful
        """
        response = await self._client.delete(f"{self.prefix}/{coc_id}/{policy_id}")
        return response

    async def get_policy_violations(
        self, coc_id: str, policy_id: str
    ) -> GetCodeOfConductViolationsResponse:
        """Get violations for a specific policy.

        Args:
            coc_id: ID of the Code of Conduct
            policy_id: ID of the policy

        Returns:
            GetCodeOfConductViolationsResponse with list of violations
        """
        response = await self._client.get(
            f"{self.prefix}/{coc_id}/{policy_id}/get_violations"
        )
        return GetCodeOfConductViolationsResponse.model_validate(response)

    async def create_violations(
        self,
        coc_id: str,
        policy_id: str,
        violations: list[CreateCodeOfConductViolationRequest],
    ) -> CreateCodeOfConductViolationsResponse:
        """Create multiple violations for a policy.

        Args:
            coc_id: ID of the Code of Conduct
            policy_id: ID of the policy
            violations: List of violation requests

        Returns:
            CreateCodeOfConductViolationsResponse with created violations
        """
        request = CreateCodeOfConductViolationsRequest(violations=violations)
        response = await self._client.post(
            f"{self.prefix}/{coc_id}/{policy_id}/create_violations",
            json=request.model_dump(),
        )
        return CreateCodeOfConductViolationsResponse.model_validate(response)

    async def update_violation(
        self, coc_id: str, policy_id: str, violation_id: str, violation: str
    ) -> UpdateCodeOfConductViolationResponse:
        """Update a violation.

        Args:
            coc_id: ID of the Code of Conduct
            policy_id: ID of the policy
            violation_id: ID of the violation
            violation: New violation text

        Returns:
            UpdateCodeOfConductViolationResponse with updated details
        """
        request = UpdateCodeOfConductViolationRequest(
            id=violation_id, coc_id=coc_id, policy_id=policy_id, violation=violation
        )
        response = await self._client.post(
            f"{self.prefix}/{coc_id}/{policy_id}/{violation_id}/update",
            json=request.model_dump(),
        )
        return UpdateCodeOfConductViolationResponse.model_validate(response)

    async def delete_violation(
        self, coc_id: str, policy_id: str, violation_id: str
    ) -> bool:
        """Delete a violation.

        Args:
            coc_id: ID of the Code of Conduct
            policy_id: ID of the policy
            violation_id: ID of the violation

        Returns:
            True if successful
        """
        response = await self._client.delete(
            f"{self.prefix}/{coc_id}/{policy_id}/{violation_id}"
        )
        return response
