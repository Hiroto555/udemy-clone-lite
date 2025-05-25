from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class EnrollmentBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")
    course_id: int = Field(foreign_key="course.id")


class Enrollment(EnrollmentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    progress: float = Field(default=0.0, ge=0.0, le=100.0)

    