import pytest
from run import app
from app.extensions import db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
    with app.test_client() as client:
        yield client

def test_signup_success(client):
    response = client.post('/auth/v1/register', json={
        "username" : "zxcvbnm",
        "password" : "zxcvbnm123@" ,
        "email" : "zxcvbnm123@msil.com"
        })
    assert response.status_code == 200
    data = response.get_json()
    assert "successful" in str(data).lower()

def test_signup_no_data(client):
    response = client.post('/auth/v1/register', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "validation failed" or "missing" or "invalid" in str(data).lower()

def test_signup_missing_password(client):
    response = client.post('/auth/v1/register', json={
        "username" : "testuser_wo_pass"
        })
    assert response.status_code == 400
    data = response.get_json()
    assert "validation" in str(data).lower()

def test_signup_missing_email(client):
    response = client.post('/auth/v1/register', json={
        "username" : "testuser_wo_mail" ,
        "email" : "123vwew@mail.com"
        })
    assert response.status_code == 400
    data = response.get_json()
    assert "validation" or "invalid" in str(data).lower()
