import json
import sys
import os
import pytest

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
            "username": "testcrud",
            "password": "44256b691@yubiG"
        })
        assert response.status_code in [200, 201]
        json_data = response.get_json()
        assert "access_token" in json_data
        return {
            "access_token": json_data["access_token"],
            "refresh_token": json_data["refresh_token"]
        }

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

def test_books_search_title(client, token):
    access_token = token["access_token"]
    response = client.get('/api/v1/books?title=Dune',
    headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert "frank herbert" in str(json_data).lower()
    assert "page" in str(json_data).lower()
    assert "per_page" in str(json_data).lower()
    assert "total_items" in str(json_data).lower()
    assert "total_pages" in str(json_data).lower()

def test_books_search_author(client, token):
    access_token = token["access_token"]
    response = client.get('/api/v1/books?author=George Orwell',
    headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert "1984" in str(json_data).lower()
    assert "page" in str(json_data).lower()
    assert "per_page" in str(json_data).lower()
    assert "total_items" in str(json_data).lower()
    assert "total_pages" in str(json_data).lower()

def test_search_author_and_title(client, token):
    access_token = token["access_token"]
    response = client.get('/api/v1/books?title=The Alchemist&author=Paulo Coelho',
    headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert "the alchemist" and "paulo coelho" in str(json_data).lower()
    assert "page" in str(json_data).lower()
    assert "per_page" in str(json_data).lower()
    assert "total_items" in str(json_data).lower()
    assert "total_pages" in str(json_data).lower()

def test_adding_books(client, token):
    access_token = token["access_token"]
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    file = os.path.join(basedir, 'books_for_post.json')

    with open(file, 'r') as f:
        books = json.load(f)

    for book in books:
        response = client.post('/api/v1/books', json={
            "title": book["title"],
            "author": book["author"],
            "genre": book["genre"]
        }, headers={
            "Authorization": f"Bearer {access_token}"
        })
        
        assert response.status_code == 201
        
        json_data = response.get_json()
        assert "title" in json_data
        assert "author" in json_data
        assert "genre" in json_data
        assert json_data["title"] == book["title"]
        assert json_data["author"] == book["author"]
        assert json_data["genre"] == book["genre"]



# -------- unused code----------
# @pytest.fixture(scope="session")
# def token():
#     app.config['TESTING'] = True
#     with app.test_client() as client:
#         new_user = client.post('/auth/v1/register', json={
#         "username" : "testcrud",
#         "password" : "44256b691@yubiG" ,
#         "email" : "test_bookcrud@mail.com"
#         })
       
#         response = client.post('/auth/v1/login', json={
#             "username": "testcrud",
#             "password": "44256b691@yubiG"
#         })
#         assert response.status_code in [200, 201]
#         json_data = response.get_json()
#         assert "access_token" in json_data
#         return {
#             "access_token": json_data["access_token"],
#             "refresh_token": json_data["refresh_token"]
#         }