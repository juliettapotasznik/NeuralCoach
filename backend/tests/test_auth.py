import pytest
from auth import verify_password, get_password_hash, authenticate_user
from models import User

def test_hash_password():
    password = "secret_password"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)

def test_authenticate_user_success(db_session):
    # Setup
    password = "testpassword"
    hashed = get_password_hash(password)
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hashed,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()

    # Test exact match
    auth_user = authenticate_user(db_session, "testuser", password)
    assert auth_user is not None
    assert auth_user.id == user.id

    # Test email match
    auth_user = authenticate_user(db_session, "test@example.com", password)
    assert auth_user is not None
    assert auth_user.id == user.id

def test_authenticate_user_case_insensitive(db_session):
    # Setup
    password = "testpassword"
    hashed = get_password_hash(password)
    user = User(
        email="lower@example.com",
        username="LowerUser",
        hashed_password=hashed,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()

    # Test mixed case email login
    auth_user = authenticate_user(db_session, "LOWER@example.com", password)
    assert auth_user is not None
    assert auth_user.email == "lower@example.com"

    # Test mixed case username login
    auth_user = authenticate_user(db_session, "loweruser", password)
    assert auth_user is not None
    assert auth_user.username == "LowerUser"

def test_authenticate_user_failures(db_session):
    # Setup
    password = "testpassword"
    hashed = get_password_hash(password)
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hashed,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()

    # Wrong password
    assert authenticate_user(db_session, "testuser", "wrong") is None

    # Non-existent user
    assert authenticate_user(db_session, "ghost", password) is None
