from typing import List, Optional
from sqlmodel import Session, select, func
from app.models.course import Review
from app.models.enrollment import Enrollment
from app.schemas.review import ReviewCreate


class CRUDReview:
    def create(
        self, db: Session, *, obj_in: ReviewCreate, user_id: int, course_id: int
    ) -> Optional[Review]:
        # Check if user already reviewed this course
        statement = select(Review).where(
            Review.user_id == user_id,
            Review.course_id == course_id
        )
        existing_review = db.exec(statement).first()
        if existing_review:
            return None  # User already reviewed this course
        
        # Check if user is enrolled in the course
        enrollment_statement = select(Enrollment).where(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id
        )
        enrollment = db.exec(enrollment_statement).first()
        if not enrollment:
            return None  # User not enrolled
        
        # Create the review
        db_obj = Review(
            **obj_in.model_dump(),
            user_id=user_id,
            course_id=course_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_course(
        self, db: Session, *, course_id: int, skip: int = 0, limit: int = 100
    ) -> List[Review]:
        statement = select(Review).where(
            Review.course_id == course_id
        ).offset(skip).limit(limit).order_by(Review.created_at.desc())
        return db.exec(statement).all()
    
    def get_average_rating(self, db: Session, *, course_id: int) -> Optional[float]:
        statement = select(func.avg(Review.rating)).where(
            Review.course_id == course_id
        )
        result = db.exec(statement).first()
        return float(result) if result else None


review = CRUDReview()