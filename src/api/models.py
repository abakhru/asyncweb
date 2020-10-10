from pydantic import BaseModel

"""NoteSchema will be used for validating the payloads for creating and updating notes."""


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
