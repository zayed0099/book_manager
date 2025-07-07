import pytest
from run import app
from app.extensions import db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_successful_login(client):
    response = client.post('/auth/v1/login', json={
            "username": "zxcvbnm",
            "password": "zxcvbnm123@"
        })
    data = response.get_json()
    assert "access_token" in str(data).lower()
    assert "refresh_token" in str(data).lower()             

def test_no_username(client):
    response = client.post('/auth/v1/login', json={
            "password": "ntestpassword123"
        })
    json_data = response.get_json()
    assert "invalid" or "validation" in str(data).lower()

def test_user_not_found(client):
    response = client.post('/auth/v1/login', json={
            "username": "qwertwery",
            "password": "ntestpassword123"
        })
    assert response.status_code == 404
    data = response.get_json()
    assert "found" in str(data).lower()    

def test_wrong_password(client):
    response = client.post('/auth/v1/login', json={
            "username": "zxcvbnm",
            "password": "fdfefefd123"
        })
    assert response.status_code in [401, 404]
    data = response.get_json()
    assert "unsuccessful" in str(data).lower()  

# @pytest.fixture(scope="session")
# def token():
#     app.config['TESTING'] = True
#     with app.test_client() as client:
#         response = client.post('/auth/v1/login', json={
#             "username": "4testuser",
#             "password": "13testpassword123"
#         })
#         assert response.status_code in [200, 201]
#         json_data = response.get_json()
#         assert "access_token" in json_data
#         return {
#             "access_token": json_data["access_token"],
#             "refresh_token": json_data["refresh_token"]
#         }