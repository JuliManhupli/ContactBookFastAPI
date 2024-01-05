from datetime import timedelta, datetime
from unittest.mock import Mock, patch, AsyncMock

from src.conf import messages
from src.services.auth import auth_service


future_data =(datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
def test_get_null_contacts(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("api/contacts", headers=headers)
        assert response.status_code == 404, response.text
        assert response.json() == {"detail": messages.CONTACTS_NOT_FOUND}


def test_create_contact(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post("api/contacts", headers=headers, json={
            "name": "test",
            "surname": "test",
            "email": "test@gmail.com",
            "birthday": future_data,
            "phone": "123456789"
        })
        assert response.status_code == 201, response.text
        data = response.json()
        assert "id" in data
        assert data["name"] == "test"
        assert data["surname"] == "test"
        assert data["email"] == "test@gmail.com"
        assert data["birthday"] == future_data
        assert data["phone"] == "123456789"


def test_get_contacts(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("api/contacts", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert "id" in data[0]
        assert data[0]["name"] == "test"
        assert data[0]["surname"] == "test"
        assert data[0]["email"] == "test@gmail.com"
        assert data[0]["birthday"] == future_data
        assert data[0]["phone"] == "123456789"


def test_get_contact(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("api/contacts/1", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert "id" in data
        assert data["name"] == "test"
        assert data["surname"] == "test"
        assert data["email"] == "test@gmail.com"
        assert data["birthday"] == future_data
        assert data["phone"] == "123456789"


def test_get_null_contact(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("api/contacts/2", headers=headers)
        assert response.status_code == 404, response.text
        assert response.json() == {"detail": messages.CONTACT_NOT_FOUND}


def test_update_contact(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put("api/contacts/1", headers=headers, json={
            "name": "new_name",
            "surname": "new_surname",
            "email": "new_email@gmail.com",
            "birthday": future_data,
            "phone": "987654321"
        })

        assert response.status_code == 200, response.text
        data = response.json()
        assert "id" in data
        assert data["name"] == "new_name"
        assert data["surname"] == "new_surname"
        assert data["email"] == "new_email@gmail.com"
        assert data["birthday"] == future_data
        assert data["phone"] == "987654321"


def test_update_null_contact(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.put("api/contacts/2", headers=headers, json={
            "name": "new_name",
            "surname": "new_surname",
            "email": "new_email@gmail.com",
            "birthday": "2000-10-15",
            "phone": "987654321"
        })
        assert response.status_code == 404, response.text
        assert response.json() == {"detail": messages.CONTACT_NOT_FOUND}


def test_upcoming_birthday(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("api/contacts/birthday/", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert "id" in data[0]
        assert data[0]["name"] == "new_name"
        assert data[0]["surname"] == "new_surname"
        assert data[0]["email"] == "new_email@gmail.com"
        assert data[0]["birthday"] == future_data
        assert data[0]["phone"] == "987654321"


def test_delete_null_contact(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete("api/contacts/2", headers=headers)
        assert response.status_code == 404, response.text
        assert response.json() == {"detail": messages.CONTACT_NOT_FOUND}

def test_delete_contact(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.delete("api/contacts/1", headers=headers)
        assert response.status_code == 204, response.text


def test_null_upcoming_birthday(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("api/contacts/birthday/", headers=headers)
        assert response.status_code == 404, response.text
        assert response.json() == {"detail": messages.CONTACTS_NOT_FOUND}