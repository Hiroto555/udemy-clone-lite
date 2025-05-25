from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api import deps
from app.crud import course as crud_course
from app.crud import review as crud_review
from app.models.user import User
from app.schemas.course import Course, CourseCreate, CourseUpdate
from app.schemas.review import Review, ReviewCreate, ReviewRead

router = APIRouter()


@router.get("/", response_model=List[Course])
def read_courses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    q: Optional[str] = Query(None, description="Search query for title and description"),
    tag: Optional[str] = Query(None, description="Filter by tag slug"),
    price_min: Optional[float] = Query(None, ge=0, description="Minimum price"),
    price_max: Optional[float] = Query(None, ge=0, description="Maximum price"),
) -> Any:
    """
    Retrieve courses with optional search and filters.
    """
    # Public endpoint - only show published courses
    courses = crud_course.get_published_courses(
        db, 
        skip=skip, 
        limit=limit,
        query=q,
        tag_slug=tag,
        price_min=price_min,
        price_max=price_max
    )
    return courses


@router.get("/my", response_model=List[Course])
def read_my_courses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve current user's courses.
    """
    courses = crud_course.get_courses(
        db, skip=skip, limit=limit, instructor_id=current_user.id
    )
    return courses


@router.post("/", response_model=Course)
def create_course(
    *,
    db: Session = Depends(deps.get_db),
    course_in: CourseCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new course.
    """
    course = crud_course.create_course(
        db, course_in=course_in, instructor_id=current_user.id
    )
    return course


@router.get("/{course_id}", response_model=Course)
def read_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get course by ID.
    """
    course = crud_course.get_course(db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if not course.is_published and not current_user.is_superuser:
        if course.instructor_id != current_user.id:
            raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.put("/{course_id}", response_model=Course)
def update_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    course_in: CourseUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a course.
    """
    course = crud_course.get_course(db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.instructor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    course = crud_course.update_course(db, db_course=course, course_update=course_in)
    return course


@router.delete("/{course_id}", response_model=Course)
def delete_course(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a course.
    """
    course = crud_course.get_course(db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.instructor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    course = crud_course.delete_course(db, course_id=course_id)
    return course


@router.post("/{course_id}/reviews", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
def create_course_review(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    review_in: ReviewCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create a review for a course.
    User must be enrolled in the course and can only review once.
    """
    # Check if course exists and is published
    course = crud_course.get_course(db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if not course.is_published:
        raise HTTPException(status_code=404, detail="Course not found")
    
    review = crud_review.review.create(
        db,
        obj_in=review_in,
        user_id=current_user.id,
        course_id=course_id
    )
    if not review:
        raise HTTPException(
            status_code=400, 
            detail="You must be enrolled in the course and can only review once"
        )
    return review


@router.get("/{course_id}/reviews", response_model=List[ReviewRead])
def read_course_reviews(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    skip: int = 0,
    limit: int = 20,
) -> Any:
    """
    Get all reviews for a course.
    Public endpoint - no authentication required.
    """
    # Check if course exists and is published
    course = crud_course.get_course(db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if not course.is_published:
        raise HTTPException(status_code=404, detail="Course not found")
    
    reviews = crud_review.review.get_by_course(
        db,
        course_id=course_id,
        skip=skip,
        limit=limit
    )
    return reviews


