import os

from fastapi import HTTPException
from fastapi_login.exceptions import InvalidCredentialsException
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy

# from src.db import users_db
# from src.db.base import SESSION, database, users
# from src.utils.auth import LOGIN_MANAGER
from src.utils.logger import LOGGER

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/database.db'
db = SQLAlchemy(app)


class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120))
    password = db.Column(db.String(80))


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "Hello Boss!"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["username"]
        passw = request.form["password"]
        login = user.query.filter_by(username=uname, password=passw).first()
        if login is not None:
            # return redirect(url_for("index"))
            return {'access_token': 'abc123', 'token_type': 'bearer'}
    # return render_template("login.html")
    raise InvalidCredentialsException


# @app.route("/create", methods=['POST'])
# def create_user():
#     payload = request.form
#     user_id = users_db.get_user(email=payload.email)
#     # if len(user_id):
#     LOGGER.debug(f'[create_user] user id: {user_id}')
#     if user_id:
#         LOGGER.warning(f'{payload.email} already exists')
#         raise HTTPException(status_code=422, detail=f"Duplicate user {payload.email}")
#     user_id = users_db.post(payload)
#     response_object = {
#         "id": user_id,
#         "email": payload.email,
#         "first_name": payload.first_name,
#         "last_name": payload.last_name,
#         }
#     return response_object


# @app.route('/login', methods=['POST'])
# def login():
#     data = request.form
#     LOGGER.debug(f'data : {data}')
#     email = data['username']
#     password = data['password']
#     user = users_db.get_user(email=email, password_hash=password)
#     if not user:
#         raise InvalidCredentialsException
#     LOGGER.info(f'User found: {user}')
#     access_token = LOGIN_MANAGER.create_access_token(data=dict(sub=email))
#     return {'access_token': access_token, 'token_type': 'bearer'}


# @app.route('/login', methods=['POST'])
# def do_admin_login():
#     LOGGER.debug(f'request form: {request.form}')
#     if request.form['password'] == 'password' and request.form['username'] == 'admin':
#         session['logged_in'] = True
#     else:
#         flash('wrong password!')
#     LOGGER.info(f'==== LOGIN SUCCESS ===')
#     return home()


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()


# @app.route('/test')
# def test():
#     POST_USERNAME = "python"
#     POST_PASSWORD = "python"
#
#     # Session = sessionmaker(bind=engine)
#     # s = Session()
#     query = SESSION.query('users').filter(users.email.in_([POST_USERNAME]),
#                                          users.password.in_([POST_PASSWORD]))
#     result = query.first()
#     # query = users.select().where(eval(f'users.c.email') == f'{POST_USERNAME}')
#     # result = database.execute(query=query)
#     LOGGER.info(f'user found: {result}')
#     # result = query.first()
#     if result:
#         return "Object found"
#     else:
#         return "Object not found " + POST_USERNAME + " " + POST_PASSWORD


# TODO:
# - auth with db
# - store password in db with hash
# - authenticate encrypted password with SECRET


if __name__ == "__main__":
    db.create_all()
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='0.0.0.0', port=4000)
