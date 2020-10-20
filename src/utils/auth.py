# """ Utility for all things authentication related """
#
from base64 import b64decode

import flask_login
from bcrypt import checkpw, gensalt, hashpw

# from indicators.db.models.user import User as UserModel
# from indicators.db.session import SESSION
# from indicators import config
from fastapi_login import LoginManager

from src import configuration
from src.configuration import SECRET
from src.db.base import SESSION, users


LOGIN_MANAGER = LoginManager(secret=SECRET, tokenUrl='/auth/token')


# pylint: disable=too-few-public-methods
class User(flask_login.UserMixin):
    """
    Placeholder class to wrap the flask UserMixin class
    """


@LOGIN_MANAGER.user_loader
def user_loader(name):
    """
    get_or_create user
    param: name string value or the user to be got or created
    """

    session = SESSION()
    user_ = session.query(users).filter_by(name=name).first()

    if user_ is None:
        return None

    user = User()
    # pylint: disable=invalid-name,attribute-defined-outside-init
    user.id = name

    return user


@LOGIN_MANAGER.request_loader
def request_loader(request):
    """
    Checks for valid auth on each incoming request
    """
    session = SESSION()

    # first, try to login using the url args
    username = request.args.get('username')
    password = request.args.get('password')
    if username and password:
        return find_user(session, username, password)

    # next, try to login using Basic Auth
    basic_auth = request.headers.get('Authorization')
    if basic_auth:
        basic_auth = b64decode(basic_auth.replace('Basic ', '', 1))
        username, password = basic_auth.decode('utf-8').split(':')
        return find_user(session, username, password)

    # finally, return None if both methods did not login the user
    return None


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
    salt = gensalt(configuration.SALT_GENERATION_ROUNDS)
    enc_pw = hashpw(password, salt)
    return str(enc_pw, encoding='utf-8')


def encrypt_password(password, salt_rounds=configuration.SALT_GENERATION_ROUNDS):
    return hashpw(password.encode('utf-8'), gensalt(salt_rounds)).decode('utf-8')


def verify_password(password, hashed_password):
    return checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def reset_password_lockout(user_id=None):
    user = db.reset_password_lockout(user_id=user_id)
    return scrub_user(user)


def check_password_history(kwargs):
    user_id = kwargs.get('user_id')
    password = kwargs.get('password')
    passwords = db.get_password_history(user_id=user_id)
    for password_entry in passwords:
        if password_entry['password_hash'].startswith(configuration.DEFAULT_PASSWORD_PREFIX):
            continue
        if security.verify_password(password, password_entry['password_hash']):
            raise web.AuthenticationError(
                {
                    "message": "New passwords must be different than any of the previous "
                               f"{configuration.PASSWORD_HISTORY_LOOKBACK} passwords that were used.",
                    }
                )
    return kwargs


def hash_password_preprocess(obj):
    if 'password' not in obj:
        raise Exception("No password in object.")
    obj['password_hash'] = encrypt_password(obj['password'])
    del obj['password']
    return obj
