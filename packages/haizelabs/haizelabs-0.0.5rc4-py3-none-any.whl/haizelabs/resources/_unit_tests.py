from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List

from haizelabs._resource import AsyncAPIResource, SyncAPIResource
from haizelabs.models.tests import (
    CancelTestResponse,
    CreateTestResponse,
    CreateUnitTestAPIRequest,
    GetUnitTestResponse,
    JudgeID,
    PromptTemplateReference,
    PromptTemplateType,
    StartTestResponse,
    UnitTestResponse,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass

UNIT_TEST_URL = "https://platform.haizelabs.com/app/unit-tests/{test_id}"


class SyncUnitTests(SyncAPIResource):
    prefix: str = "/tests/unit"

    def create(
        self,
        name: str,
        system_id: str,
        judge_ids: List[str],
        prompt_template: str,
        dataset_id: str,
        dataset_version: int,
    ) -> CreateTestResponse:
        """Create a unit test.

        Args:
            name: Name of the unit test
            system_id: ID of the AI system to test
            judge_ids: List of judge IDs to use for evaluation
            prompt_template: The prompt template string
            dataset_id: ID of the dataset to use
            dataset_version: Version of the dataset

        Returns:
            CreateTestResponse with the created test ID
        """
        request = CreateUnitTestAPIRequest(
            name=name,
            system_id=system_id,
            judge_ids=[JudgeID(id=judge_id) for judge_id in judge_ids],
            prompt_template=PromptTemplateReference(
                template=prompt_template,
                prompt_template_type=PromptTemplateType.AI_SYSTEM,
            ),
            dataset_id=dataset_id,
            dataset_version=dataset_version,
        )
        response = self._client.post(
            f"{self.prefix}/create", json=request.model_dump(exclude_none=True)
        )
        return CreateTestResponse.model_validate(response)

    def get(self, test_id: str) -> UnitTestResponse:
        """Get a unit test by ID.

        Args:
            test_id: The test ID

        Returns:
            UnitTestResponse with the test details
        """
        response = self._client.get(f"{self.prefix}/{test_id}")
        get_response = GetUnitTestResponse.model_validate(response)
        return get_response.test

    def start(self, test_id: str) -> StartTestResponse:
        """Start a unit test.

        Args:
            test_id: The test ID to start

        Returns:
            StartTestResponse with the result
        """
        response = self._client.post(f"{self.prefix}/{test_id}/start")
        validated_response = StartTestResponse.model_validate(response)
        if validated_response.success:
            logger.info(
                f"Started test {test_id}, view at {UNIT_TEST_URL.format(test_id=test_id)}"
            )
        else:
            logger.error(f"Failed to start test {test_id}")
        return validated_response

    def cancel(self, test_id: str) -> CancelTestResponse:
        """Cancel a unit test.

        Args:
            test_id: The test ID to cancel

        Returns:
            CancelTestResponse with the result
        """
        response = self._client.post(f"{self.prefix}/{test_id}/cancel")
        return CancelTestResponse.model_validate(response)


class AsyncUnitTests(AsyncAPIResource):
    prefix: str = "/tests/unit"

    async def create(
        self,
        name: str,
        system_id: str,
        judge_ids: List[str],
        prompt_template: str,
        dataset_id: str,
        dataset_version: int,
    ) -> CreateTestResponse:
        """Create a unit test.

        Args:
            name: Name of the unit test
            system_id: ID of the AI system to test
            judge_ids: List of judge IDs to use for evaluation
            prompt_template: The prompt template string
            dataset_id: ID of the dataset to use
            dataset_version: Version of the dataset

        Returns:
            CreateTestResponse with the created test ID
        """
        request = CreateUnitTestAPIRequest(
            name=name,
            system_id=system_id,
            judge_ids=[JudgeID(id=judge_id) for judge_id in judge_ids],
            prompt_template=PromptTemplateReference(
                template=prompt_template,
                prompt_template_type=PromptTemplateType.AI_SYSTEM,
            ),
            dataset_id=dataset_id,
            dataset_version=dataset_version,
        )
        response = await self._client.post(
            f"{self.prefix}/create", json=request.model_dump(exclude_none=True)
        )
        return CreateTestResponse.model_validate(response)

    async def get(self, test_id: str) -> UnitTestResponse:
        """Get a unit test by ID.

        Args:
            test_id: The test ID

        Returns:
            UnitTestResponse with the test details
        """
        response = await self._client.get(f"{self.prefix}/{test_id}")
        get_response = GetUnitTestResponse.model_validate(response)
        return get_response.test

    async def start(self, test_id: str) -> StartTestResponse:
        """Start a unit test.

        Args:
            test_id: The test ID to start

        Returns:
            StartTestResponse with the result
        """
        response = await self._client.post(f"{self.prefix}/{test_id}/start")
        validated_response = StartTestResponse.model_validate(response)
        if validated_response.success:
            logger.info(
                f"Started test {test_id}, view at {UNIT_TEST_URL.format(test_id=test_id)}"
            )
        else:
            logger.error(f"Failed to start test {test_id}")
        return validated_response

    async def cancel(self, test_id: str) -> CancelTestResponse:
        """Cancel a unit test.

        Args:
            test_id: The test ID to cancel

        Returns:
            CancelTestResponse with the result
        """
        response = await self._client.post(f"{self.prefix}/{test_id}/cancel")
        return CancelTestResponse.model_validate(response)
