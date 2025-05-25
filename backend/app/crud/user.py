from typing import Optional

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    return db.exec(statement).first()


def create_user(db: Session, user_create: UserCreate) -> User:
    db_user = User(
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
        full_name=user_create.full_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, db_user: User, user_update: UserUpdate) -> User:
    user_data = user_update.model_dump(exclude_unset=True)
    if "password" in user_data:
        hashed_password = get_password_hash(user_data["password"])
        del user_data["password"]
        user_data["hashed_password"] = hashed_password
    for key, value in user_data.items():
        setattr(db_user, key, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def is_active(user: User) -> bool:
    return user.is_active


def is_superuser(user: User) -> bool:
    return user.is_superuser