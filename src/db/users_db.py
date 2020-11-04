from src.db.base import database, users_table
from src.db.crud import get_password_hash
from src.utils.models import UserSchema


async def post(payload: UserSchema):
    query = users_table.insert().values(
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        password_hash=get_password_hash(payload.password),
    )
    return await database.execute(query=query)


async def get(id: int):
    query = users_table.select().where(id == users_table.c.id)
    return await database.fetch_one(query=query)


async def put(id: int, payload: UserSchema):
    query = (
        users_table.update()
        .where(users_table.c.id == id)
        .values(
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
        .returning(users_table.c.id)
    )
    return await database.execute(query=query)


async def delete(id: int):
    query = users_table.delete().where(id == users_table.c.id)
    return await database.execute(query=query)
