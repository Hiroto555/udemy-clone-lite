from sqlmodel import SQLModel, Session, create_engine
from passlib.context import CryptContext
from app.models.user import User   # ここだけ他に依存

DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(DATABASE_URL, echo=True)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db() -> None:
    # ① テーブルを作る ── これが最優先
    SQLModel.metadata.create_all(engine)

    # ② 初期ユーザーを突っ込む
    with Session(engine) as session:
        admin = session.exec(User.select().where(User.email == "admin@example.com")).first()
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


