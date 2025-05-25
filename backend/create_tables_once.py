# create_tables_once.py  ← backend 直下に新規作成

from sqlmodel import SQLModel, create_engine

engine = create_engine("sqlite:///./sql_app.db", echo=True)

if __name__ == "__main__":
    SQLModel.metadata.create_all(engine)

