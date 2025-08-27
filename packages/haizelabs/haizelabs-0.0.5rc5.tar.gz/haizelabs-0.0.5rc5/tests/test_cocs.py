import pytest

from haizelabs import AsyncHaize, Haize


@pytest.mark.asyncio
async def test_code_of_conduct_create(async_haize: AsyncHaize, request_vcr) -> None:
    """Test creating code of conduct"""
    with request_vcr.use_cassette("create_coc.yaml"):
        coc = await async_haize.code_of_conduct.create(
            name="test_coc", description="Test code of conduct for AI safety"
        )
        assert coc.coc_id is not None


@pytest.mark.asyncio
async def test_code_of_conduct_get(async_haize: AsyncHaize, request_vcr) -> None:
    """Test getting code of conduct"""
    with request_vcr.use_cassette("get_coc.yaml"):
        created_coc = await async_haize.code_of_conduct.create(
            name="test_coc_get", description="Test code of conduct"
        )
        coc = await async_haize.code_of_conduct.get(created_coc.coc_id)
        assert coc.coc.id == created_coc.coc_id
        assert coc.coc.name == "test_coc_get"
        assert coc.coc.description == "Test code of conduct"


@pytest.mark.asyncio
async def test_code_of_conduct_policies(
    async_haize: AsyncHaize, coc, request_vcr
) -> None:
    """Test creating and getting policies"""
    with request_vcr.use_cassette("create_coc_policies.yaml"):
        policy = await async_haize.code_of_conduct.create_policy(
            coc_id=coc.coc_id, policy="Do not generate harmful content"
        )

        assert policy.policy_id is not None
        assert policy.coc_id == coc.coc_id

        policies = await async_haize.code_of_conduct.get_policies(coc.coc_id)
        assert len(policies.policies) >= 1

        retrieved_policy = await async_haize.code_of_conduct.get_policy(
            coc_id=coc.coc_id, policy_id=policy.policy_id
        )
        assert retrieved_policy.policy.id == policy.policy_id
        assert retrieved_policy.policy.policy == "Do not generate harmful content"


@pytest.mark.asyncio
async def test_code_of_conduct_violations(
    async_haize: AsyncHaize, coc, policy, request_vcr
) -> None:
    """Test creating and getting violations"""
    with request_vcr.use_cassette("create_coc_violations.yaml"):
        violation = await async_haize.code_of_conduct.create_violation(
            coc_id=coc.coc_id,
            policy_id=policy.policy_id,
            violation="Generated instructions for dangerous activity",
        )
        assert violation.violation_id is not None
        assert violation.policy_id == policy.policy_id
        assert violation.coc_id == coc.coc_id
        retrieved_violation = await async_haize.code_of_conduct.get_violation(
            coc_id=coc.coc_id,
            policy_id=policy.policy_id,
            violation_id=violation.violation_id,
        )
        assert retrieved_violation.violation.id == violation.violation_id
        assert (
            retrieved_violation.violation.violation
            == "Generated instructions for dangerous activity"
        )
        all_violations = await async_haize.code_of_conduct.get_violations(coc.coc_id)
        assert len(all_violations.violations) >= 1


def test_sync_code_of_conduct_create(haize: Haize, request_vcr) -> None:
    """Test sync version of code of conduct creation"""
    with request_vcr.use_cassette("create_coc.yaml"):
        coc = haize.code_of_conduct.create(
            name="test_coc",
            description="Test code of conduct for AI safety",
        )
        assert coc.coc_id is not None


def test_sync_code_of_conduct_get(haize: Haize, request_vcr) -> None:
    """Test sync version of getting code of conduct"""
    with request_vcr.use_cassette("get_coc.yaml"):
        created_coc = haize.code_of_conduct.create(
            name="test_coc_get", description="Test code of conduct"
        )
        coc = haize.code_of_conduct.get(created_coc.coc_id)
        assert coc.coc.id == created_coc.coc_id
        assert coc.coc.name == "test_coc_get"
        assert coc.coc.description == "Test code of conduct"


@pytest.mark.asyncio
async def test_code_of_conduct_update(async_haize: AsyncHaize, request_vcr) -> None:
    """Test updating a code of conduct"""
    with request_vcr.use_cassette("update_coc.yaml"):
        created_coc = await async_haize.code_of_conduct.create(
            name="test_coc_update", description="Original description"
        )

        updated_coc = await async_haize.code_of_conduct.update(
            coc_id=created_coc.coc_id,
            name="test_coc_updated",
            description="Updated description",
        )

        assert updated_coc.coc.name == "test_coc_updated"
        assert updated_coc.coc.description == "Updated description"


@pytest.mark.asyncio
async def test_code_of_conduct_delete(async_haize: AsyncHaize, request_vcr) -> None:
    """Test deleting a code of conduct"""
    with request_vcr.use_cassette("delete_coc.yaml"):
        created_coc = await async_haize.code_of_conduct.create(
            name="test_coc_delete", description="To be deleted"
        )
        result = await async_haize.code_of_conduct.delete(created_coc.coc_id)
        assert result is True


@pytest.mark.asyncio
async def test_code_of_conduct_policy_update(
    async_haize: AsyncHaize, coc, request_vcr
) -> None:
    """Test updating a policy"""
    with request_vcr.use_cassette("update_coc_policy.yaml"):
        policy = await async_haize.code_of_conduct.create_policy(
            coc_id=coc.coc_id, policy="Original policy text"
        )
        updated_policy = await async_haize.code_of_conduct.update_policy(
            coc_id=coc.coc_id, policy_id=policy.policy_id, policy="Updated policy text"
        )
        assert updated_policy.policy.policy == "Updated policy text"


@pytest.mark.asyncio
async def test_code_of_conduct_policy_delete(
    async_haize: AsyncHaize, coc, request_vcr
) -> None:
    """Test deleting a policy"""
    with request_vcr.use_cassette("delete_coc_policy.yaml"):
        policy = await async_haize.code_of_conduct.create_policy(
            coc_id=coc.coc_id, policy="Policy to delete"
        )
        result = await async_haize.code_of_conduct.delete_policy(
            coc_id=coc.coc_id, policy_id=policy.policy_id
        )
        assert result is True


@pytest.mark.asyncio
async def test_code_of_conduct_violations_batch(
    async_haize: AsyncHaize, coc, policy, request_vcr
) -> None:
    """Test creating multiple violations at once"""
    with request_vcr.use_cassette("create_coc_violations_batch.yaml"):
        from haizelabs.models.code_of_conduct import CreateCodeOfConductViolationRequest

        violations = [
            CreateCodeOfConductViolationRequest(
                violation="First violation",
                policy_id=policy.policy_id,
                coc_id=coc.coc_id,
            ),
            CreateCodeOfConductViolationRequest(
                violation="Second violation",
                policy_id=policy.policy_id,
                coc_id=coc.coc_id,
            ),
        ]

        result = await async_haize.code_of_conduct.create_violations(
            coc_id=coc.coc_id, policy_id=policy.policy_id, violations=violations
        )
        assert len(result.violations) == 2


@pytest.mark.asyncio
async def test_code_of_conduct_policy_violations(
    async_haize: AsyncHaize, coc, policy, request_vcr
) -> None:
    """Test getting violations for a specific policy"""
    with request_vcr.use_cassette("get_policy_violations.yaml"):
        violation = await async_haize.code_of_conduct.create_violation(
            coc_id=coc.coc_id,
            policy_id=policy.policy_id,
            violation="Test violation for policy",
        )
        violations = await async_haize.code_of_conduct.get_policy_violations(
            coc_id=coc.coc_id, policy_id=policy.policy_id
        )
        assert len(violations.violations) >= 1
        assert any(v.id == violation.violation_id for v in violations.violations)


@pytest.mark.asyncio
async def test_code_of_conduct_violation_update(
    async_haize: AsyncHaize, coc, policy, request_vcr
) -> None:
    """Test updating a violation"""
    with request_vcr.use_cassette("update_coc_violation.yaml"):
        violation = await async_haize.code_of_conduct.create_violation(
            coc_id=coc.coc_id,
            policy_id=policy.policy_id,
            violation="Original violation text",
        )
        updated = await async_haize.code_of_conduct.update_violation(
            coc_id=coc.coc_id,
            policy_id=policy.policy_id,
            violation_id=violation.violation_id,
            violation="Updated violation text",
        )

        assert updated.violation.violation == "Updated violation text"


@pytest.mark.asyncio
async def test_code_of_conduct_violation_delete(
    async_haize: AsyncHaize, coc, policy, request_vcr
) -> None:
    """Test deleting a violation"""
    with request_vcr.use_cassette("delete_coc_violation.yaml"):
        violation = await async_haize.code_of_conduct.create_violation(
            coc_id=coc.coc_id,
            policy_id=policy.policy_id,
            violation="Violation to delete",
        )
        result = await async_haize.code_of_conduct.delete_violation(
            coc_id=coc.coc_id,
            policy_id=policy.policy_id,
            violation_id=violation.violation_id,
        )
        assert result is True
