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


class User(BaseModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created = Column(DATETIME_WITH_TIME_ZONE, default=datetime.now)

    __table_args__ = (
        Index("user_id_idx", "id"),
        Index("user_name_idx", "name"),
        )
