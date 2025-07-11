import json
import sys
import os
import pytest
import pprint

# Get the absolute path to the root of your project
current_dir = os.path.dirname(__file__)              # tests/
project_root = os.path.abspath(os.path.join(current_dir, '..'))  # go up to project root

# Add the project root to sys.path
sys.path.append(project_root)

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
            "username": "testadmin",
            "password": "testadminpass"
        })
        assert response.status_code in [200, 201]
        json_data = response.get_json()
        assert "access_token" in json_data
        return {
            "access_token": json_data["access_token"],
            "refresh_token": json_data["refresh_token"]
        }

# def test_books_get_book_admin(client, token):
#     access_token = token["access_token"]
#     response = client.get('/a/v1/books?page=1&per_page=5',
#     headers={
#         "Authorization": f"Bearer {access_token}"
#     })
#     assert response.status_code == 200
#     json_data = response.get_json()

#     pprint.pprint(json_data)

#     assert "page" in str(json_data).lower()
#     assert "per_page" in str(json_data).lower()
#     assert "total_items" in str(json_data).lower()
#     assert "total_pages" in str(json_data).lower()
#     assert "dune" in str(json_data).lower()
#     assert "one hundred years of solitude" in str(json_data).lower()
#     assert "to kill a mockingbird" in str(json_data).lower()

# def test_admin_ban_user(client, token):
#     access_token = token["access_token"]
#     response = client.delete('/a/v1/user/ban',json={
#         "username" : "testuser"
#         },
#     headers={
#         "Authorization": f"Bearer {access_token}"
#     })
#     assert response.status_code == 200
#     json_data = response.get_json()

#     pprint.pprint(json_data)

#     assert "user" in str(json_data).lower()
#     assert "testuser" in str(json_data).lower()
#     assert "banned" in str(json_data).lower()

# def test_admin_unban_user(client, token):
#     access_token = token["access_token"]
#     response = client.put('/a/v1/user/ban',json={
#         "username" : "testuser"
#         },
#     headers={
#         "Authorization": f"Bearer {access_token}"
#     })
#     assert response.status_code == 200
#     json_data = response.get_json()

#     pprint.pprint(json_data)

#     assert "access" in str(json_data).lower()
#     assert "testuser" in str(json_data).lower()
#     assert "restored" in str(json_data).lower()

 def test_admin_delete_jwt(client, token):
    access_token = token["access_token"]
    response = client.put('/a/v1/jwt/clear',
    headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    json_data = response.get_json()

    pprint.pprint(json_data)

    assert "tokens" in str(json_data).lower()
    assert "permitted" in str(json_data).lower()
    assert "delete" in str(json_data).lower()   