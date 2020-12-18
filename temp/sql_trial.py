import os
from datetime import datetime

from sqlalchemy import MetaData, create_engine

# from src.db import users_db
# from src.db.base import session, users_table
# from src.utils.auth import get_password_hash
# from src.utils.logger import LOGGER

# from src.utils.models import UserModel
from sqlalchemy.orm import Session

engine = create_engine(os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:////tmp/database.db'))
session = Session(engine)
metadata = MetaData()


q = engine.execute(db.text('''SELECT email FROM users WHERE email=%(email)s''', email='Jack'))
for row in q:
    print(row)


def get_user(**kwargs):
    for key, value in kwargs.items():
        return session.query(users_table).filter(eval(f'users_table.c.{key}') == f'{value}').first()

    #
    # if __name__ == "__main__":
    #     email = 'test.8cee78f6-7776-4de2-a3a1-0b15f331290b@amit.com'
    #     password = 'password123'
    # db = session
    # records = get_user(email=email)
    # result = get_user(email=email)
    # for row in records:
    #     LOGGER.info(row)
    # result = session.query(users_table).filter(users_table.c.email == email,
    #                                            users_table.c.password_hash == password).first()
    # result = users_table.insert().values(email="test.88888888888888@amit.com",
    #                                      first_name="abc",
    #                                      last_name="def",
    #                                      password=get_password_hash(str('password123')))
    payload = {
        "email": "test.88888888888888@amit.com",
        "password": "password123",
        "first_name": "abc",
        "last_name": "def",
    }
    # result = users_db.post(payload)

    # result = UserModel(email="test.88888888888888@amit.com",
    #                    first_name="abc",
    #                    last_name="def",
    #                    password='password123')
    # db.add(result)
    # db.commit()
    # db.refresh(result)
    # LOGGER.info(f'==== {result}')
    # print(type(result))
    # for i in result:
    #     if not isinstance(i, datetime):
    #         print(i)
    # users2 = Author(name="users2")
    # session.add(users2)
    # session.commit()
    # print(session.query(users).all())

    # query = session.query(users.c.email)
    # # print(query)
    # records = query.all()
    # # do we do another select here to get the name?
    # # no, we just have [(1,), (2,)]
    # print(records)
    # records = session.query.all() # .where(id == users.c.id)
    # query = session.query(users.c.email == email)
    # print(query)
    # records = query.all()
    # LOGGER.info(records)
    # records = session.query(users).all()
    # records = session.query(users).filter(
    #     users.c.email == 'test.4248f1a1-8844-4936-813e-a6b49653ea2d@amit.com').all()
    # print(type(records))
    # for row in records:
    #     print(row)
    #     print(type(row))
    # def get(email):
    #     query = users.select().where(email == users.c.email)
    #     return database.fetch_all(query=query)
    #
    #
    # def read_user(email):
    #     user_id = get(email)
    #     if not user_id:
    #         raise HTTPException(status_code=404, detail="User not found")
    #     return user_id
    # record = read_user(email)
    # for row in record:
    #     LOGGER.info(f'==== {row}')
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
