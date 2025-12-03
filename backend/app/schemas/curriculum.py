from typing import List, Optional
from pydantic import BaseModel

class LectureBaseSchema(BaseModel):
    title: str
    description: Optional[str] = None
    content_url: Optional[str] = None
    content_text: Optional[str] = None
    video_duration: Optional[int] = None
    order: Optional[int] = 0
    is_preview: Optional[bool] = False

class LectureCreate(LectureBaseSchema):
    pass

class LectureUpdate(LectureBaseSchema):
    title: Optional[str] = None
    order: Optional[int] = None

class LectureRead(LectureBaseSchema):
    id: int
    section_id: int

    class ConfigDict:
        from_attributes = True

class SectionBaseSchema(BaseModel):
    title: str
    order: Optional[int] = 0

class SectionCreate(SectionBaseSchema):
    pass

class SectionUpdate(SectionBaseSchema):
    title: Optional[str] = None
    order: Optional[int] = None

class SectionRead(SectionBaseSchema):
    id: int
    course_id: int
    lectures: List[LectureRead] = []

    class ConfigDict:
        from_attributes = True
