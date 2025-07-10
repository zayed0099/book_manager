import pytest

import sys
import os

# Get the absolute path to the root of your project
current_dir = os.path.dirname(__file__)              # tests/book/
project_root = os.path.abspath(os.path.join(current_dir, '../../..'))

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
            "username": "bookrudtest",
            "password": "zxasqwerdfcv"
        })
        assert response.status_code in [200, 201]
        json_data = response.get_json()
        assert "access_token" in json_data
        return {
            "access_token": json_data["access_token"],
            "refresh_token": json_data["refresh_token"]
        }
        
def test_book_get_by_id(client, token):
    access_token = token["access_token"]
    
    response = client.get('/api/v1/books/21',
    headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert "test" in str(json_data).lower()
    assert "auth_test" in str(json_data).lower()

def test_book_put_by_id(client, token):
    access_token = token["access_token"]
    
    response = client.put('/api/v1/books/22',json={
        "title" : "just_updated1" ,
        "author" : "updated1"},
    headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert "successfully" in str(json_data).lower()
    assert "updated" in str(json_data).lower()
    
def test_book_delete_by_id(client, token):
    access_token = token["access_token"]
    
    response = client.delete('/api/v1/books/23',
    headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert "successfully" in str(json_data).lower()
    assert "deleted" in str(json_data).lower()

def test_recover_book(client, token):
    access_token = token["access_token"]
    
    response = client.get('/api/v1/recovery',
    headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert "authordes" in str(json_data).lower()
    assert "recovery_check" in str(json_data).lower()

""" adding/deleting/updating books favourite test"""

def test_see_book_favourite(client, token):
    access_token = token["access_token"]
    
    response = client.get('/api/v1/favourites',
    headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert "favourito" in str(json_data).lower()
    assert "check" in str(json_data).lower()

def test_add_book_favourites(client, token):
    access_token = token["access_token"]
    
    response = client.put('/api/v1/favourites/27',
    headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert "favourite" in str(json_data).lower()
    assert "added" in str(json_data).lower()

def test_delete_book_favourites(client, token):
    access_token = token["access_token"]
    
    response = client.delete('/api/v1/favourites/26',json={
        "title" : "removefav"},
    headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert "favourites" in str(json_data).lower()
    assert "removed" in str(json_data).lower()