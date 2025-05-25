# app/db/session.py
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)

def get_session() -> Session:
    with Session(engine) as session:
        yield session

def create_db_and_tables() -> None:
    """必ず呼び出して全テーブルを作成する"""
    SQLModel.metadata.create_all(engine)

