"""Seven independent API tests based on the Petstore v3 OpenAPI contract."""

from http import HTTPStatus
from typing import Any

import pytest
from playwright.sync_api import APIRequestContext, APIResponse

pytestmark = pytest.mark.api


def assert_pet_response(response: APIResponse, expected: dict[str, Any]) -> None:
    """Check the exact status, JSON content type, and submitted pet fields."""
    assert response.status == HTTPStatus.OK, (
        f"Expected HTTP 200, got {response.status}: {response.text()}"
    )
    assert response.headers.get("content-type", "").split(";")[0] == "application/json"
    actual = response.json()
    assert isinstance(actual, dict), f"Expected a pet object, got {actual!r}"
    assert {key: actual.get(key) for key in expected} == expected


def test_create_pet(api_context: APIRequestContext, pet_payload: dict[str, Any]) -> None:
    """POST /pet creates a pet and persists its fields."""
    response = api_context.post("pet", data=pet_payload)

    assert_pet_response(response, pet_payload)
    saved_pet = api_context.get(f"pet/{pet_payload['id']}")
    assert_pet_response(saved_pet, pet_payload)


def test_get_pet_by_id(
    api_context: APIRequestContext, created_pet: dict[str, Any]
) -> None:
    """GET /pet/{id} returns the requested pet."""
    response = api_context.get(f"pet/{created_pet['id']}")

    assert_pet_response(response, created_pet)


def test_update_pet(api_context: APIRequestContext, created_pet: dict[str, Any]) -> None:
    """PUT /pet updates fields and persists them without changing the ID."""
    updated_pet = {
        **created_pet,
        "name": f"{created_pet['name']}-updated",
        "status": "sold",
    }

    response = api_context.put("pet", data=updated_pet)

    assert_pet_response(response, updated_pet)
    saved_pet = api_context.get(f"pet/{created_pet['id']}")
    assert_pet_response(saved_pet, updated_pet)


def test_find_pets_by_status(
    api_context: APIRequestContext, created_pet: dict[str, Any]
) -> None:
    """GET /pet/findByStatus filters results and includes our own pet."""
    response = api_context.get(
        "pet/findByStatus", params={"status": created_pet["status"]}
    )

    assert response.status == HTTPStatus.OK, response.text()
    assert response.headers.get("content-type", "").split(";")[0] == "application/json"
    pets = response.json()
    assert isinstance(pets, list), f"Expected a list, got {pets!r}"
    assert pets, "A matching pet was created, so the result must not be empty"
    assert all(isinstance(pet, dict) for pet in pets)
    assert all(pet.get("status") == created_pet["status"] for pet in pets)
    matching_pets = [pet for pet in pets if pet.get("id") == created_pet["id"]]
    assert len(matching_pets) == 1, f"Expected our pet exactly once, got {matching_pets!r}"
    assert {key: matching_pets[0].get(key) for key in created_pet} == created_pet


def test_delete_pet(api_context: APIRequestContext, created_pet: dict[str, Any]) -> None:
    """DELETE /pet/{id} removes the pet; a subsequent GET returns 404."""
    response = api_context.delete(f"pet/{created_pet['id']}")

    assert response.status == HTTPStatus.OK, response.text()
    deleted_pet = api_context.get(f"pet/{created_pet['id']}")
    assert deleted_pet.status == HTTPStatus.NOT_FOUND, deleted_pet.text()


def test_get_pet_with_invalid_id(api_context: APIRequestContext) -> None:
    """GET /pet/{id} rejects a non-integer identifier with 400."""
    response = api_context.get("pet/not-an-integer")

    assert response.status == HTTPStatus.BAD_REQUEST, response.text()


def test_find_pets_with_invalid_status(api_context: APIRequestContext) -> None:
    """GET /pet/findByStatus rejects a value outside the status enum."""
    response = api_context.get("pet/findByStatus", params={"status": "invalid-status"})

    assert response.status == HTTPStatus.BAD_REQUEST, response.text()
