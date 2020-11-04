from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Index, Integer, String
from werkzeug.security import check_password_hash, generate_password_hash

"""NoteSchema will be used for validating the payloads for creating and updating notes."""
DATETIME_WITH_TIME_ZONE = DateTime(timezone=True)
db = SQLAlchemy()


class NoteSchema(BaseModel):
    title: str
    description: str


class NoteDB(NoteSchema):
    id: int


class UserSchema(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class UserDB(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


class UserLoginSchema(BaseModel):
    email: str
    password: str


class UserModel(UserMixin, db.Model):
    __tablename__ = 'users'

    id = Column("id", Integer, primary_key=True),
    email = Column("email", String(128), nullable=False, unique=True),
    password_hash = Column("password_hash", String(256), nullable=False, default=''),
    first_name = Column("first_name", String(128), nullable=False),
    last_name = Column("last_name", String(128), nullable=False),
    created_at = Column("created_at", DATETIME_WITH_TIME_ZONE, default=datetime.now)

    __table_args__ = (
        Index("user_id_idx", "id"),
        Index("user_name_idx", "name"),
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Message(BaseModel):
    message: str


class UserBase(BaseModel):
    email: str


class UserVerify(UserBase):
    id: int


class UserCreate(UserBase):
    password: str
    first_name: str
    last_name: str


class UserUpdate(UserBase):
    name: str


class UserAuthenticate(UserBase):
    password: str


class UserPasswordReset(BaseModel):
    token: str
    password: str


# return in response
class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    pass


class PostCreate(PostBase):
    title: str
    post: str


class PostUpdate(PostBase):
    title: str
    post: str


# return in response
class Post(PostBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str
    expire: str
    issue_time: str
