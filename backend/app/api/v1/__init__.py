from fastapi import APIRouter

from app.api.v1 import auth, courses, enrollments, tags

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(enrollments.router, prefix="/enrollments", tags=["enrollments"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])