from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.schemas.tag import Tag


class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    is_published: bool = False


class CourseCreate(CourseBase):
    pass 


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_published: Optional[bool] = None


class CourseInDBBase(CourseBase):
    id: int
    instructor_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Course(CourseInDBBase):
    pass


class CourseRead(Course):
    tags: List[Tag] = []
    average_rating: Optional[float] = None