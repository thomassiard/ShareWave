import pytest
from flask import Flask
from flask.testing import FlaskClient
from your_project_name import create_app, db
from your_project_name.models import User

@pytest.fixture
def app() -> Flask:
    """Create a new Flask application instance for each test."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a new test client for the Flask application."""
    return app.test_client()

@pytest.fixture
def auth(client: FlaskClient):
    """Fixture for authentication."""
    def register(username, password):
        return client.post('/auth/register', json={
            'username': username,
            'password': password
        })

    def login(username, password):
        return client.post('/auth/login', json={
            'username': username,
            'password': password
        })

    return {
        'register': register,
        'login': login,
    }

def test_home_page(client: FlaskClient):
    """Test the home page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to ShareWave' in response.data

def test_user_registration(client: FlaskClient, auth: dict):
    """Test user registration functionality."""
    response = auth['register']('testuser', 'testpassword')
    assert response.status_code == 201
    assert b'User created successfully' in response.data

def test_user_login(client: FlaskClient, auth: dict):
    """Test user login functionality."""
    auth['register']('testuser', 'testpassword')
    response = auth['login']('testuser', 'testpassword')
    assert response.status_code == 200
    assert b'Login successful' in response.data

def test_unauthorized_access(client: FlaskClient):
    """Test access to a protected resource without authentication."""
    response = client.get('/protected-resource')
    assert response.status_code == 401
    assert b'Unauthorized' in response.data

def test_profile_info(client: FlaskClient, auth: dict):
    """Test retrieving user profile information."""
    auth['register']('testuser', 'testpassword')
    auth['login']('testuser', 'testpassword')
    response = client.get('/profile')
    assert response.status_code == 200
    assert b'testuser' in response.data
