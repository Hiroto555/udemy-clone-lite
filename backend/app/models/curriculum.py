from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .course import Course


class LectureBase(SQLModel):
    title: str = Field(index=True)
    description: Optional[str] = None
    content_url: Optional[str] = None
    content_text: Optional[str] = None
    video_duration: Optional[int] = None  # In seconds
    order: int = Field(default=0)
    is_preview: bool = False


class Lecture(LectureBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    section_id: int = Field(foreign_key="section.id")

    # Relationships
    section: "Section" = Relationship(back_populates="lectures")


class SectionBase(SQLModel):
    title: str = Field(index=True)
    order: int = Field(default=0)


class Section(SectionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="course.id")

    # Relationships
    course: "Course" = Relationship(back_populates="sections")
    lectures: List[Lecture] = Relationship(back_populates="section")
