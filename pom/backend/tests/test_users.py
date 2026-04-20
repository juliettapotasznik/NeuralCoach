import pytest
from unittest.mock import patch
from models import User
from auth import get_password_hash

def test_register_user_success(client, db_session):
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "securepassword123"
    }
    
    # Mock the email sending function to avoid actual email attempts
    with patch("routers.users.send_verification_email"):
        response = client.post("/api/users/register", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "id" in data
    
    # Verify DB state
    user = db_session.query(User).filter(User.email == "newuser@example.com").first()
    assert user is not None
    assert user.is_verified is False

def test_register_duplicate_email(client, db_session):
    # Create existing user
    user = User(
        email="existing@example.com",
        username="existing",
        hashed_password="hash",
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()

    user_data = {
        "email": "existing@example.com",
        "username": "newuser",
        "password": "password"
    }
    
    response = client.post("/api/users/register", json=user_data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_register_case_insensitive_duplicate(client, db_session):
    # Create existing user
    user = User(
        email="existing@example.com",
        username="existing",
        hashed_password="hash",
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()

    # Try to register with uppercase email
    user_data = {
        "email": "EXISTING@example.com",
        "username": "newuser",
        "password": "password"
    }
    
    response = client.post("/api/users/register", json=user_data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login_success(client, db_session):
    password = "password123"
    hashed = get_password_hash(password)
    user = User(
        email="login@example.com",
        username="loginuser",
        hashed_password=hashed,
        is_verified=True # Must be verified to login
    )
    db_session.add(user)
    db_session.commit()

    login_data = {
        "username": "loginuser",
        "password": password
    }
    
    response = client.post("/api/users/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_unverified(client, db_session):
    password = "password123"
    hashed = get_password_hash(password)
    user = User(
        email="unverified@example.com",
        username="unverified",
        hashed_password=hashed,
        is_verified=False 
    )
    db_session.add(user)
    db_session.commit()

    login_data = {
        "username": "unverified",
        "password": password
    }
    
    response = client.post("/api/users/login", json=login_data)
    assert response.status_code == 403
    assert "Email not verified" in response.json()["detail"]

def test_get_me(client, db_session):
    # 1. Create User
    password = "password123"
    hashed = get_password_hash(password)
    user = User(
        email="me@example.com",
        username="meuser",
        hashed_password=hashed,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()

    # 2. Login to get token
    login_res = client.post("/api/users/login", json={"username": "meuser", "password": password})
    token = login_res.json()["access_token"]

    # 3. Call /me
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/users/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "meuser"
    assert data["email"] == "me@example.com"
