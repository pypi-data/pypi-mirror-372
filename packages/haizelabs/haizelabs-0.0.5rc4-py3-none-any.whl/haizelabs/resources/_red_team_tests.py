from __future__ import annotations

import asyncio
import logging
import time
from typing import List

from haizelabs._resource import AsyncAPIResource, SyncAPIResource
from haizelabs.models.behaviors import (
    BehaviorType,
    CodeOfConductBehaviorRequest,
    CustomBehaviorRequest,
)
from haizelabs.models.datasets import UpsertDatasetResponse
from haizelabs.models.judges import JudgeID
from haizelabs.models.tests import (
    CancelTestResponse,
    CreateRedTeamTestRequest,
    CreateTestResponse,
    ExportRedTeamDatasetRequest,
    GetRedTeamTestResponse,
    GetRedTeamTestResultsResponse,
    JobStatusResponse,
    PlatformJobStatus,
    RedTeamTestBehaviorMetrics,
    RedTeamTestMetricsResponse,
    StartTestResponse,
    TestStatus,
)

logger = logging.getLogger(__name__)

RED_TEAM_TEST_URL = "https://platform.haizelabs.com/app/red-team-tests/{test_id}"
RED_TEAM_TEST_REPORT_URL = RED_TEAM_TEST_URL + "/report"
DATASET_URL = "https://platform.haizelabs.com/app/datasets/{dataset_id}"


class SyncRedTeamTests(SyncAPIResource):
    prefix: str = "/tests/red_team"

    def run(
        self,
        name: str,
        system_id: str,
        judge_ids: List[str],
        custom_behaviors: List[str] | None = None,
        code_of_conduct_behaviors: List[CodeOfConductBehaviorRequest] | None = None,
        creativity: int = 5,
        attack_system_id: str | None = None,
    ) -> "SyncRedTeamTest":
        """Create and start a red team test.

        Args:
            name: Name of the red team test
            system_id: ID of the AI system to test
            judge_ids: List of judge IDs to use for evaluation
            custom_behaviors: List of custom behavior strings to test
            code_of_conduct_behaviors: List of CodeOfConductBehaviorRequest objects
            creativity: Creativity level (1-10)
            attack_system_id: Optional attack system ID

        Returns:
            SyncRedTeamTest wrapper for the running test
        """
        test = self.create(
            name,
            system_id,
            judge_ids,
            custom_behaviors,
            code_of_conduct_behaviors,
            creativity,
            attack_system_id,
        )
        self.start(test.test_id)
        test_response = self.get(test.test_id)
        return SyncRedTeamTest(self._client, test_response)

    def create(
        self,
        name: str,
        system_id: str,
        judge_ids: List[str],
        custom_behaviors: List[str] | None = None,
        code_of_conduct_behaviors: List[CodeOfConductBehaviorRequest] | None = None,
        creativity: int = 5,
        attack_system_id: str | None = None,
    ) -> CreateTestResponse:
        """Create a red team test.

        Args:
            name: Name of the red team test
            system_id: ID of the AI system to test
            judge_ids: List of judge IDs to use for evaluation
            custom_behaviors: List of custom behavior strings to test
            code_of_conduct_behaviors: List of CodeOfConductBehaviorRequest objects
            creativity: Creativity level (1-10)
            attack_system_id: Optional attack system ID

        Returns:
            CreateTestResponse with the created test ID
        """
        behavior_requests = []

        if custom_behaviors:
            behavior_requests.extend(
                [
                    CustomBehaviorRequest(behavior=behavior, type=BehaviorType.CUSTOM)
                    for behavior in custom_behaviors
                ]
            )
        if code_of_conduct_behaviors:
            behavior_requests.extend(code_of_conduct_behaviors)

        if not behavior_requests:
            raise ValueError(
                "At least one behavior must be provided (custom or code of conduct)"
            )

        request = CreateRedTeamTestRequest(
            name=name,
            system_id=system_id,
            judge_ids=[JudgeID(id=judge_id) for judge_id in judge_ids],
            behaviors=behavior_requests,
            creativity=creativity,
            attack_system_id=attack_system_id,
        )
        response = self._client.post(
            f"{self.prefix}/create", json=request.model_dump(exclude_none=True)
        )
        return CreateTestResponse.model_validate(response)

    def get(self, test_id: str) -> GetRedTeamTestResponse:
        """Get a red team test by ID.

        Args:
            test_id: The test ID

        Returns:
            GetRedTeamTestResponse with the test details
        """
        response = self._client.get(f"{self.prefix}/{test_id}")
        return GetRedTeamTestResponse.model_validate(response)

    def start(self, test_id: str) -> StartTestResponse:
        """Start a red team test.

        Args:
            test_id: ID of the test to start

        Returns:
            StartTestResponse with success status
        """
        response = self._client.post(f"{self.prefix}/{test_id}/start")
        validated_response = StartTestResponse.model_validate(response)
        if validated_response.success:
            logger.info(
                f"Started test {test_id}, see results at {RED_TEAM_TEST_URL.format(test_id=test_id)}"
            )
        else:
            logger.error("Failed to start test %s", test_id)
        return validated_response

    def cancel(self, test_id: str) -> CancelTestResponse:
        """Cancel a red team test.

        Args:
            test_id: ID of the test to cancel

        Returns:
            CancelTestResponse with success status
        """
        response = self._client.post(f"{self.prefix}/{test_id}/cancel")
        return CancelTestResponse.model_validate(response)

    def results(self, test_id: str) -> GetRedTeamTestResultsResponse:
        """Get the results of a red team test by ID.

        Args:
            test_id: The test ID

        Returns:
            GetRedTeamTestResultsResponse with the test results
        """
        response = self._client.get(f"{self.prefix}/{test_id}/results")
        return GetRedTeamTestResultsResponse.model_validate(response)

    def metrics(self, test_id: str) -> RedTeamTestMetricsResponse:
        """Get the metrics of a red team test by ID.

        Args:
            test_id: The test ID

        Returns:
            RedTeamTestMetricsResponse with the test metrics
        """
        response = self._client.get(f"{self.prefix}/{test_id}/metrics")
        return RedTeamTestMetricsResponse.model_validate(response)

    def behavior_metrics(
        self, test_id: str, behavior: str
    ) -> RedTeamTestBehaviorMetrics:
        """Get behavior-level metrics for a red team test.

        Args:
            test_id: The test ID
            behavior: The behavior to get metrics for

        Returns:
            RedTeamTestBehaviorMetrics with behavior-level metrics
        """
        response = self._client.get(
            f"{self.prefix}/{test_id}/metrics/behavior", params={"behavior": behavior}
        )
        return RedTeamTestBehaviorMetrics.model_validate(response)

    def export_results_as_dataset(
        self, test_id: str, name: str, description: str, minimum_score: float
    ) -> UpsertDatasetResponse:
        """Export the test as a dataset.

        Args:
            test_id: ID of the test to export
            name: Name for the exported dataset
            description: Description of the dataset
            minimum_score: Minimum score threshold for including results

        Returns:
            UpsertDatasetResponse with created dataset ID
        """
        response = self._client.post(
            f"{self.prefix}/{test_id}/export_dataset",
            json=ExportRedTeamDatasetRequest(
                dataset_name=name,
                dataset_description=description,
                minimum_score=minimum_score,
            ).model_dump(exclude_none=True),
        )
        response = UpsertDatasetResponse.model_validate(response)
        logger.debug(
            "Exported test dataset for red team test. View at: https://platform.haizelabs.com/app/datasets/%s",
            response.dataset_id,
        )
        return response

    def generate_report(self, test_id: str) -> str:
        """Generate a report for a red team test.
        Args:
            test_id: ID of the test for report generation
        Returns:
            Job ID for the report generation job
        """
        return self._client.post(f"{self.prefix}/{test_id}/generate_report")

    def get_report_job_status(self, job_id: str) -> JobStatusResponse:
        """Get the status of the report generation job.
        Args:
            job_id: ID of the report generation job
        Returns:
            JobStatusResponse with the current status
        """
        response = self._client.get(f"{self.prefix}/{job_id}/report_status")
        return JobStatusResponse.model_validate(response)


class AsyncRedTeamTests(AsyncAPIResource):
    prefix: str = "/tests/red_team"

    async def run(
        self,
        name: str,
        system_id: str,
        judge_ids: List[str],
        custom_behaviors: List[str] | None = None,
        code_of_conduct_behaviors: List[CodeOfConductBehaviorRequest] | None = None,
        creativity: int = 5,
        attack_system_id: str | None = None,
    ) -> AsyncRedTeamTest:
        """Create and start a red team test.

        Args:
            name: Name of the red team test
            system_id: ID of the AI system to test
            judge_ids: List of judge IDs to use for evaluation
            custom_behaviors: List of custom behavior strings to test
            code_of_conduct_behaviors: List of CodeOfConductBehaviorRequest objects
            creativity: Creativity level (1-10)
            attack_system_id: Optional attack system ID

        Returns:
            AsyncRedTeamTest wrapper for the running test
        """
        logger.debug("Creating red team test '%s' for system '%s'", name, system_id)
        test = await self.create(
            name,
            system_id,
            judge_ids,
            custom_behaviors,
            code_of_conduct_behaviors,
            creativity,
            attack_system_id,
        )
        logger.debug("Starting run for red team test '%s'", test.test_id)
        await self.start(test.test_id)
        test_response = await self.get(test.test_id)
        return AsyncRedTeamTest(self._client, test_response)

    async def create(
        self,
        name: str,
        system_id: str,
        judge_ids: List[str],
        custom_behaviors: List[str] | None = None,
        code_of_conduct_behaviors: List[CodeOfConductBehaviorRequest] | None = None,
        creativity: int = 5,
        attack_system_id: str | None = None,
    ) -> CreateTestResponse:
        """Create a red team test.

        Args:
            name: Name of the red team test
            system_id: ID of the AI system to test
            judge_ids: List of judge IDs to use for evaluation
            custom_behaviors: List of custom behavior strings to test
            code_of_conduct_behaviors: List of CodeOfConductBehaviorRequest objects
            creativity: Creativity level (1-10)
            attack_system_id: Optional attack system ID

        Returns:
            CreateTestResponse with the created test ID
        """
        behavior_requests = []

        if custom_behaviors:
            behavior_requests.extend(
                [
                    CustomBehaviorRequest(behavior=behavior, type=BehaviorType.CUSTOM)
                    for behavior in custom_behaviors
                ]
            )

        if code_of_conduct_behaviors:
            behavior_requests.extend(code_of_conduct_behaviors)

        if not behavior_requests:
            raise ValueError(
                "At least one behavior must be provided (custom or code of conduct)"
            )

        request = CreateRedTeamTestRequest(
            name=name,
            system_id=system_id,
            judge_ids=[JudgeID(id=judge_id) for judge_id in judge_ids],
            behaviors=behavior_requests,
            creativity=creativity,
            attack_system_id=attack_system_id,
        )
        response = await self._client.post(
            f"{self.prefix}/create", json=request.model_dump(exclude_none=True)
        )
        return CreateTestResponse.model_validate(response)

    async def get(self, test_id: str) -> GetRedTeamTestResponse:
        """Get a red team test by ID.

        Args:
            test_id: The test ID

        Returns:
            GetRedTeamTestResponse with the test details
        """
        response = await self._client.get(f"{self.prefix}/{test_id}")
        return GetRedTeamTestResponse.model_validate(response)

    async def start(self, test_id: str) -> StartTestResponse:
        """Start a red team test.

        Args:
            test_id: ID of the test to start

        Returns:
            StartTestResponse with success status
        """
        response = await self._client.post(f"{self.prefix}/{test_id}/start")
        validated_response = StartTestResponse.model_validate(response)
        if validated_response.success:
            logger.info(
                f"Started test {test_id}, see results at {RED_TEAM_TEST_URL.format(test_id=test_id)}"
            )
        else:
            logger.error("Failed to start test %s", test_id)
        return validated_response

    async def cancel(self, test_id: str) -> CancelTestResponse:
        """Cancel a red team test.

        Args:
            test_id: ID of the test to cancel

        Returns:
            CancelTestResponse with success status
        """
        response = await self._client.post(f"{self.prefix}/{test_id}/cancel")
        return CancelTestResponse.model_validate(response)

    async def results(self, test_id: str) -> GetRedTeamTestResultsResponse:
        """Get the results of a red team test.

        Args:
            test_id: The test ID

        Returns:
            GetRedTeamTestResultsResponse with the test results
        """
        response = await self._client.get(f"{self.prefix}/{test_id}/results")
        return GetRedTeamTestResultsResponse.model_validate(response)

    async def metrics(self, test_id: str) -> RedTeamTestMetricsResponse:
        """Get the metrics of a red team test.

        Args:
            test_id: The test ID

        Returns:
            RedTeamTestMetricsResponse with the test metrics
        """
        response = await self._client.get(f"{self.prefix}/{test_id}/metrics")
        return RedTeamTestMetricsResponse.model_validate(response)

    async def behavior_metrics(
        self, test_id: str, behavior: str
    ) -> RedTeamTestBehaviorMetrics:
        """Get behavior-level metrics for a red team test.

        Args:
            test_id: The test ID
            behavior: The behavior to get metrics for

        Returns:
            RedTeamTestBehaviorMetrics with behavior-level metrics
        """
        response = await self._client.get(
            f"{self.prefix}/{test_id}/metrics/behavior", params={"behavior": behavior}
        )
        return RedTeamTestBehaviorMetrics.model_validate(response)

    async def export_results_as_dataset(
        self, test_id: str, name: str, description: str, minimum_score: float
    ) -> UpsertDatasetResponse:
        """Export the test as a dataset.

        Args:
            test_id: ID of the test to export
            name: Name for the exported dataset
            description: Description of the dataset
            minimum_score: Minimum score threshold for including results

        Returns:
            UpsertDatasetResponse with created dataset ID
        """
        response = await self._client.post(
            f"{self.prefix}/{test_id}/export_dataset",
            json=ExportRedTeamDatasetRequest(
                dataset_name=name,
                dataset_description=description,
                minimum_score=minimum_score,
            ).model_dump(exclude_none=True),
        )
        response = UpsertDatasetResponse.model_validate(response)
        logger.debug(
            f"Exported test dataset for red team test. View at: {DATASET_URL.format(dataset_id=response.dataset_id)}"
        )
        return response

    async def generate_report(self, test_id: str) -> str:
        """Generate a report for a red team test.

        Args:
            test_id: ID of the test for report generation

        Returns:
            Job ID for the report generation job
        """
        return await self._client.post(f"{self.prefix}/{test_id}/generate_report")

    async def get_report_job_status(self, job_id: str) -> JobStatusResponse:
        """Get the status of the report generation job.

        Args:
            job_id: ID of the report generation job

        Returns:
            JobStatusResponse with the current status
        """
        response = await self._client.get(f"{self.prefix}/{job_id}/report_status")
        return JobStatusResponse.model_validate(response)


class AsyncRedTeamTest:
    """Convenience wrapper for a red team test"""

    def __init__(self, client, test_data: GetRedTeamTestResponse):
        self._test = test_data
        self._client = client
        self._update_from_response(test_data)

    def _update_from_response(self, test_data: GetRedTeamTestResponse):
        self.id = test_data.test.id
        self.name = test_data.test.name
        self.status = test_data.test.status
        self.system_id = test_data.test.system_id
        self.attack_system_id = test_data.test.attack_system_id
        self.judge_ids = test_data.test.judge_ids
        self.started_at = test_data.test.started_at
        self.completed_at = test_data.test.completed_at
        self.cancelled_at = test_data.test.cancelled_at
        self.behaviors = test_data.test.behaviors
        self.creativity = test_data.test.creativity
        self.creator_id = test_data.test.creator_id
        self.span_id = test_data.test.span_id
        self.trace_id = test_data.test.trace_id

    async def poll(self, interval: int = 10, timeout: int = 3600) -> "AsyncRedTeamTest":
        """Poll until test completes or times out

        Args:
            interval: Seconds between status checks
            timeout: Maximum seconds to wait before timing out

        Returns:
            Self with updated status
        """
        start_time = time.time()
        logger.debug(
            "Polling red team test '%s' (status=%s, interval=%ds, timeout=%ds)",
            self.id,
            self.status.value,
            interval,
            timeout,
        )

        while self.status not in [
            TestStatus.SUCCEEDED,
            TestStatus.FAILED,
            TestStatus.CANCELLED,
            TestStatus.PARTIAL_SUCCESS,
        ]:
            if time.time() - start_time > timeout:
                raise TimeoutError(
                    f"Red team test {self.id} timed out after {timeout} seconds"
                )

            response = await self._client.get(f"/tests/red_team/{self.id}")
            test_response = GetRedTeamTestResponse.model_validate(response)
            self._update_from_response(test_response)
            logger.debug(
                "Polling red team test '%s' (status=%s, interval=%ds, timeout=%ds)",
                self.id,
                self.status.value,
                interval,
                timeout,
            )
            if self.status in [TestStatus.PENDING, TestStatus.RUNNING]:
                await asyncio.sleep(interval)

        logger.debug(
            "Red team test '%s' completed with status: %s",
            self.id,
            self.status.value,
        )
        return self

    async def cancel(self) -> bool:
        """Cancel the running test"""
        logger.debug("Cancelling red team test '%s'", self.id)
        response = await self._client.post(f"/tests/red_team/{self.id}/cancel")
        cancel_response = CancelTestResponse.model_validate(response)
        if cancel_response.success:
            self.status = TestStatus.CANCELLED
            logger.debug("Successfully cancelled red team test '%s'", self.id)
        else:
            logger.warning("Failed to cancel red team test '%s'", self.id)
        return cancel_response.success

    async def results(self) -> GetRedTeamTestResultsResponse:
        """Get detailed results (only available after completion)"""
        if self.status not in [
            TestStatus.SUCCEEDED,
            TestStatus.FAILED,
            TestStatus.PARTIAL_SUCCESS,
        ]:
            raise ValueError(
                f"Results not available - test status is '{self.status.value}'"
            )

        logger.debug("Fetching results for red team test '%s'", self.id)
        response = await self._client.get(f"/tests/red_team/{self.id}/results")
        results = GetRedTeamTestResultsResponse.model_validate(response)
        logger.debug(
            "Retrieved %d results for red team test '%s'",
            len(results.results),
            self.id,
        )
        return results

    async def metrics(self) -> RedTeamTestMetricsResponse:
        """Get the metrics of the red team test"""
        response = await self._client.get(f"/tests/red_team/{self.id}/metrics")
        return RedTeamTestMetricsResponse.model_validate(response)

    async def export_results_as_dataset(
        self, name: str, description: str, minimum_score: float
    ) -> UpsertDatasetResponse:
        """Export test results as a dataset"""
        request = ExportRedTeamDatasetRequest(
            dataset_name=name,
            dataset_description=description,
            minimum_score=minimum_score,
        )
        response = await self._client.post(
            f"/tests/red_team/{self.id}/export_dataset",
            json=request.model_dump(),
        )
        response = UpsertDatasetResponse.model_validate(response)
        logger.info(
            f"Exported test dataset for red team test. View at: {DATASET_URL.format(dataset_id=response.dataset_id)}"
        )
        return response

    async def generate_report(self) -> str:
        """Generate a PDF report for the test.

        Returns:
            Job ID for the report generation job
        """
        return await self._client.post(f"/tests/red_team/{self.id}/generate_report")

    async def get_report_job_status(self, job_id: str) -> JobStatusResponse:
        """Get the status of the report generation job."""
        response = await self._client.get(f"/tests/red_team/{job_id}/report_status")
        status = JobStatusResponse.model_validate(response)
        if status.status == PlatformJobStatus.SUCCEEDED:
            logger.info(
                f"Report generation job {job_id} completed, see at {RED_TEAM_TEST_REPORT_URL.format(test_id=self.id)}"
            )
        return status


class SyncRedTeamTest:
    """Convenience wrapper for a sync red team test"""

    def __init__(self, client, test_data: GetRedTeamTestResponse):
        self._test = test_data
        self._client = client
        self._update_from_response(test_data)

    def _update_from_response(self, test_data: GetRedTeamTestResponse):
        self.id = test_data.test.id
        self.name = test_data.test.name
        self.status = test_data.test.status
        self.system_id = test_data.test.system_id
        self.attack_system_id = test_data.test.attack_system_id
        self.judge_ids = test_data.test.judge_ids
        self.started_at = test_data.test.started_at
        self.completed_at = test_data.test.completed_at
        self.cancelled_at = test_data.test.cancelled_at
        self.behaviors = test_data.test.behaviors
        self.creativity = test_data.test.creativity
        self.creator_id = test_data.test.creator_id
        self.span_id = test_data.test.span_id
        self.trace_id = test_data.test.trace_id

    def poll(self, interval: int = 10, timeout: int = 3600) -> "SyncRedTeamTest":
        """Poll until test completes or times out

        Args:
            interval: Seconds between status checks
            timeout: Maximum seconds to wait before timing out

        Returns:
            Self with updated status
        """
        start_time = time.time()
        logger.debug(
            "Polling red team test '%s' (status=%s, interval=%ds, timeout=%ds)",
            self.id,
            self.status.value,
            interval,
            timeout,
        )

        while self.status not in [
            TestStatus.SUCCEEDED,
            TestStatus.FAILED,
            TestStatus.CANCELLED,
            TestStatus.PARTIAL_SUCCESS,
        ]:
            if time.time() - start_time > timeout:
                raise TimeoutError(
                    f"Red team test {self.id} timed out after {timeout} seconds"
                )

            response = self._client.get(f"/tests/red_team/{self.id}")
            test_response = GetRedTeamTestResponse.model_validate(response)
            self._update_from_response(test_response)
            logger.debug(
                "Polling red team test '%s' (status=%s, interval=%ds, timeout=%ds)",
                self.id,
                self.status.value,
                interval,
                timeout,
            )
            if self.status in [TestStatus.PENDING, TestStatus.RUNNING]:
                time.sleep(interval)

        logger.debug(
            "Red team test '%s' completed with status: %s",
            self.id,
            self.status.value,
        )
        return self

    def cancel(self) -> bool:
        """Cancel the running test"""
        logger.debug("Cancelling red team test '%s'", self.id)
        response = self._client.post(f"/tests/red_team/{self.id}/cancel")
        cancel_response = CancelTestResponse.model_validate(response)
        if cancel_response.success:
            self.status = TestStatus.CANCELLED
            logger.debug("Successfully cancelled red team test '%s'", self.id)
        else:
            logger.warning("Failed to cancel red team test '%s'", self.id)
        return cancel_response.success

    def results(self) -> GetRedTeamTestResultsResponse:
        """Get detailed results (only available after completion)"""
        if self.status not in [
            TestStatus.SUCCEEDED,
            TestStatus.FAILED,
            TestStatus.PARTIAL_SUCCESS,
        ]:
            raise ValueError(
                f"Results not available - test status is '{self.status.value}'"
            )

        logger.debug("Fetching results for red team test '%s'", self.id)
        response = self._client.get(f"/tests/red_team/{self.id}/results")
        results = GetRedTeamTestResultsResponse.model_validate(response)
        logger.debug(
            "Retrieved %d results for red team test '%s'",
            len(results.results),
            self.id,
        )
        return results

    def metrics(self) -> RedTeamTestMetricsResponse:
        """Get the metrics of the red team test"""
        response = self._client.get(f"/tests/red_team/{self.id}/metrics")
        return RedTeamTestMetricsResponse.model_validate(response)

    def export_results_as_dataset(
        self, name: str, description: str, minimum_score: float
    ) -> UpsertDatasetResponse:
        """Export test results as a dataset"""
        request = ExportRedTeamDatasetRequest(
            dataset_name=name,
            dataset_description=description,
            minimum_score=minimum_score,
        )
        response = self._client.post(
            f"/tests/red_team/{self.id}/export_dataset",
            json=request.model_dump(),
        )
        response = UpsertDatasetResponse.model_validate(response)
        logger.info(
            f"Exported test dataset for red team test. View at: {DATASET_URL.format(dataset_id=response.dataset_id)}"
        )
        return response

    def generate_report(self) -> str:
        """Generate a PDF report for the test.

        Returns:
            Job ID for the report generation job
        """
        return self._client.post(f"/tests/red_team/{self.id}/generate_report")

    def get_report_job_status(self, job_id: str) -> JobStatusResponse:
        """Get the status of the report generation job."""
        response = self._client.get(f"/tests/red_team/{job_id}/report_status")
        status = JobStatusResponse.model_validate(response)
        if status.status == PlatformJobStatus.SUCCEEDED:
            logger.info(
                f"Report generation job {job_id} completed, see at {RED_TEAM_TEST_REPORT_URL.format(test_id=self.id)}"
            )
        return status
