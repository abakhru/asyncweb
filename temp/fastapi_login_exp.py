#!/usr/bin/env python

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
    )
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from src.conf import config
from src.utils.logger import LOGGER

SECRET_KEY = config['project']['secret']
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SQLALCHEMY_DATABASE_URL = 'sqlite:////tmp/database.db'
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

fake_users_db = {
    "amit": {
        "username": "amit",
        "full_name": "Amit Bakhru",
        "email": "amit@bakhru.com",
        "hashed_password": "$2b$14$8pv3hc2zUGumXfdaXRvqrO2cXmUgcW.sX6CsmW3GvO/0mIhOvtbMK",
        "disabled": False,
        },
    "alice": {
        "username": "alice",
        "full_name": "Alice Chains",
        "email": "alicechains@example.com",
        "hashed_password": "$2b$14$8pv3hc2zUGumXfdaXRvqrO2cXmUgcW.sX6CsmW3GvO/0mIhOvtbMK",
        "disabled": True,
        },
    }


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="items")


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token",
                                     scopes={"me": "Read information about the current user.",
                                             "items": "Read items."})
app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    LOGGER.info(f'user: {user}')
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": authenticate_value})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Not enough permissions",
                                headers={"WWW-Authenticate": authenticate_value})
    return user


async def get_current_active_user(current_user: User = Security(get_current_user, scopes=["me"])):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    LOGGER.debug(f'form_data: {form_data.__dict__}')
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username,
                                             "scopes": form_data.scopes},
                                       expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: User = Security(get_current_active_user, scopes=["items"])):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.get("/status/")
async def read_system_status(current_user: User = Depends(get_current_user)):
    return {"status": "ok"}


#
# # TODO:
# # - auth with db
# # - store password in db with hash
# # - authenticate encrypted password with SECRET


if __name__ == "__main__":
    # db.create_all()
    # admin = User(username='admin', email='admin@example.com')
    # admin.set_password(password='admin')
    # db.session.add(admin)
    # db.session.commit()
    # print(User.query.all())
    # LOGGER.info(f"{User.query.filter_by(username='admin').first()}")
    app.run(debug=True, host='0.0.0.0', port=8000)
