from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, defer

from src.api.models import User, UserAuthenticate, UserCreate, UserUpdate
from src.utils.auth import verify_password
from src.utils.logger import LOGGER


def check_username_password(db: Session, user: UserAuthenticate) -> Any:
    db_user_info = get_user(db, email=user.email)

    return verify_password(str(user.password), str(db_user_info.password))


def create_user(db: Session, user: UserCreate) -> Any:
    try:
        hashed_password = get_password_hash(str(user.password))
        db_user = User(email=user.email, password=hashed_password, name=user.name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as _:
        LOGGER.exception("create_user")
        return None


def update_user(db: Session, user_id: int, user: UserUpdate) -> Any:
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        db_user.name = user.name
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as _:
        LOGGER.exception("update_user")
        return None


def update_user_password(db: Session, email: str, password: str) -> Any:
    try:
        hashed_password = get_password_hash(password)
        db_user = db.query(User).filter(User.email == email).first()
        db_user.password = hashed_password
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as _:
        LOGGER.exception("update_user_password")
        return None


def delete_user(db: Session, user_id: int) -> Any:
    try:
        # db_user = db.query(User).filter(User.id == user_id)
        # db.delete(db_user)
        db.query(User).filter(User.id == user_id).delete()
        db.commit()
        # db.refresh(db_user)
        return True
    except SQLAlchemyError as _:
        LOGGER.exception("delete_user")
        return None


def verify_user(db: Session, email: str) -> Any:
    try:
        data = db.query(User.id, User.email).filter(User.email == email).first()
        return data
    except SQLAlchemyError as _:
        LOGGER.exception("verify_user")
        return None


def get_user(db: Session, email: str) -> Any:
    try:
        data = db.query(User).filter(User.email == email).options(defer('password')).first()
        return data
    except SQLAlchemyError as _:
        LOGGER.exception("get_user")
        return None


def get_user_id(db: Session, id: int) -> Any:
    try:
        data = db.query(User).filter(User.id == id).options(defer('password')).first()
        return data
    except SQLAlchemyError as _:
        LOGGER.exception("get_user_id")
        return None


# https://docs.sqlalchemy.org/en/13/orm/loading_columns.html#deferred
def get_all_user(db: Session) -> Any:
    try:
        data = db.query(User).options(defer('password')).all()
        return data
    except SQLAlchemyError as _:
        LOGGER.exception("get_all_user")
        return None