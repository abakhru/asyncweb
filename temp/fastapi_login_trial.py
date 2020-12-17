#!/usr/bin/env python
from datetime import timedelta
from pathlib import Path
from typing import List, Optional

from databases import Database
from fastapi import Depends, FastAPI, HTTPException
from fastapi.params import Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker
from starlette.responses import JSONResponse, Response
from uvicorn import Config, Server

from src.conf import config
from src.utils.logger import LOGGER

LOGGER.setLevel('DEBUG')

SECRET_KEY = config['project']['secret']
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATABASE_URL = 'sqlite:////tmp/database.db'
# DATABASE_URL = "postgresql://user:password@postgresserver/db"
Base: DeclarativeMeta = declarative_base()


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

    def set_password(self, password):
        self.hashed_password = get_password_hash(password)


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="items")


database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
login_manager = LoginManager(SECRET_KEY, tokenUrl='/auth/token', use_cookie=True)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
Base.metadata.create_all(engine)
session = Session(engine)
users_table = User.__table__
app = FastAPI()


def verify_password(plain_password, hashed_password):
    LOGGER.debug(f'plain: {plain_password}; hashed: {hashed_password}')
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


@login_manager.user_loader
async def get_user(**kwargs):
    for key, value in kwargs.items():
        result = session.query(users_table).filter(
                eval(f'users_table.c.{key}') == f'{value}').first()
        LOGGER.debug(f'result: {result}')
        return result


async def authenticate_user(username: str, password: str):
    user = await get_user(email=username)
    if not user:
        return None
    if not verify_password(plain_password=password,
                           hashed_password=user.hashed_password):
        return False
    return user


async def create_user(email: str, password: str):
    user = await get_user(email=email)
    if user:
        HTTPException(detail=f'User {email} already exists!', status_code=402)
    admin = User(email=email)
    admin.set_password(password=password)
    try:
        session.add(admin)
        session.commit()
    except (IntegrityError, InvalidRequestError) as _:
        HTTPException(detail=f'User {email} already exists!', status_code=402)
    return await get_user(email=email)


@app.post('/auth/token')
async def login(data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(data.username, data.password)
    LOGGER.debug(f'[/login] locals: {locals()}')
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = login_manager.create_access_token(data={"sub": data.username,
                                                           "scopes": data.scopes},
                                                     expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get('/auth')
async def auth(response: Response, user=Depends(login_manager)):
    token = login_manager.create_access_token(data=dict(sub=user.email))
    login_manager.set_cookie(response, token)
    return response


@app.post('/users/create')
async def create(email: str = Form(None),
                 password: str = Form(None)) -> JSONResponse:
    LOGGER.debug(f'[/login] locals: {locals()}')
    return await create_user(email=email, password=password)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# TODO:
# [x] auth with db
# [x] store password in db with hash
# [x] authenticate encrypted password with SECRET


if __name__ == "__main__":
    create_user('admin@example.com', 'admin')
    config = Config(app=app,
                    host=config['project']['server_host'],
                    port=config['project']['server_port'],
                    log_level='debug',
                    debug=True,
                    reload=True,
                    reload_dirs=Path(__file__).parent.resolve(),
                    workers=1,
                    use_colors=True)
    server = Server(config=config)
    server.run()
