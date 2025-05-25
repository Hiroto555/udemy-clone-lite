from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api import deps
from app.crud import course as crud_course
from app.crud import enrollment as crud_enrollment
from app.models.user import User
from app.schemas.enrollment import Enrollment, EnrollmentCreate

router = APIRouter()


@router.post("/", response_model=Enrollment)
def create_enrollment(
    *,
    db: Session = Depends(deps.get_db),
    enrollment_in: EnrollmentCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new enrollment.
    """
    # Check if course exists and is published
    course = crud_course.get_course(db, course_id=enrollment_in.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if not course.is_published:
        raise HTTPException(status_code=400, detail="Course is not published")
    
    # Check if user is already enrolled
    existing_enrollment = crud_enrollment.get_enrollment_by_user_course(
        db, user_id=current_user.id, course_id=enrollment_in.course_id
    )
    if existing_enrollment:
        raise HTTPException(status_code=400, detail="Already enrolled in this course")
    
    # Check if user is the instructor
    if course.instructor_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot enroll in your own course")
    
    enrollment = crud_enrollment.create_enrollment(
        db, enrollment_in=enrollment_in, user_id=current_user.id
    )
    return enrollment


@router.get("/my", response_model=List[Enrollment])
def read_my_enrollments(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve current user's enrollments.
    """
    enrollments = crud_enrollment.get_enrollments_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return enrollments