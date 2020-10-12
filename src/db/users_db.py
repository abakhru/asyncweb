from src.api.models import UserSchema
from src.db.base import database, users


def get_user(**kwargs):
    for key, value in kwargs.items():
        # return session.query(eval('users.c.id')).filter(eval(f'users.c.{key}') == f'{value}').all()
        query = users.select().where(eval(f'users.c.{key}') == f'{value}')
        return database.execute(query=query)


async def post(payload: UserSchema):
    query = users.insert().values(
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        password_hash=payload.password,
    )
    return await database.execute(query=query)


async def get(id: int):
    query = users.select().where(id == users.c.id)
    return await database.fetch_one(query=query)


async def put(id: int, payload: UserSchema):
    query = (
        users.update()
        .where(id == users.c.id)
        .values(
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
        .returning(users.c.id)
    )
    return await database.execute(query=query)


async def delete(id: int):
    query = users.delete().where(id == users.c.id)
    return await database.execute(query=query)
