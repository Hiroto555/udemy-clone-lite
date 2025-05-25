from sqlmodel import SQLModel, Session, create_engine
from passlib.context import CryptContext
from app.models.user import User  # 循環参照を避けるためローカル import
from sqlmodel import select  


DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(DATABASE_URL, echo=True)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db() -> None:
    # 1️⃣ ここで必ず全テーブルを作成
    SQLModel.metadata.create_all(engine)

    # 2️⃣ 初期ユーザーを投入
    with Session(engine) as session:
        admin = session.exec(
    select(User).where(User.email == "admin@example.com")
).first()
        if not admin:
            user = User(
                email="admin@example.com",
                full_name="Admin",
                hashed_password=pwd_context.hash("changeme123"),
                is_active=True,
                is_superuser=True,
            )
            session.add(user)
            session.commit()

if __name__ == "__main__":
    init_db()


