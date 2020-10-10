# from base import ModelBase, get_sql_table_data

import os

from databases import Database
from fastapi import HTTPException
from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

from src.utils.logger import LOGGER

DATABASE_URL = os.getenv("DATABASE_URL", 'postgresql://amit:amit@db/asyncweb')

# SQLAlchemy
engine = create_engine(DATABASE_URL)
metadata = MetaData()
Session = sessionmaker(bind=engine)
session = Session()

LOGGER.debug(f'Creating "notes" table ..')
notes = Table(
    "notes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(50)),
    Column("description", String(50)),
    Column("created_date", DateTime, default=func.now(), nullable=False),
)

LOGGER.debug(f'Creating "users" table ..')
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("created_at", DateTime, default=func.now()),
    Column("last_modified", DateTime, default=func.now()),
    Column("deleted_at", DateTime, default=func.now()),
    Column("email", String(128), nullable=False),
    Column("password_hash", String(256), nullable=False, default=''),
    Column("consecutive_failures", Integer, nullable=True, default=0),
    Column("lockout_ends", DateTime, default=func.now()),
    Column("first_name", String(128), nullable=False),
    Column("last_name", String(128), nullable=False),
    Column("consecutive_resets", Integer, nullable=True, default=0),
    Column("reset_lockout_ends", DateTime, default=func.now()),
)

# databases query builder
database = Database(DATABASE_URL)


def get_user(**kwargs):
    for key, value in kwargs.items():
        return session.query(eval('users.c.id')).filter(eval(f'users.c.{key}') == f'{value}').all()


if __name__ == "__main__":
    email = 'test.4248f1a1-8844-4936-813e-a6b49653ea2d@amit.com'
    records = get_user(email=email)
    for row in records:
        print(row)

    # users2 = Author(name="users2")
    # session.add(users2)
    # session.commit()
    # print(session.query(users).all())

    # query = session.query(users.c.email)
    # print(query)
    # records = query.all()
    # # do we do another select here to get the name?
    # # no, we just have [(1,), (2,)]
    # print(records)
    # records = session.query.all() # .where(id == users.c.id)
    # query = session.query(users.c.email ==
    #                       'test.4248f1a1-8844-4936-813e-a6b49653ea2d@amit.com')
    # print(query)
    # records = query.scalar()
    # print(records)
    # records = session.query(users).all()
    # records = session.query(users).filter(
    #     users.c.email == 'test.4248f1a1-8844-4936-813e-a6b49653ea2d@amit.com').all()
    # print(type(records))
    # for row in records:
    #     print(row)
    #     print(type(row))
    # def get(email: int):
    #     query = users.select().where(email == users.c.email)
    #     return database.fetch_one(query=query)
    #
    #
    # def read_user(email):
    #     user_id = get(email)
    #     if not user_id:
    #         raise HTTPException(status_code=404, detail="User not found")
    #     return user_id
    # record = read_user(email)
    # print(record)
    # Now the query which may be useful if we want to group / order something
    # in a subquery and then get the full data
    # The subquery can return only ids and we then join the same table again to
    # get the full data:
    # SELECT users.*
    # FROM (
    #   SELECT users.id FROM userss
    # ) as sub_users
    # JOIN users on users.id = sub_userss.id
    # query = session.query(users.id)
    # #query = query.add_entity(users).from_self()
    # users_data = aliased(users)
    # query = query.from_self(users_data)
    # query = query.join(users_data, users_data.id==users.id)
    # print(query)
    # records = query.all()
    # print(records)
    #
