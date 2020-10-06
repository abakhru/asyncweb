from pydantic import BaseModel
from pydantic.fields import Field

"""NoteSchema will be used for validating the payloads for creating and updating notes."""


# class NoteSchema(BaseModel):
#     title: str
#     description: str


class NoteSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., min_length=3, max_length=50)


class NoteDB(NoteSchema):
    id: int
