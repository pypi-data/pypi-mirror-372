"""Tests for custom exception handling in the SDK."""

import json

import pytest
from httpx import Response

from haizelabs import (
    AsyncHaize,
    BadRequestError,
    ForbiddenError,
    Haize,
    InternalServerError,
    NotFoundError,
    UnauthorizedError,
    UnprocessableRequestError,
)


@pytest.mark.asyncio
async def test_client_no_api_key(monkeypatch):
    """Test that client raises ValueError when no API key is provided."""
    monkeypatch.delenv("HAIZE_API_KEY", raising=False)
    with pytest.raises(ValueError, match="HAIZE_API_KEY.*not found"):
        AsyncHaize()


@pytest.mark.asyncio
async def test_client_api_key_from_env(monkeypatch, api_key):
    """Test that client reads API key from environment variable."""
    monkeypatch.setenv("HAIZE_API_KEY", api_key)
    monkeypatch.setenv("HAIZE_BASE_URL", "https://api.env.com")
    client = AsyncHaize()
    assert client._headers["X-Haize-API-Key"] == api_key
    assert client._base_url == "https://api.env.com"
    await client.close()


@pytest.mark.asyncio
async def test_client_param_overrides_env(monkeypatch, api_key):
    """Test that parameters override environment variables."""
    monkeypatch.setenv("HAIZE_API_KEY", api_key)
    monkeypatch.setenv("HAIZE_BASE_URL", "https://api.env.com")
    client = AsyncHaize(api_key=api_key + "123", base_url="https://api.param.com")
    assert client._headers["X-Haize-API-Key"] == api_key + "123"
    assert client._base_url == "https://api.param.com"
    await client.close()


@pytest.mark.asyncio
async def test_client_invalid_api_key(monkeypatch):
    """Test that invalid API key results in UnauthorizedError on request."""

    async def mock_get(*args, **kwargs):
        response = Response(
            status_code=401,
            headers={"content-type": "application/json"},
            content=json.dumps({"detail": "Invalid API key"}).encode(),
        )
        return response

    client = AsyncHaize(api_key="invalid_key", base_url="https://api.test.com")
    monkeypatch.setattr(client._client, "get", mock_get)

    with pytest.raises(UnauthorizedError) as exc_info:
        await client.get("/test")

    assert exc_info.value.status_code == 401
    assert "Invalid API key" in exc_info.value.message
    await client.close()


@pytest.mark.asyncio
async def test_client_default_base_url(monkeypatch):
    """Test that client uses default base URL when not specified."""
    monkeypatch.setenv("HAIZE_API_KEY", "test_key")
    monkeypatch.delenv("HAIZE_BASE_URL", raising=False)
    client = AsyncHaize()
    assert client._base_url == "https://api.haizelabs.com/v1/"
    await client.close()


def test_sync_client_no_api_key(monkeypatch):
    """Test that sync client raises ValueError when no API key is provided."""
    monkeypatch.delenv("HAIZE_API_KEY", raising=False)
    with pytest.raises(ValueError, match="HAIZE_API_KEY.*not found"):
        Haize()


def test_sync_client_api_key_from_env(monkeypatch):
    """Test that sync client reads API key from environment variable."""
    monkeypatch.setenv("HAIZE_API_KEY", "env_api_key_456")
    monkeypatch.setenv("HAIZE_BASE_URL", "https://api.env.com")
    client = Haize()
    assert client._headers["X-Haize-API-Key"] == "env_api_key_456"
    assert client._base_url == "https://api.env.com"
    client.close()


def test_sync_client_param_overrides_env(monkeypatch):
    """Test that parameters override environment variables for sync client."""
    monkeypatch.setenv("HAIZE_API_KEY", "env_api_key")
    monkeypatch.setenv("HAIZE_BASE_URL", "https://api.env.com")
    client = Haize(api_key="param_api_key", base_url="https://api.param.com")
    assert client._headers["X-Haize-API-Key"] == "param_api_key"
    assert client._base_url == "https://api.param.com"
    client.close()


def test_sync_client_invalid_api_key(monkeypatch):
    """Test that invalid API key results in UnauthorizedError on sync request."""

    def mock_get(*args, **kwargs):
        response = Response(
            status_code=401,
            headers={"content-type": "application/json"},
            content=json.dumps({"detail": "Invalid API key"}).encode(),
        )
        return response

    client = Haize(api_key="invalid_key", base_url="https://api.test.com")
    monkeypatch.setattr(client._client, "get", mock_get)

    with pytest.raises(UnauthorizedError) as exc_info:
        client.get("/test")

    assert exc_info.value.status_code == 401
    assert "Invalid API key" in exc_info.value.message
    client.close()


def test_sync_client_default_base_url(monkeypatch):
    """Test that sync client uses default base URL when not specified."""
    monkeypatch.setenv("HAIZE_API_KEY", "test_key")
    monkeypatch.delenv("HAIZE_BASE_URL", raising=False)
    client = Haize()
    assert client._base_url == "https://api.haizelabs.com/v1/"
    client.close()


@pytest.mark.asyncio
async def test_client_raises_not_found_error(async_haize: AsyncHaize, monkeypatch):
    """Test that the async client raises NotFoundError for 404 responses."""

    async def mock_get(*args, **kwargs):
        response = Response(
            status_code=404,
            headers={"content-type": "application/json"},
            content=json.dumps(
                {"detail": "Dataset with id dataset_123 not found"}
            ).encode(),
        )
        return response

    monkeypatch.setattr(async_haize.datasets._client._client, "get", mock_get)

    with pytest.raises(NotFoundError) as exc_info:
        await async_haize.datasets.get("dataset_123")

    assert exc_info.value.status_code == 404
    assert "dataset_123" in exc_info.value.message


@pytest.mark.asyncio
async def test_client_raises_bad_request_error(async_haize: AsyncHaize, monkeypatch):
    """Test that the async client raises BadRequestError for 400 responses."""

    async def mock_post(*args, **kwargs):
        response = Response(
            status_code=400,
            headers={"content-type": "application/json"},
            content=json.dumps(
                {"detail": "Invalid creativity value: must be between 1 and 10"}
            ).encode(),
        )
        return response

    monkeypatch.setattr(async_haize.red_team_tests._client._client, "post", mock_post)

    with pytest.raises(BadRequestError) as exc_info:
        await async_haize.red_team_tests.create(
            name="test",
            system_id="sys_123",
            judge_ids=["judge_1"],
            custom_behaviors=["test"],
            creativity=3,
        )

    assert exc_info.value.status_code == 400
    assert "Invalid" in exc_info.value.message


@pytest.mark.asyncio
async def test_client_raises_unauthorized_error(async_haize: AsyncHaize, monkeypatch):
    """Test that the async client raises UnauthorizedError for 401 responses."""

    async def mock_get(*args, **kwargs):
        response = Response(
            status_code=401,
            headers={"content-type": "application/json"},
            content=json.dumps({"detail": "Invalid API key"}).encode(),
        )
        return response

    monkeypatch.setattr(async_haize.ai_systems._client._client, "get", mock_get)

    with pytest.raises(UnauthorizedError) as exc_info:
        await async_haize.ai_systems.get("system_123")

    assert exc_info.value.status_code == 401
    assert "Invalid API key" in exc_info.value.message


@pytest.mark.asyncio
async def test_client_raises_forbidden_error(async_haize: AsyncHaize, monkeypatch):
    """Test that the async client raises ForbiddenError for 403 responses."""

    async def mock_post(*args, **kwargs):
        response = Response(
            status_code=403,
            headers={"content-type": "application/json"},
            content=json.dumps(
                {
                    "detail": "User does not have the CREATE permission on resources of type tests.red_team"
                }
            ).encode(),
        )
        return response

    monkeypatch.setattr(async_haize.red_team_tests._client._client, "post", mock_post)

    with pytest.raises(ForbiddenError) as exc_info:
        await async_haize.red_team_tests.create(
            name="test",
            system_id="sys_123",
            judge_ids=["judge_1"],
            custom_behaviors=["test"],
        )

    assert exc_info.value.status_code == 403
    assert "CREATE permission" in exc_info.value.message


@pytest.mark.asyncio
async def test_client_raises_unprocessable_request_error(
    async_haize: AsyncHaize, monkeypatch
):
    """Test that the async client raises UnprocessableRequestError for 422 responses."""

    async def mock_post(*args, **kwargs):
        response = Response(
            status_code=422,
            headers={"content-type": "application/json"},
            content=json.dumps({"detail": "Test report already exists"}).encode(),
        )
        return response

    monkeypatch.setattr(async_haize.red_team_tests._client._client, "post", mock_post)

    with pytest.raises(UnprocessableRequestError) as exc_info:
        await async_haize.red_team_tests.generate_report("test_123")

    assert exc_info.value.status_code == 422
    assert "already exists" in exc_info.value.message


@pytest.mark.asyncio
async def test_client_context_manager(api_key):
    """Test that async client works as context manager."""
    async with AsyncHaize(
        api_key=api_key, base_url="http://localhost:8001/v1"
    ) as client:
        assert client._headers["X-Haize-API-Key"] == api_key
        assert client._base_url == "http://localhost:8001/v1"
        assert client._client is not None


def test_sync_client_context_manager(api_key):
    """Test that sync client works as context manager."""
    with Haize(api_key=api_key, base_url="http://localhost:8001/v1") as client:
        assert client._headers["X-Haize-API-Key"] == api_key
        assert client._base_url == "http://localhost:8001/v1"
        assert client._client is not None


@pytest.mark.asyncio
async def test_client_raises_internal_server_error(
    async_haize: AsyncHaize, monkeypatch
):
    """Test that the async client raises InternalServerError for 500 responses."""

    async def mock_get(*args, **kwargs):
        response = Response(
            status_code=500,
            headers={"content-type": "application/json"},
            content=json.dumps({"detail": "Database connection failed"}).encode(),
        )
        return response

    monkeypatch.setattr(async_haize.datasets._client._client, "get", mock_get)

    with pytest.raises(InternalServerError) as exc_info:
        await async_haize.datasets.get("dataset_123")

    assert exc_info.value.status_code == 500
    assert "Database connection" in exc_info.value.message
