from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session

from app.core.config import settings
from app.crud import user as crud_user


def test_register_user(client: TestClient):
    email = "newuser@example.com"
    password = "newpassword"
    data = {"email": email, "password": password, "full_name": "New User"}
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["email"] == email
    assert "id" in content


def test_register_existing_user(client: TestClient):
    email = "test@example.com"
    password = "testpassword"
    data = {"email": email, "password": password}
    # Register first time
    client.post(f"{settings.API_V1_STR}/auth/register", json=data)
    # Try to register again
    response = client.post(f"{settings.API_V1_STR}/auth/register", json=data)
    assert response.status_code == 400


def test_login_user(client: TestClient):
    email = "logintest@example.com"
    password = "loginpassword"
    data = {"email": email, "password": password}
    # Register user
    client.post(f"{settings.API_V1_STR}/auth/register", json=data)
    # Login with form data (OAuth2 standard)
    login_data = {"username": email, "password": password}
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert response.status_code == 200
    content = response.json()
    assert "access_token" in content
    assert "refresh_token" in content
    assert content["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient):
    email = "wrongpass@example.com"
    password = "correctpassword"
    data = {"email": email, "password": password}
    # Register user
    client.post(f"{settings.API_V1_STR}/auth/register", json=data)
    # Try to login with wrong password using form data
    login_data = {"username": email, "password": "wrongpassword"}
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert response.status_code == 401


def test_refresh_token(client: TestClient):
    email = "refresh@example.com"
    password = "refreshpassword"
    data = {"email": email, "password": password}
    # Register and login
    client.post(f"{settings.API_V1_STR}/auth/register", json=data)
    login_data = {"username": email, "password": password}
    login_response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    refresh_token = login_response.json()["refresh_token"]
    
    # Use refresh token
    response = client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert response.status_code == 200
    content = response.json()
    assert "access_token" in content
    assert "refresh_token" in content


def test_register_and_login_ok(client: TestClient, session: Session):
    """Test successful user registration and login flow (happy path)"""
    # Generate unique test email
    import time
    email = f"happypath_{int(time.time())}@example.com"
    password = "testpassword123"
    full_name = "Happy Path User"
    
    # Test registration
    register_data = {
        "email": email,
        "password": password,
        "full_name": full_name
    }
    response = client.post(f"{settings.API_V1_STR}/auth/register", json=register_data)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == email
    assert user_data["full_name"] == full_name
    assert user_data["is_active"] == True
    assert "id" in user_data
    assert "hashed_password" not in user_data  # Should not expose password
    
    # Test login with form-data (OAuth2 standard)
    login_data = {
        "username": email,
        "password": password
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"
    
    # Verify tokens are valid JWT strings
    assert len(token_data["access_token"]) > 20
    assert len(token_data["refresh_token"]) > 20
    
    # Clean up - delete test user
    test_user = crud_user.get_user_by_email(session, email=email)
    if test_user:
        session.delete(test_user)
        session.commit()