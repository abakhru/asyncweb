from src.db.base import database, notes_table
from src.utils.models import NoteSchema


async def post(payload: NoteSchema):
    query = notes_table.insert().values(title=payload.title, description=payload.description)
    return await database.execute(query=query)


async def get(id: int):
    query = notes_table.select().where(id == notes_table.c.id)
    return await database.fetch_one(query=query)


async def get_all():
    query = notes_table.select()
    return await database.fetch_all(query=query)


async def put(id: int, payload: NoteSchema):
    query = (
        notes_table.update()
        .where(id == notes_table.c.id)
        .values(title=payload.title, description=payload.description)
        .returning(notes_table.c.id)
    )
    return await database.execute(query=query)


async def delete(id: int):
    query = notes_table.delete().where(id == notes_table.c.id)
    return await database.execute(query=query)
