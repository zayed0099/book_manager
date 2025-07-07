import pytest
from run import app
from app.extensions import db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="session")
def token():
    app.config['TESTING'] = True
    with app.test_client() as client:
        response = client.post('/auth/v1/login', json={
            "username": "4testuser",
            "password": "13testpassword123"
        })
        assert response.status_code in [200, 201]
        json_data = response.get_json()
        assert "access_token" in json_data
        return {
            "access_token": json_data["access_token"],
            "refresh_token": json_data["refresh_token"]
        }

def test_refresh_token(client, token):
    refresh_token = token["refresh_token"]

    response = client.post('/auth/v1/refresh', 
     headers={
        "Authorization": f"Bearer {refresh_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert "access_token" in json_data
    assert "refresh_token" in json_data

def test_logout(client, token):
    access_token = token["access_token"]

    response = client.delete('/auth/v1/logout',
    headers={
        "Authorization": f"Bearer {access_token}"
    })

    json_data = response.get_json()
    assert "revoked" in str(json_data).lower()