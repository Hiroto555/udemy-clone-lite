from typing import List, Optional

from sqlmodel import Session, select

from app.models.enrollment import Enrollment
from app.schemas.enrollment import EnrollmentCreate


def get_enrollment(db: Session, enrollment_id: int) -> Optional[Enrollment]:
    return db.get(Enrollment, enrollment_id)


def get_enrollment_by_user_course(
    db: Session, *, user_id: int, course_id: int
) -> Optional[Enrollment]:
    statement = select(Enrollment).where(
        Enrollment.user_id == user_id,
        Enrollment.course_id == course_id
    )
    return db.exec(statement).first()


def get_enrollments_by_user(
    db: Session, *, user_id: int, skip: int = 0, limit: int = 100
) -> List[Enrollment]:
    statement = select(Enrollment).where(
        Enrollment.user_id == user_id
    ).offset(skip).limit(limit)
    return db.exec(statement).all()


def get_enrollments_by_course(
    db: Session, *, course_id: int, skip: int = 0, limit: int = 100
) -> List[Enrollment]:
    statement = select(Enrollment).where(
        Enrollment.course_id == course_id
    ).offset(skip).limit(limit)
    return db.exec(statement).all()


def create_enrollment(
    db: Session, *, enrollment_in: EnrollmentCreate, user_id: int
) -> Enrollment:
    db_enrollment = Enrollment(
        **enrollment_in.model_dump(),
        user_id=user_id,
    )
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment