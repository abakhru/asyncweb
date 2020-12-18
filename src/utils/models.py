from pydantic import BaseModel
from sqlalchemy import DateTime

"""NoteSchema will be used for validating the payloads for creating and updating notes."""
DATETIME_WITH_TIME_ZONE = DateTime(timezone=True)


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
