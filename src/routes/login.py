from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from flask import render_template
from jwt.exceptions import JWTException
from jwt.utils import get_int_from_datetime
from sqlalchemy.orm import Session
from starlette import status

from src.db.base import session
from src.utils import auth
from src.utils.logger import LOGGER
from src.utils.models import UserAuthenticate, UserLoginSchema, UserPasswordReset
from src.auth.access_token import access_token
from src.conf import config
from src.db import crud, users_db
from src.utils.deps import get_db
from src.utils.email_util import send_reset_password_email
from src.utils.response_schemas import general_responses, get_token_response

router = APIRouter()


@router.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return JSONResponse(status_code=200, content={"message": "Welcome to Demo Server"})

# @router.post("/login", response_model=UserLoginSchema, status_code=201)
# async def login(payload: UserLoginSchema):
#     pass


@router.post('/login')
# def login(data: OAuth2PasswordRequestForm = Depends()):
def login(user: UserAuthenticate, db: Session = Depends(get_db)) -> JSONResponse:
    db_user = auth.get_user(db, email=user.email)
    if db_user is None:
        return JSONResponse(status_code=400, content={"message": "Invalid Credentials"})
    else:
        is_password_correct = auth.check_username_password(db, user)
        if is_password_correct is False:
            return JSONResponse(status_code=400, content={"message": "Invalid Credentials"})
        else:
            access_token_expires = timedelta(minutes=config['project']['access_token_expire_minutes'])
            token = access_token.create_access_token(data={"sub": user.email},
                                                     expires_delta=access_token_expires)
            return JSONResponse(status_code=200,
                                content={"access_token": token, "token_type": "Bearer"})


@router.post("/logout", response_model=UserLoginSchema, status_code=201)
async def logout(payload: UserLoginSchema):
    pass


# replace response_model=Token with custom responses
@router.post("getToken", responses=get_token_response)
def authenticate_user(user: UserAuthenticate, db: Session = Depends(get_db)) -> JSONResponse:
    db_user = crud.get_user(db, email=user.email)
    if db_user is None:
        return JSONResponse(status_code=400, content={"message": "Invalid Credentials"})
    else:
        is_password_correct = crud.check_username_password(db, user)
        if is_password_correct is False:
            return JSONResponse(status_code=400, content={"message": "Invalid Credentials"})
        else:
            access_token_expires = timedelta(
                minutes=config['project']['access_token_expire_minutes']
                )
            token = access_token.create_access_token(
                data={"sub": user.email}, expires_delta=access_token_expires
                )
            return JSONResponse(
                status_code=200, content={"access_token": token, "token_type": "Bearer"}
                )


@router.post("password-recovery/{email}", responses=general_responses)
def recover_password(email: str, db: Session = Depends(get_db)) -> JSONResponse:
    """
    Password Recovery
    """
    db_user = crud.get_user(db, email=email)

    if db_user is None:
        return JSONResponse(
            status_code=404,
            content={"message": "The user with this email does not exist in the system."},
            )

    password_reset_token = access_token.generate_password_reset_token(email=email)
    send_reset_password_email(email=email, password_reset_token=password_reset_token)
    return JSONResponse(status_code=200, content={"message": "success"})


@router.post("reset-password", responses=general_responses)
def reset_password(reset_data: UserPasswordReset, db: Session = Depends(get_db)) -> JSONResponse:
    """
    Reset password
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
        )
    expire_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="access expired",
        headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = access_token.verify_password_reset_token(token=reset_data.token)
        token_validity = payload.get("exp")
        if get_int_from_datetime(datetime.utcnow()) >= token_validity:
            raise expire_exception
        token_email: str = payload.get("sub")
        if token_email is None:
            raise credentials_exception
    except JWTException as e:
        print(e)
        raise credentials_exception
    db_user = crud.verify_user(db, email=token_email)
    if db_user is None:
        raise credentials_exception

    data = crud.update_user_password(db, email=token_email, password=reset_data.password)
    if data is None:
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})
    return JSONResponse(status_code=200, content={"message": "success"})
