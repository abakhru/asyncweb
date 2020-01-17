from pydantic import BaseModel

"""NoteSchema will be used for validating the payloads for creating and updating notes."""


class NoteSchema(BaseModel):
    title: str
    description: str


class NoteDB(NoteSchema):
    id: int
