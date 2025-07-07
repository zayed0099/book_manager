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
        new_user = client.post('/auth/v1/register', json={
        "username" : "testcrud",
        "password" : "44256b691@yubiG" ,
        "email" : "test_bookcrud@mail.com"
        })
       
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

def test_adding_books(client, token):
    access_token = token["access_token"]

    books = [
  {
    "title": "One Hundred Years of Solitude",
    "author": "Gabriel García Márquez",
    "genre": "Magical Realism"
  },
  {
    "title": "Dune",
    "author": "Frank Herbert",
    "genre": "Science Fiction"
  },
  {
    "title": "Pride and Prejudice",
    "author": "Jane Austen",
    "genre": "Romance"
  },
  {
    "title": "To Kill a Mockingbird",
    "author": "Harper Lee",
    "genre": "Southern Gothic"
  },
  {
    "title": "Sapiens: A Brief History of Humankind",
    "author": "Yuval Noah Harari",
    "genre": "History"
  },
  {
    "title": "The Haunting of Hill House",
    "author": "Shirley Jackson",
    "genre": "Horror"
  },
  {
    "title": "The Hitchhiker's Guide to the Galaxy",
    "author": "Douglas Adams",
    "genre": "Satirical Science Fiction"
  },
  {
    "title": "Educated",
    "author": "Tara Westover",
    "genre": "Memoir"
  },
  {
    "title": "The Count of Monte Cristo",
    "author": "Alexandre Dumas",
    "genre": "Adventure"
  },
  {
    "title": "Where the Crawdads Sing",
    "author": "Delia Owens",
    "genre": "Mystery"
  }
]
    for book in books:
        response = client.post('/api/v1/books', json={
        "title": book["title"],
        "author": book["author"],
        "genre" : book["genre"]
    },
        headers={
            "Authorization": f"Bearer {access_token}"
        })
        assert response.status_code == 201
        json_data = response.get_json()
        assert json_data["title"] == book["title"]
        assert json_data["author"] == book["author"]
        assert json_data["genre"] == book["genre"]

