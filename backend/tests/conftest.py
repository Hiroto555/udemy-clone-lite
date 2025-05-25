from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.api.deps import get_db
from app.core.config import settings
from app.main import app


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def normal_user_token_headers(client: TestClient):
    login_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User",
    }
    # Create user
    client.post(f"{settings.API_V1_STR}/auth/register", json=login_data)
    # Login
    response = client.post(f"{settings.API_V1_STR}/auth/login", json=login_data)
    tokens = response.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


@pytest.fixture
def superuser_token_headers(client: TestClient):
    login_data = {
        "email": "admin@example.com",
        "password": "adminpassword",
        "full_name": "Admin User",
    }
    # Create user
    response = client.post(f"{settings.API_V1_STR}/auth/register", json=login_data)
    user_id = response.json()["id"]
    
    # Make user superuser (normally done through init_db)
    from app.models.user import User
    session = next(get_db())
    user = session.get(User, user_id)
    user.is_superuser = True
    session.add(user)
    session.commit()
    
    # Login
    response = client.post(f"{settings.API_V1_STR}/auth/login", json=login_data)
    tokens = response.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers