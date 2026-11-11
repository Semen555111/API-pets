"""Seven independent API tests based on the Petstore v3 OpenAPI contract."""
import pytest
from playwright.sync_api import Playwright, sync_playwright

def test_get_petid(api_context, create_pet) -> None:

    response = api_context.get(
        f'pet/{create_pet["id"]}'
    )
    assert response.status == 200, response.text()
    res_json = response.json()
    assert res_json["id"] == create_pet["id"]
    assert res_json["category"]["name"] == "Cats"

def test_update_name_pet(api_context, create_pet) -> None:
    updated_pet = create_pet.copy()
    updated_pet['name'] += 'Updated'
    response = api_context.put('pet/', data=updated_pet)
    assert response.status == 200, response.text()
    res_json = response.json()
    assert res_json["id"] == updated_pet["id"]

def test_update_status_pet(api_context, create_pet) -> None:
    updated_pet = create_pet.copy()
    updated_pet['status'] = 'sold'
    response = api_context.put('pet/', data=updated_pet)
    assert response.status == 200, response.text()
    res_json = response.json()
    assert res_json["status"] == "sold"
    assert res_json["id"] == updated_pet["id"]

@pytest.mark.parametrize("sta", ["available", "pending", "sold"])
def test_update_status_pet_parametrized(api_context, create_pet, sta) -> None:
    updated_pet = create_pet.copy()
    updated_pet['status'] = sta
    response = api_context.put('pet/', data=updated_pet)
    assert response.status == 200, response.text()
    res_json = response.json()
    assert res_json["status"] == sta
    assert res_json["id"] == updated_pet["id"]

def test_delete_pet(api_context, create_pet) -> None:
    updated_pet = create_pet.copy()
    response = api_context.delete(f'pet/{updated_pet["id"]}')
    assert response.status == 200, response.text()
    response = api_context.get(f'pet/{updated_pet["id"]}')
    assert response.status == 404, response.text()

@pytest.mark.parametrize('number', 'expected',
                         [pytest.param(-1, 404, id='404'),
                          pytest.param('abc', 400, id='400'),
                          pytest.param('', 400, id='400')])
def test_invalid_pet_id(api_context, number, expected) -> None:
    response = api_context.get(f'pet/{number}')
    assert response.status == expected, response.text()