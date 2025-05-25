from typing import List, Optional
from sqlmodel import Session, select
from app.models.course import Tag, Course, CourseTagLink
from app.schemas.tag import TagCreate


class CRUDTag:
    def create(self, db: Session, *, obj_in: TagCreate) -> Tag:
        db_obj = Tag(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, tag_id: int) -> Optional[Tag]:
        return db.get(Tag, tag_id)
    
    def get_by_slug(self, db: Session, slug: str) -> Optional[Tag]:
        statement = select(Tag).where(Tag.slug == slug)
        return db.exec(statement).first()
    
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Tag]:
        statement = select(Tag).offset(skip).limit(limit)
        return db.exec(statement).all()
    
    def get_courses_by_tag(
        self, db: Session, *, tag_slug: str, skip: int = 0, limit: int = 100
    ) -> List[Course]:
        statement = (
            select(Course)
            .join(CourseTagLink)
            .join(Tag)
            .where(Tag.slug == tag_slug)
            .where(Course.is_published == True)
            .offset(skip)
            .limit(limit)
        )
        return db.exec(statement).all()


tag = CRUDTag()