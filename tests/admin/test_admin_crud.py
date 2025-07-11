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

def test_get_admin(client, token):
    access_token = token["access_token"]
    response = client.get('/a/v1/manage',
    headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()

    pprint.pprint(json_data)

    assert "page" in str(json_data).lower()
    assert "per_page" in str(json_data).lower()
    assert "total_items" in str(json_data).lower()
    assert "total_pages" in str(json_data).lower()
    assert "zxcvbnm" in str(json_data).lower()
    assert "testadmin" in str(json_data).lower()

def test_create_new_admin(client, token):
    access_token = token["access_token"]
    response = client.post('/a/v1/manage',json={
        "username": "admin_crud_test_remove",
        "password": "admincrudtest_remove" ,
        "email" : "admincrud.remove@test.com"
        },
    headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()

    pprint.pprint(json_data)

    assert "successful" in str(json_data).lower()
    assert "login" in str(json_data).lower()
    assert "start" in str(json_data).lower()


def test_create_new_admin_put(client, token):
    access_token = token["access_token"]
    response = client.put('/a/v1/manage',json={
        "username": "testuser"
        },
    headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()

    pprint.pprint(json_data)

    assert "successful" in str(json_data).lower()
    assert "admin" in str(json_data).lower()

def test_books_delete_admin(client, token):
    access_token = token["access_token"]
    response = client.delete('/a/v1/manage',json={
        "username" : "admin_crud_test_remove"
        },
    headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()

    pprint.pprint(json_data)

    assert "removed" in str(json_data).lower()
    assert "user" in str(json_data).lower()
    assert "admin" in str(json_data).lower()
    assert "ban" in str(json_data).lower()


'''
credentials to use later
{
    "username": "admin_crud_test",
    "password": "admincrudtest" ,
    "email" : "admincrud@test.com"
}
'''