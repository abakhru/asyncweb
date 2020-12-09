import json

from bcrypt import checkpw, gensalt, hashpw
from fastapi_login.exceptions import InvalidCredentialsException
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import LoginManager, current_user, logout_user
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, create_engine, func
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import scoped_session, sessionmaker, validates

from src.conf import config
from src.utils.logger import LOGGER

login_manager = LoginManager()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/database.db'
app.secret_key = config['project']['secret']
db = SQLAlchemy(app)
engine = create_engine('sqlite:////tmp/database.db')
Session = scoped_session(sessionmaker(bind=engine))


class ApiError(dict):
    def __init__(self, status, message):
        self.update({'status': status, 'message': message})

    def __call__(self):
        return self, self['status']


LoginRequired = ApiError(401, 'Login required')

UserAlreadyAuthenticated = ApiError(401, 'You are already logged in')

UserAlreadyExist = ApiError(401, 'A user with that email already exists')

InvalidCredentials = ApiError(401, 'Invalid email or password')

PasswordConfirmationInvalid = ApiError(401, 'Passwords do not match')

AccountNotActive = ApiError(401, 'User account not active')

NoUpdatesToMake = ApiError(401, 'No updates to make')

UserCreationFailure = ApiError(500, 'Could not create user')

CouldNotSendEmail = ApiError(500, 'Server could not process email request')

UserConfirmationRequired = ApiError(400, 'Please confirm your account')

MissingValidatorAction = ApiError(500, 'Missing validator action type')

InvalidToken = ApiError(400, 'Invalid validation token')

AccountNotActive = ApiError(401, 'Account is deactivated login to reactivate')

UserAlreadyConfirmed = ApiError(401, 'Account already confirmed')

InvalidPassword = ApiError(401, 'Password is incorrect')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def hash_password(password):
    """returns the salted and hashed password"""
    salt = gensalt(config['project']['salt_generation_rounds'])
    enc_pw = hashpw(password.encode(), salt)
    return enc_pw


def get_password_hash(password: str):
    return hash_password(password)


def verify_password(plain_password: str, hashed_password: bytes):
    return checkpw(password=plain_password.encode('utf-8'), hashed_password=hashed_password)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password_hash = db.Column(db.String(120))
    created_at = db.Column(DateTime, default=func.now())
    last_modified = db.Column(DateTime, default=func.now())
    deleted_at = db.Column(DateTime, nullable=True)

    # def __init__(self, email, password, **kwargs):
    #     self.email = email
    #     self.password = password
    #
    # def __repr__(self):
    #     return f"<User {self.id}:{self.email}>"
    #
    # @hybrid_property
    # def password(self):
    #     return self.password_hash
    #
    # @password.setter
    # def password(self, credentials):
    #     self.password_hash = hash_password(credentials)
    #
    # @hybrid_method
    # def authorize(self, credentials):
    #     return verify_password(credentials, self.password_hash)
    #
    # @validates('email')
    # def validate_identity(self, key, address):
    #     assert validate_email(address)
    #     return address

    def set_password(self, password):
        self.password_hash = get_password_hash(password)

    def check_password(self, password):
        return verify_password(plain_password=password, hashed_password=self.password_hash)


def db_available():
    """Check if database is available on network"""
    try:
        session = db.create_scoped_session()
        session.execute('SELECT 1')
        return True, "Database OK!"
    except Exception as e:
        return False, str(e)


def login_required(f):
    """ REST friendly decorator for enforcing authentication """
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return errors.LoginRequired()
        else:
            return f(*args, **kwargs)
    return wrapper


def user_is_active(f):
    """Decorator to deflect request from deactivated users"""
    def wrapper(*args, **kwargs):
        if current_user.is_active:
            return f(*args, **kwargs)
        else:
            return errors.AccountNotActive()
    return wrapper


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "Hello Boss!"


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        # return jsonify(message='Already logged in!')
        return redirect(url_for("index"))

    if request.method == "POST":
        payload = request.json
        logged_in_user = User.query.filter_by(username=payload["username"]).first()
        if logged_in_user.check_password(payload['password']):
            session['logged_in'] = True
            return {'access_token': 'acb123', 'token_type': 'bearer'}
        else:
            flash('wrong password!')
            raise InvalidCredentialsException
    else:
        return redirect(url_for("index"))
        # return render_template("login.html")


def get_user(**kwargs):
    for key, value in kwargs.items():
        LOGGER.debug(f'Querying: {key}="{value}"')
        # return User.query.filter_by(eval(f'{key}') = f'{value}').first()
        return User.query.filter_by(email=value).first()


@app.route("/create", methods=['POST'])
def create_user():
    LOGGER.debug(f'request.json:\n{json.dumps(request.json, indent=4)}')
    payload = request.json
    if not payload.get('username') or not payload.get('email') or not payload.get('password'):
        return jsonify(message='Please enter all the fields')
    user_id = get_user(email=payload['email'])
    if user_id:
        LOGGER.error(f'{payload["email"]} already exists')
        return jsonify(message="Duplicate user")
    new_user = User(username=payload["username"], email=payload["email"])
    new_user.set_password(payload['password'])
    db.session.add(new_user)
    db.session.commit()
    user_id = get_user(email=payload['email'])
    LOGGER.debug(f'[create_user] user id: {user_id.id}')
    response_object = {"id": user_id.id,
                       "email": user_id.email,
                       "username": user_id.username}
    return response_object


@app.route("/logout")
def logout():
    session['logged_in'] = False
    logout_user()
    flash('You are now logged out.', 'success')
    return redirect(url_for('index'))


# TODO:
# - auth with db
# - store password in db with hash
# - authenticate encrypted password with SECRET


if __name__ == "__main__":
    db.create_all()
    # admin = User(username='admin', email='admin@example.com')
    # admin.set_password(password='admin')
    # db.session.add(admin)
    # db.session.commit()
    # print(User.query.all())
    # LOGGER.info(f"{User.query.filter_by(username='admin').first()}")
    app.run(debug=True, host='0.0.0.0', port=8000)
