import json
import subprocess
from os import environ

import redis
from bcrypt import checkpw, gensalt, hashpw
from fastapi_login.exceptions import InvalidCredentialsException
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, func
from flask_session import Session

from src.conf import config
from src.utils.logger import LOGGER

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/database.db'
app.secret_key = config['project']['secret']
db = SQLAlchemy(app)
login_manager = LoginManager(app=app)


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
    password = db.Column(db.String(120))
    created_at = db.Column(DateTime, default=func.now())
    last_modified = db.Column(DateTime, default=func.now())
    deleted_at = db.Column(DateTime)

    def set_password(self, password):
        self.password = get_password_hash(password)

    def check_password(self, password):
        return verify_password(plain_password=password, hashed_password=self.password)


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[email]['password']

    return user


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "Hello Boss!"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        payload = request.json
        login = User.query.filter_by(username=payload["username"]).first()
        if login.check_password(payload['password']):
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
    return home()


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
