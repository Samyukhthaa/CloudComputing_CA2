import pytest
import sys
sys.path.append(".")

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_login_page(client):
    response = client.get('/')
    assert response.status_code == 200


def test_register_page(client):
    response = client.get('/register')
    assert response.status_code == 200


def test_books_page(client):
    response = client.get('/books')
    assert response.status_code == 200
