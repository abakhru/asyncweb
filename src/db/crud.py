from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, defer

from src.db.base import pwd_context, session, users_table
from src.utils.logger import LOGGER
from src.utils.models import UserCreate, UserUpdate


def get_password_hash(password: str):
    return pwd_context.hash(password)


def __get_user_item__(**kwargs):
    for key, value in kwargs.items():
        return session.query(users_table).filter(eval(f'users_table.c.{key}') == f'{value}').first()


def create_user(db: Session, user: UserCreate) -> Any:
    try:
        db_user = users_table.insert().values(email=user.email,
                                              first_name=user.first_name,
                                              last_name=user.last_name,
                                              password=get_password_hash(str(user.password))
                                              )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as _:
        LOGGER.exception("create_user")
        return None


def update_user(db: Session, user_id: int, user: UserUpdate) -> Any:
    try:
        db_user = db.query(users_table).filter(users_table.c.id == user_id).first()
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
        db_user = db.query(users_table).filter(users_table.c.email == email).first()
        db_user.password = hashed_password
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as _:
        LOGGER.exception("update_user_password")
        return None


def delete_user(db: Session, user_id: int) -> Any:
    try:
        # db_user = db.query(users).filter(users.id == user_id)
        # db.delete(db_user)
        db.query(users_table).filter(users_table.c.id == user_id).delete()
        db.commit()
        # db.refresh(db_user)
        return True
    except SQLAlchemyError as _:
        LOGGER.exception("delete_user")
        return None


def verify_user(db: Session, email: str) -> Any:
    try:
        data = (
            db.query(users_table.c.id, users_table.c.email)
                .filter(users_table.c.email == email)
                .first()
        )
        return data
    except SQLAlchemyError as _:
        LOGGER.exception("verify_user")
        return None


def get_user_id(db: Session, id: int) -> Any:
    try:
        # data = (
        #     db.query(users_table)
        #     .filter(users_table.c.id == id)
        #     .options(defer('password_hash'))
        #     .first()
        # )
        data = __get_user_item__(id=id)
        return data
    except SQLAlchemyError as _:
        LOGGER.exception("get_user_id")
        return None


# https://docs.sqlalchemy.org/en/13/orm/loading_columns.html#deferred
def get_all_user(db: Session) -> Any:
    try:
        data = db.query(users_table).options(defer('password')).all()
        return data
    except SQLAlchemyError as _:
        LOGGER.exception("get_all_user")
        return None
