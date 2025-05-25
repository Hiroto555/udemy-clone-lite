from fastapi.testclient import TestClient

from app.core.config import settings


def test_create_enrollment(client: TestClient, normal_user_token_headers: dict):
    # First, create another user who will be the instructor
    instructor_data = {
        "email": "instructor@example.com",
        "password": "instructorpass",
        "full_name": "Instructor User",
    }
    client.post(f"{settings.API_V1_STR}/auth/register", json=instructor_data)
    instructor_response = client.post(f"{settings.API_V1_STR}/auth/login", json=instructor_data)
    instructor_headers = {"Authorization": f"Bearer {instructor_response.json()['access_token']}"}
    
    # Instructor creates a course
    course_data = {
        "title": "Course to Enroll",
        "description": "Test course for enrollment",
        "price": 49.99,
        "is_published": True,
    }
    course_response = client.post(
        f"{settings.API_V1_STR}/courses/",
        headers=instructor_headers,
        json=course_data,
    )
    course_id = course_response.json()["id"]
    
    # Student enrolls in the course
    enrollment_data = {"course_id": course_id}
    response = client.post(
        f"{settings.API_V1_STR}/enrollments/",
        headers=normal_user_token_headers,
        json=enrollment_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["course_id"] == course_id
    assert "id" in content
    assert "enrolled_at" in content


def test_cannot_enroll_twice(client: TestClient, normal_user_token_headers: dict):
    # Create instructor and course
    instructor_data = {
        "email": "instructor2@example.com",
        "password": "instructorpass2",
        "full_name": "Instructor User 2",
    }
    client.post(f"{settings.API_V1_STR}/auth/register", json=instructor_data)
    instructor_response = client.post(f"{settings.API_V1_STR}/auth/login", json=instructor_data)
    instructor_headers = {"Authorization": f"Bearer {instructor_response.json()['access_token']}"}
    
    course_data = {
        "title": "Course for Double Enrollment Test",
        "description": "Test course",
        "price": 29.99,
        "is_published": True,
    }
    course_response = client.post(
        f"{settings.API_V1_STR}/courses/",
        headers=instructor_headers,
        json=course_data,
    )
    course_id = course_response.json()["id"]
    
    # First enrollment
    enrollment_data = {"course_id": course_id}
    client.post(
        f"{settings.API_V1_STR}/enrollments/",
        headers=normal_user_token_headers,
        json=enrollment_data,
    )
    
    # Try to enroll again
    response = client.post(
        f"{settings.API_V1_STR}/enrollments/",
        headers=normal_user_token_headers,
        json=enrollment_data,
    )
    assert response.status_code == 400
    assert "Already enrolled" in response.json()["detail"]


def test_cannot_enroll_in_own_course(client: TestClient, normal_user_token_headers: dict):
    # User creates a course
    course_data = {
        "title": "My Own Course",
        "description": "I created this",
        "price": 99.99,
        "is_published": True,
    }
    course_response = client.post(
        f"{settings.API_V1_STR}/courses/",
        headers=normal_user_token_headers,
        json=course_data,
    )
    course_id = course_response.json()["id"]
    
    # Try to enroll in own course
    enrollment_data = {"course_id": course_id}
    response = client.post(
        f"{settings.API_V1_STR}/enrollments/",
        headers=normal_user_token_headers,
        json=enrollment_data,
    )
    assert response.status_code == 400
    assert "Cannot enroll in your own course" in response.json()["detail"]


def test_read_my_enrollments(client: TestClient, normal_user_token_headers: dict):
    # Create instructor
    instructor_data = {
        "email": "instructor3@example.com",
        "password": "instructorpass3",
        "full_name": "Instructor User 3",
    }
    client.post(f"{settings.API_V1_STR}/auth/register", json=instructor_data)
    instructor_response = client.post(f"{settings.API_V1_STR}/auth/login", json=instructor_data)
    instructor_headers = {"Authorization": f"Bearer {instructor_response.json()['access_token']}"}
    
    # Create multiple courses and enroll
    for i in range(2):
        course_data = {
            "title": f"Course {i} for Enrollment List",
            "description": f"Course {i}",
            "price": 39.99 + i * 10,
            "is_published": True,
        }
        course_response = client.post(
            f"{settings.API_V1_STR}/courses/",
            headers=instructor_headers,
            json=course_data,
        )
        course_id = course_response.json()["id"]
        
        enrollment_data = {"course_id": course_id}
        client.post(
            f"{settings.API_V1_STR}/enrollments/",
            headers=normal_user_token_headers,
            json=enrollment_data,
        )
    
    # Get my enrollments
    response = client.get(
        f"{settings.API_V1_STR}/enrollments/my",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content) >= 2