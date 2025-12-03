from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api import deps
from app.crud import course as crud_course
from app.crud import review as crud_review
from app.crud import curriculum as crud_curriculum
from app.crud import enrollment as crud_enrollment
from app.models.user import User
from app.schemas.course import Course, CourseCreate, CourseUpdate
from app.schemas.review import Review, ReviewCreate, ReviewRead
from app.schemas.curriculum import SectionCreate, SectionUpdate, SectionRead
from app.schemas.curriculum import LectureCreate, LectureUpdate, LectureRead

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


# Curriculum Endpoints

@router.post("/{course_id}/sections", response_model=SectionRead)
def create_course_section(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    section_in: SectionCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create a section for a course.
    Only instructor can create sections.
    """
    course = crud_course.get_course(db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if course.instructor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    section = crud_curriculum.create_section(db, section_in=section_in, course_id=course_id)
    return section


@router.get("/{course_id}/sections", response_model=List[SectionRead])
def read_course_sections(
    *,
    db: Session = Depends(deps.get_db),
    course_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get all sections for a course (including lectures).
    Only enrolled users, the instructor, or superusers can access this.
    """
    course = crud_course.get_course(db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if user has access
    has_access = False

    # 1. Superuser
    if current_user.is_superuser:
        has_access = True

    # 2. Instructor
    elif course.instructor_id == current_user.id:
        has_access = True

    # 3. Enrolled Student (only if published)
    elif course.is_published:
        enrollment = crud_enrollment.get_enrollment_by_user_course(
            db, user_id=current_user.id, course_id=course_id
        )
        if enrollment:
            has_access = True

    if not has_access:
        raise HTTPException(status_code=403, detail="You do not have access to this course content")

    sections = crud_curriculum.get_sections_by_course(db, course_id=course_id)
    return sections


@router.put("/sections/{section_id}", response_model=SectionRead)
def update_section(
    *,
    db: Session = Depends(deps.get_db),
    section_id: int,
    section_in: SectionUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a section.
    """
    section = crud_curriculum.get_section(db, section_id=section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    course = crud_course.get_course(db, course_id=section.course_id)
    if course.instructor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    section = crud_curriculum.update_section(db, db_obj=section, obj_in=section_in)
    return section


@router.delete("/sections/{section_id}", response_model=SectionRead)
def delete_section(
    *,
    db: Session = Depends(deps.get_db),
    section_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a section.
    """
    section = crud_curriculum.get_section(db, section_id=section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    course = crud_course.get_course(db, course_id=section.course_id)
    if course.instructor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    section = crud_curriculum.delete_section(db, section_id=section_id)
    return section


@router.post("/sections/{section_id}/lectures", response_model=LectureRead)
def create_section_lecture(
    *,
    db: Session = Depends(deps.get_db),
    section_id: int,
    lecture_in: LectureCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create a lecture for a section.
    """
    section = crud_curriculum.get_section(db, section_id=section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")

    course = crud_course.get_course(db, course_id=section.course_id)
    if course.instructor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    lecture = crud_curriculum.create_lecture(db, lecture_in=lecture_in, section_id=section_id)
    return lecture


@router.put("/lectures/{lecture_id}", response_model=LectureRead)
def update_lecture(
    *,
    db: Session = Depends(deps.get_db),
    lecture_id: int,
    lecture_in: LectureUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a lecture.
    """
    lecture = crud_curriculum.get_lecture(db, lecture_id=lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    section = crud_curriculum.get_section(db, section_id=lecture.section_id)
    course = crud_course.get_course(db, course_id=section.course_id)

    if course.instructor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    lecture = crud_curriculum.update_lecture(db, db_obj=lecture, obj_in=lecture_in)
    return lecture


@router.delete("/lectures/{lecture_id}", response_model=LectureRead)
def delete_lecture(
    *,
    db: Session = Depends(deps.get_db),
    lecture_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a lecture.
    """
    lecture = crud_curriculum.get_lecture(db, lecture_id=lecture_id)
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    section = crud_curriculum.get_section(db, section_id=lecture.section_id)
    course = crud_course.get_course(db, course_id=section.course_id)

    if course.instructor_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    lecture = crud_curriculum.delete_lecture(db, lecture_id=lecture_id)
    return lecture
