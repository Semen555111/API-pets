"""Shared API context and isolated pet data with automatic cleanup."""
import pytest
import numpy as np
from uuid import uuid4
from playwright.sync_api import APIRequestContext, Playwright, sync_playwright

@pytest.fixture(scope="session")
def base_data():
    return {
        "id": np.random.randint(1, 10000000),
        "name": f'Fluffy-{uuid4()}',
        "category": {
            "id": np.random.randint(1, 10000000),
            "name": "Cats"
        },
        "status": "available",
        "photoUrls": []
    }

@pytest.fixture
def api_context(playwright: Playwright, request: pytest.FixtureRequest) -> APIRequestContext:
    URL = "https://petstore3.swagger.io/api/v3/"
    request = playwright.request.new_context(base_url=URL)
    yield request
    request.dispose()

@pytest.fixture
def create_pet(api_context: APIRequestContext, base_data) -> dict:
    new_pet = base_data.copy()
    response = api_context.post("pet", data=new_pet)
    assert response.status == 200
    yield new_pet
    delete_pet = api_context.delete(f'pets/{base_data["id"]}')
    







