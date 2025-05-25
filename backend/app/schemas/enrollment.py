from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EnrollmentBase(BaseModel):
    course_id: int


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentInDBBase(EnrollmentBase):
    id: int
    user_id: int
    enrolled_at: datetime
    completed_at: Optional[datetime] = None
    progress: float = 0.0

    class Config:
        from_attributes = True


class Enrollment(EnrollmentInDBBase):
    pass