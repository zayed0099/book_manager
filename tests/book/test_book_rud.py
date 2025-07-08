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
        new_user = client.post('/auth/v1/register', json={
        "username" : "bookrudtest",
        "password" : "zxasqwerdfcv" ,
        "email" : "bookrudtest@gmail.com"
        })
       
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

    def test_books_pagination(client, token):
    access_token = token["access_token"]
    response = client.get('/api/v1/books?page=2&per_page=5',
    headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert "page" in str(json_data).lower()
    assert "per_page" in str(json_data).lower()
    assert "total_items" in str(json_data).lower()
    assert "total_pages" in str(json_data).lower()
    