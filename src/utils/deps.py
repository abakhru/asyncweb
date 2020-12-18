from datetime import datetime

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette import status

# from src.auth.access_token import access_token
from src.db import login_manager, session
from src.db.user_crud import get_user
from src.utils.logger import LOGGER
from src.utils.models import TokenData, UserVerify


def get_db():
    db = None
    try:
        db = session
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/getToken")


def get_current_user(
        token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
        ) -> UserVerify:
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
        payload = login_manager.decode_access_token(token=token)
        token_validity = payload.get("exp")
        # if get_int_from_datetime(datetime.utcnow()) >= token_validity:
        #     raise expire_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except Exception as _:
        LOGGER.exception("get_current_user")
        raise credentials_exception
    user = get_user(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user
