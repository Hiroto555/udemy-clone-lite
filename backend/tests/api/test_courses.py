from fastapi.testclient import TestClient

from app.core.config import settings


def test_create_course(client: TestClient, normal_user_token_headers: dict):
    data = {
        "title": "Test Course",
        "description": "Test Description",
        "price": 99.99,
    }
    response = client.post(
        f"{settings.API_V1_STR}/courses/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == data["title"]
    assert content["description"] == data["description"]
    assert content["price"] == data["price"]
    assert content["is_published"] is False
    assert "id" in content


def test_read_course(client: TestClient, normal_user_token_headers: dict):
    # Create course
    data = {
        "title": "Test Course for Reading",
        "description": "Test Description",
        "price": 49.99,
        "is_published": True,
    }
    response = client.post(
        f"{settings.API_V1_STR}/courses/",
        headers=normal_user_token_headers,
        json=data,
    )
    course_id = response.json()["id"]
    
    # Read course
    response = client.get(
        f"{settings.API_V1_STR}/courses/{course_id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["id"] == course_id


def test_update_course(client: TestClient, normal_user_token_headers: dict):
    # Create course
    data = {
        "title": "Original Title",
        "description": "Original Description",
        "price": 99.99,
    }
    response = client.post(
        f"{settings.API_V1_STR}/courses/",
        headers=normal_user_token_headers,
        json=data,
    )
    course_id = response.json()["id"]
    
    # Update course
    update_data = {
        "title": "Updated Title",
        "price": 149.99,
        "is_published": True,
    }
    response = client.put(
        f"{settings.API_V1_STR}/courses/{course_id}",
        headers=normal_user_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["title"] == update_data["title"]
    assert content["price"] == update_data["price"]
    assert content["is_published"] is True


def test_delete_course(client: TestClient, normal_user_token_headers: dict):
    # Create course
    data = {
        "title": "Course to Delete",
        "description": "Will be deleted",
        "price": 19.99,
    }
    response = client.post(
        f"{settings.API_V1_STR}/courses/",
        headers=normal_user_token_headers,
        json=data,
    )
    course_id = response.json()["id"]
    
    # Delete course
    response = client.delete(
        f"{settings.API_V1_STR}/courses/{course_id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get(
        f"{settings.API_V1_STR}/courses/{course_id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 404


def test_read_my_courses(client: TestClient, normal_user_token_headers: dict):
    # Create multiple courses
    for i in range(3):
        data = {
            "title": f"My Course {i}",
            "description": f"Description {i}",
            "price": 29.99 + i * 10,
        }
        client.post(
            f"{settings.API_V1_STR}/courses/",
            headers=normal_user_token_headers,
            json=data,
        )
    
    # Get my courses
    response = client.get(
        f"{settings.API_V1_STR}/courses/my",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) >= 3