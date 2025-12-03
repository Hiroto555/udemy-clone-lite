from typing import List, Optional
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models.curriculum import Section, Lecture
from app.schemas.curriculum import SectionCreate, SectionUpdate, LectureCreate, LectureUpdate

def create_section(db: Session, *, section_in: SectionCreate, course_id: int) -> Section:
    db_obj = Section(**section_in.model_dump(), course_id=course_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_section(db: Session, section_id: int) -> Optional[Section]:
    return db.get(Section, section_id)

def get_sections_by_course(db: Session, course_id: int) -> List[Section]:
    statement = (
        select(Section)
        .where(Section.course_id == course_id)
        .options(selectinload(Section.lectures))
        .order_by(Section.order)
    )
    return db.exec(statement).all()

def update_section(db: Session, *, db_obj: Section, obj_in: SectionUpdate) -> Section:
    section_data = obj_in.model_dump(exclude_unset=True)
    for key, value in section_data.items():
        setattr(db_obj, key, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_section(db: Session, *, section_id: int) -> Optional[Section]:
    section = db.get(Section, section_id)
    if not section:
        return None

    # Delete all lectures in the section first (cascade manual if not DB configured)
    # SQLModel relationships don't auto-cascade delete in python side unless configured on DB level,
    # but let's just delete the section and rely on DB cascade or manual delete.
    # For SQLite default might not cascade without configuration.
    # Let's manually delete lectures to be safe.
    for lecture in section.lectures:
        db.delete(lecture)

    db.delete(section)
    db.commit()
    return section

# Lecture CRUD
def create_lecture(db: Session, *, lecture_in: LectureCreate, section_id: int) -> Lecture:
    db_obj = Lecture(**lecture_in.model_dump(), section_id=section_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_lecture(db: Session, lecture_id: int) -> Optional[Lecture]:
    return db.get(Lecture, lecture_id)

def get_lectures_by_section(db: Session, section_id: int) -> List[Lecture]:
    statement = select(Lecture).where(Lecture.section_id == section_id).order_by(Lecture.order)
    return db.exec(statement).all()

def update_lecture(db: Session, *, db_obj: Lecture, obj_in: LectureUpdate) -> Lecture:
    lecture_data = obj_in.model_dump(exclude_unset=True)
    for key, value in lecture_data.items():
        setattr(db_obj, key, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_lecture(db: Session, *, lecture_id: int) -> Optional[Lecture]:
    lecture = db.get(Lecture, lecture_id)
    if not lecture:
        return None
    db.delete(lecture)
    db.commit()
    return lecture
