from src.db.base import database, users
from src.api.models import UserSchema


async def post(payload: UserSchema):
    query = users.insert().values(email=payload.email,
                                  first_name=payload.first_name,
                                  last_name=payload.last_name,
                                  password_hash=payload.password)
    return await database.execute(query=query)


async def get(id: int):
    query = users.select().where(id == users.c.id)
    return await database.fetch_one(query=query)


async def put(id: int, payload: UserSchema):
    query = (
        users.update()
        .where(id == users.c.id)
        .values(first_name=payload.first_name, last_name=payload.last_name,)
        .returning(users.c.id)
    )
    return await database.execute(query=query)


async def delete(id: int):
    query = users.delete().where(id == users.c.id)
    return await database.execute(query=query)
