# """ Utility for all things authentication related """

from bcrypt import gensalt, hashpw
from fastapi_login import LoginManager
from passlib.context import CryptContext

from src.api.models import User
from src.conf import config
from src.db.base import users

login = LoginManager(secret=config['project']['secret'], tokenUrl='/auth/token')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def find_user(session, username, password):
    """
    Checks for a user with the given username, password combination
    """
    user_ = session.query(users).filter_by(name=username).first()
    if user_:
        hashed_password = user_.password
        hashed_password = hashed_password.encode("utf-8")
        if hashpw(password.encode('utf-8'), hashed_password) == hashed_password:
            user = User()
            user.id = username
            return user
    return None


def get_user(session, username):
    """
    returns the user properties for the user with the given username, if there is one
    """
    user = session.query(users).filter_by(name=username).first()
    if user:
        return user.id, user.name, user.password
    return None, None, None


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
    return pwd_context.verify(plain_password, hashed_password)
