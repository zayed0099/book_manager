import pytest
import pprint
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
            "username": "user4321",
            "password": "user4321"
        })
        assert response.status_code in [200, 201]
        json_data = response.get_json()
        assert "access_token" in json_data
        return {
            "access_token": json_data["access_token"],
            "refresh_token": json_data["refresh_token"]
        }
        
# To Send review+ratings
def test_book_review_post(client, token):
    access_token = token["access_token"]
    
    response = client.post('/api/v1/reviews',json={
        "review" : "A good book which i thoroughly enjoyed while reading.And i will also recommend it to everyone" ,
        "rating" : 7,
        "book_id" : 5},
    headers={
        "Authorization": f"Bearer {access_token}"
    })
    json_data = response.get_json()
    pprint.pprint(json_data)
    assert response.status_code == 200
    assert "rating" in json_data
    assert "review" in json_data
    assert "book_id" in json_data


# def test_book_review_delete(client, token):
#     access_token = token["access_token"]
    
#     response = client.delete('/reviews/1',
#     headers={
#         "Authorization": f"Bearer {access_token}"
#     })
#     assert response.status_code == 200
#     json_data = response.get_json()
#     assert "successfully" in str(json_data).lower()
#     assert "updated" in str(json_data).lower()