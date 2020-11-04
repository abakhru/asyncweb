from src.utils.models import UserSchema
from src.db.base import database, session, users_table


def get_user(**kwargs):
    query_string = list()
    for key, value in kwargs.items():
        query_string.append(f'users_table.c.{key} == "{value}"')
    # LOGGER.debug(f'final query: {", ".join(query_string)}')
    # return session.query(users_table).filter_by(**kwargs).first()
    return (
        session.query(users_table)
        .filter_by(email=kwargs.get('username'), password_hash=kwargs.get('password_hash'))
        .first()
    )

    # query = users_table.select().where(eval(f'users_table.c.{key}') == f'{value}')
    # return database.execute(query=query)
    # return database.execute(query=query)
    # result = session.query(users_table).filter(users_table.c.email == email,
    #                                      users_table.c.password_hash == password).first()


async def post(payload: UserSchema):
    query = users_table.insert().values(
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        password_hash=payload.password,
    )
    return await database.execute(query=query)


async def get(id: int):
    query = users_table.select().where(id == users_table.c.id)
    return await database.fetch_one(query=query)


async def put(id: int, payload: UserSchema):
    query = (
        users_table.update()
        .where(id == users_table.c.id)
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
