from src.api.models import UserSchema
from src.db.base import database, session, users
from src.utils.logger import LOGGER


def get_user(**kwargs):
    query_string = list()
    for key, value in kwargs.items():
        query_string.append(f'users.c.{key} == "{value}"')
    # LOGGER.debug(f'final query: {", ".join(query_string)}')
    # return session.query(users).filter_by(**kwargs).first()
    return (
        session.query(users)
        .filter_by(email=kwargs.get('username'), password_hash=kwargs.get('password_hash'))
        .first()
    )

    # query = users.select().where(eval(f'users.c.{key}') == f'{value}')
    # return database.execute(query=query)
    # return database.execute(query=query)
    # result = session.query(users).filter(users.c.email == email,
    #                                      users.c.password_hash == password).first()


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
