from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException

from src.db import notes_db
from src.api.models import NoteDB, NoteSchema

router = APIRouter()


@router.post("/", response_model=NoteDB, status_code=201)
async def create_note(payload: NoteSchema):
    note_id = await notes_db.post(payload)
    response_object = {
        "id": note_id,
        "title": payload.title,
        "description": payload.description,
    }
    return response_object


@router.get("/{id}/", response_model=NoteDB)
async def read_note(id: int = Path("..", gt=0)):
    note = await notes_db.get(id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.get("/", response_model=List[NoteDB])
async def read_all_notes():
    return await notes_db.get_all()


@router.put("/{id}/", response_model=NoteDB)
async def update_note(id: int, payload: NoteSchema):
    note = await notes_db.get(id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note_id = await notes_db.put(id, payload)

    response_object = {
        "id": note_id,
        "title": payload.title,
        "description": payload.description,
    }
    return response_object


@router.delete("/{id}/", response_model=NoteDB)
async def delete_note(id: int):
    note = await notes_db.get(id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    await notes_db.delete(id)

    return note
