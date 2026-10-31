"""Shared API context and isolated pet data with automatic cleanup."""

import os
from collections.abc import Generator
from http import HTTPStatus
from typing import Any
from uuid import uuid4

import pytest
from playwright.sync_api import APIRequestContext, Playwright


@pytest.fixture
def api_context(playwright: Playwright) -> Generator[APIRequestContext, None, None]:
    """Create an independent HTTP context for each test; no browser is needed."""
    base_url = os.getenv("PETSTORE_BASE_URL", "https://petstore3.swagger.io/api/v3")
    headers = {"Accept": "application/json"}
    if api_key := os.getenv("PETSTORE_API_KEY"):
        headers["api_key"] = api_key

    context = playwright.request.new_context(
        base_url=f"{base_url.rstrip('/')}/",
        extra_http_headers=headers,
        timeout=15_000,
    )
    try:
        yield context
    finally:
        context.dispose()


@pytest.fixture
def pet_payload(api_context: APIRequestContext) -> Generator[dict[str, Any], None, None]:
    """Reserve unique data and register cleanup before a test sends POST."""
    unique_id = uuid4()
    payload = {
        # Playwright transports JSON through JavaScript: stay below 2**53.
        "id": unique_id.int % (2**52 - 1) + 1,
        "name": f"qa-pet-{unique_id.hex}",
        "category": {"id": 1, "name": "Dogs"},
        "photoUrls": ["https://example.com/pet.jpg"],
        "tags": [{"id": 1, "name": f"qa-{unique_id.hex}"}],
        "status": "available",
    }
    try:
        yield payload
    finally:
        response = api_context.delete(f"pet/{payload['id']}")
        # The DELETE test may already have removed this pet.
        assert response.status in (HTTPStatus.OK, HTTPStatus.NOT_FOUND), (
            f"Cleanup failed for pet {payload['id']}: "
            f"HTTP {response.status}, {response.text()}"
        )


@pytest.fixture
def created_pet(
    api_context: APIRequestContext, pet_payload: dict[str, Any]
) -> dict[str, Any]:
    """Create the prerequisite pet without depending on another test."""
    response = api_context.post("pet", data=pet_payload)
    assert response.status == HTTPStatus.OK, (
        f"Pet setup failed: HTTP {response.status}, {response.text()}"
    )
    assert response.json()["id"] == pet_payload["id"]
    return pet_payload
