from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    pass


class ReviewInDBBase(ReviewBase):
    id: int
    course_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Review(ReviewInDBBase):
    pass


class ReviewRead(Review):
    user_email: Optional[str] = None


class ReviewUpdate(ReviewBase):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None