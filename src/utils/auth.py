'''
Utilitiy for all things authentication related
'''
from base64 import b64decode
import flask_login
from bcrypt import hashpw, gensalt

# from indicators.db.models.user import User as UserModel
# from indicators.db.session import SESSION
# from indicators import config
from src.db.base import SESSION

LOGIN_MANAGER = flask_login.LoginManager()


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
    user_ = session.query(UserModel).filter_by(name=name).first()

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
    user_ = session.query(UserModel).filter_by(name=username).first()
    if user_:
        hashed_password = user_.password
        hashed_password = hashed_password.encode("utf-8")

        if hashpw(password.encode('utf-8'), hashed_password) == hashed_password:
            user = User()
            # pylint: disable=invalid-name,attribute-defined-outside-init
            user.id = username
            return user

    return None


def get_user(session, username):
    """
    returns the user properties for the user with the given username, if there is one
    """
    user = session.query(UserModel).filter_by(name=username).first()

    if user:
        return user.id, user.name, user.password

    return None, None, None


def hash_password(password):
    """
    returns the salted and hashed password
    """
    salt = gensalt(config.SALT_ROUNDS)
    enc_pw = hashpw(password, salt)
    return str(enc_pw, encoding='utf-8')
