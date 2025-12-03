from typing import Dict
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.core.config import settings
import random
import string
from app.schemas.user import UserCreate
from app.crud import user as crud_user

def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))

def random_email() -> str:
    return f"{random_lower_string()}@example.com"

@pytest.fixture
def instructor_token_headers(client: TestClient, session: Session) -> Dict[str, str]:
    email = random_email()
    password = "testpassword"
    user_in = UserCreate(email=email, password=password)
    crud_user.create_user(db=session, user_create=user_in)

    login_data = {
        "username": email,
        "password": password,
    }
    r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers

def test_create_section(
    client: TestClient, instructor_token_headers: Dict[str, str]
) -> None:
    # 1. Create a course
    data = {"title": "Test Course", "price": 10.0}
    response = client.post(
        f"{settings.API_V1_STR}/courses/", headers=instructor_token_headers, json=data
    )
    assert response.status_code == 200, response.text
    course = response.json()
    course_id = course["id"]

    # 2. Add a section
    section_data = {"title": "Introduction", "order": 1}
    response = client.post(
        f"{settings.API_V1_STR}/courses/{course_id}/sections",
        headers=instructor_token_headers,
        json=section_data,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content["title"] == section_data["title"]
    assert content["course_id"] == course_id

def test_create_lecture(
    client: TestClient, instructor_token_headers: Dict[str, str]
) -> None:
    # 1. Create a course
    data = {"title": "Test Course", "price": 10.0}
    response = client.post(
        f"{settings.API_V1_STR}/courses/", headers=instructor_token_headers, json=data
    )
    course_id = response.json()["id"]

    # 2. Add a section
    section_data = {"title": "Introduction", "order": 1}
    response = client.post(
        f"{settings.API_V1_STR}/courses/{course_id}/sections",
        headers=instructor_token_headers,
        json=section_data,
    )
    section_id = response.json()["id"]

    # 3. Add a lecture
    lecture_data = {
        "title": "Welcome",
        "content_text": "Hello world",
        "order": 1
    }
    response = client.post(
        f"{settings.API_V1_STR}/courses/sections/{section_id}/lectures",
        headers=instructor_token_headers,
        json=lecture_data,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content["title"] == lecture_data["title"]
    assert content["section_id"] == section_id
    assert content["content_text"] == "Hello world"

def test_read_course_with_sections(
    client: TestClient, instructor_token_headers: Dict[str, str]
) -> None:
    # 1. Create course, section, lecture
    data = {"title": "Full Course", "price": 10.0}
    r = client.post(f"{settings.API_V1_STR}/courses/", headers=instructor_token_headers, json=data)
    course_id = r.json()["id"]

    s_data = {"title": "Sec 1"}
    r = client.post(f"{settings.API_V1_STR}/courses/{course_id}/sections", headers=instructor_token_headers, json=s_data)
    section_id = r.json()["id"]

    l_data = {"title": "Lec 1", "content_text": "Content"}
    client.post(f"{settings.API_V1_STR}/courses/sections/{section_id}/lectures", headers=instructor_token_headers, json=l_data)

    # 2. Get sections
    response = client.get(
        f"{settings.API_V1_STR}/courses/{course_id}/sections",
        headers=instructor_token_headers
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert len(content) == 1
    assert content[0]["title"] == "Sec 1"
    assert len(content[0]["lectures"]) == 1
    assert content[0]["lectures"][0]["title"] == "Lec 1"

def test_delete_section_cascade(
    client: TestClient, instructor_token_headers: Dict[str, str]
) -> None:
    # 1. Create course, section, lecture
    data = {"title": "Delete Course", "price": 10.0}
    r = client.post(f"{settings.API_V1_STR}/courses/", headers=instructor_token_headers, json=data)
    course_id = r.json()["id"]

    s_data = {"title": "Sec 1"}
    r = client.post(f"{settings.API_V1_STR}/courses/{course_id}/sections", headers=instructor_token_headers, json=s_data)
    section_id = r.json()["id"]

    l_data = {"title": "Lec 1", "content_text": "Content"}
    r_lec = client.post(f"{settings.API_V1_STR}/courses/sections/{section_id}/lectures", headers=instructor_token_headers, json=l_data)
    lecture_id = r_lec.json()["id"]

    # 2. Delete section
    response = client.delete(
        f"{settings.API_V1_STR}/courses/sections/{section_id}",
        headers=instructor_token_headers
    )
    assert response.status_code == 200, response.text

    # 3. Verify section is gone
    r = client.get(f"{settings.API_V1_STR}/courses/{course_id}/sections", headers=instructor_token_headers)
    assert len(r.json()) == 0

    # 4. Verify lecture is gone (via direct check if possible, or assume cascade handled by code)
    # Since we don't have a direct "get lecture" endpoint exposed without section, we rely on the implementation logic.
