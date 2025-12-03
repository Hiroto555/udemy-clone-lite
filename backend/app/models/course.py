from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .user import User
    from .curriculum import Section


class CourseTagLink(SQLModel, table=True):
    """Many-to-many relationship between Course and Tag"""
    __tablename__ = "course_tag_link"
    
    course_id: Optional[int] = Field(
        default=None, foreign_key="course.id", primary_key=True
    )
    tag_id: Optional[int] = Field(
        default=None, foreign_key="tag.id", primary_key=True
    )


class TagBase(SQLModel):
    name: str = Field(unique=True, index=True)
    slug: str = Field(unique=True, index=True)


class Tag(TagBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationship
    courses: List["Course"] = Relationship(back_populates="tags", link_model=CourseTagLink)


class ReviewBase(SQLModel):
    course_id: int = Field(foreign_key="course.id")
    user_id: int = Field(foreign_key="user.id")
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class Review(ReviewBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    course: Optional["Course"] = Relationship(back_populates="reviews")
    user: Optional["User"] = Relationship()


class CourseBase(SQLModel):
    title: str = Field(index=True)
    description: Optional[str] = None
    price: float = Field(ge=0)
    instructor_id: int = Field(foreign_key="user.id")
    is_published: bool = False


class Course(CourseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    instructor: Optional["User"] = Relationship()
    tags: List[Tag] = Relationship(back_populates="courses", link_model=CourseTagLink)
    reviews: List[Review] = Relationship(back_populates="course")
    sections: List["Section"] = Relationship(back_populates="course")