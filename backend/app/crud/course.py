from typing import List, Optional

from sqlmodel import Session, select, or_

from app.models.course import Course, Tag, CourseTagLink
from app.schemas.course import CourseCreate, CourseUpdate


def get_course(db: Session, course_id: int) -> Optional[Course]:
    return db.get(Course, course_id)


def get_courses(
    db: Session, *, skip: int = 0, limit: int = 100, instructor_id: Optional[int] = None
) -> List[Course]:
    statement = select(Course)
    if instructor_id:
        statement = statement.where(Course.instructor_id == instructor_id)
    statement = statement.offset(skip).limit(limit)
    return db.exec(statement).all()


def get_published_courses(
    db: Session, 
    *, 
    skip: int = 0, 
    limit: int = 100,
    query: Optional[str] = None,
    tag_slug: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None
) -> List[Course]:
    statement = select(Course).where(Course.is_published == True)
    
    # Search by title or description
    if query:
        search_term = f"%{query}%"
        statement = statement.where(
            or_(
                Course.title.ilike(search_term),
                Course.description.ilike(search_term)
            )
        )
    
    # Filter by tag
    if tag_slug:
        # Join with Tag through CourseTagLink
        statement = (
            statement
            .join(CourseTagLink, Course.id == CourseTagLink.course_id)
            .join(Tag, CourseTagLink.tag_id == Tag.id)
            .where(Tag.slug == tag_slug)
        )
    
    # Filter by price range
    if price_min is not None:
        statement = statement.where(Course.price >= price_min)
    
    if price_max is not None:
        statement = statement.where(Course.price <= price_max)
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    
    # Execute and return distinct results (important when joining with tags)
    return db.exec(statement.distinct()).all()


def create_course(db: Session, *, course_in: CourseCreate, instructor_id: int) -> Course:
    db_course = Course(
        **course_in.model_dump(),
        instructor_id=instructor_id,
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def update_course(
    db: Session, *, db_course: Course, course_update: CourseUpdate
) -> Course:
    course_data = course_update.model_dump(exclude_unset=True)
    for key, value in course_data.items():
        setattr(db_course, key, value)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def delete_course(db: Session, *, course_id: int) -> Optional[Course]:
    course = db.get(Course, course_id)
    if course:
        db.delete(course)
        db.commit()
    return course