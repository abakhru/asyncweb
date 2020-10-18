import os

from fastapi import HTTPException
from fastapi_login.exceptions import InvalidCredentialsException
from flask import Flask, flash, render_template, request, session

from src.db import users_db
from src.db.base import SESSION, database, users
from src.utils.auth import LOGIN_MANAGER
from src.utils.logger import LOGGER

app = Flask(__name__)


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "Hello Boss!"


@app.route("/create", methods=['POST'])
def create_user():
    payload = request.form
    user_id = users_db.get_user(email=payload.email)
    # if len(user_id):
    LOGGER.debug(f'[create_user] user id: {user_id}')
    if user_id:
        LOGGER.warning(f'{payload.email} already exists')
        raise HTTPException(status_code=422, detail=f"Duplicate user {payload.email}")
    user_id = users_db.post(payload)
    response_object = {
        "id": user_id,
        "email": payload.email,
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        }
    return response_object


@app.route('/login', methods=['POST'])
def login():
    # data = request.form.copy()
    data = request.form
    LOGGER.debug(f'data : {data}')
    # import pdb;pdb.set_trace()
    email = data['username']
    password = data['password']
    user_id = users_db.get_user(email=email)
    LOGGER.info(f'User found: {user_id}')
    user = users_db.get(user_id)
    if any([not user,
            password != user['password']]):
        raise InvalidCredentialsException

    access_token = LOGIN_MANAGER.create_access_token(data=dict(sub=email))
    return {'access_token': access_token, 'token_type': 'bearer'}


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


@app.route('/test')
def test():
    POST_USERNAME = "python"
    POST_PASSWORD = "python"

    # Session = sessionmaker(bind=engine)
    # s = Session()
    query = SESSION.query('users').filter(users.email.in_([POST_USERNAME]),
                                         users.password.in_([POST_PASSWORD]))
    result = query.first()
    # query = users.select().where(eval(f'users.c.email') == f'{POST_USERNAME}')
    # result = database.execute(query=query)
    LOGGER.info(f'user found: {result}')
    # result = query.first()
    if result:
        return "Object found"
    else:
        return "Object not found " + POST_USERNAME + " " + POST_PASSWORD


# TODO:
# - auth with db
# - store password in db with hash
# - authenticate encrypted password with SECRET


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='0.0.0.0', port=4000)
