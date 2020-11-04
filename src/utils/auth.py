# """ Utility for all things authentication related """
from typing import Any

from bcrypt import gensalt, hashpw
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.conf import config
from src.db import crud
from src.db.base import pwd_context, users_table
from src.utils.logger import LOGGER
from src.utils.models import User, UserAuthenticate


def check_username_password(db: Session, user: UserAuthenticate) -> Any:
    # db_user_info = get_user(db, email=user.email)
    db_user_info = crud.__get_user_item__(email=user.email)
    return verify_password(str(user.password), str(db_user_info.password_hash))


def find_user(session, username, password):
    """
    Checks for a user with the given username, password combination
    """
    user_ = session.query(users_table).filter_by(name=username).first()
    if user_:
        hashed_password = user_.password
        hashed_password = hashed_password.encode("utf-8")
        if hashpw(password.encode('utf-8'), hashed_password) == hashed_password:
            user = User()
            user.id = username
            return user
    return None


def get_user(db: Session, email: str) -> Any:
    try:
        # data = db.query(users_table).filter_by(email=email).options(defer('password_hash')).first()
        data = crud.__get_user_item__(email=email)
        return data
    except SQLAlchemyError as _:
        LOGGER.exception("get_user")
        return None


def hash_password(password):
    """
    returns the salted and hashed password
    """
    salt = gensalt(config['project']['salt_generation_rounds'])
    enc_pw = hashpw(password, salt)
    return str(enc_pw, encoding='utf-8')


def encrypt_password(password, salt_rounds=config['project']['salt_generation_rounds']):
    return hashpw(password.encode('utf-8'), gensalt(salt_rounds)).decode('utf-8')


def hash_password_preprocess(obj):
    if 'password' not in obj:
        raise Exception("No password in object.")
    obj['password_hash'] = encrypt_password(obj['password'])
    del obj['password']
    return obj


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    # return checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    LOGGER.info(f'plain: {plain_password}')
    LOGGER.info(f'hashed: {hashed_password}')
    # return pwd_context.verify(plain_password, hashed_password)
    return plain_password == hashed_password
