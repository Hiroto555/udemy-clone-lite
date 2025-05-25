from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.api import deps
from app.crud import tag as crud_tag
from app.schemas.tag import Tag, TagCreate
from app.schemas.course import Course

router = APIRouter()


@router.get("/", response_model=List[Tag])
def read_tags(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all tags.
    """
    tags = crud_tag.tag.get_multi(db, skip=skip, limit=limit)
    return tags


@router.get("/{slug}/courses", response_model=List[Course])
def read_tag_courses(
    *,
    db: Session = Depends(deps.get_db),
    slug: str,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all published courses for a specific tag.
    """
    tag = crud_tag.tag.get_by_slug(db, slug=slug)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    courses = crud_tag.tag.get_courses_by_tag(
        db, tag_slug=slug, skip=skip, limit=limit
    )
    return courses