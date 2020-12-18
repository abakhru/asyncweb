import os

from databases import Database
from fastapi_login import LoginManager
from passlib.context import CryptContext
from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy.sql import func

from src.conf import config
from src.utils.logger import LOGGER

SECRET_KEY = config['project']['secret']
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:////tmp/database.db')
Base: DeclarativeMeta = declarative_base()

if not DATABASE_URL:
    db_conf = config['database']
    # DATABASE_URL = "postgresql://user:password@postgresserver/db"
    DATABASE_URL = (
        f'{db_conf["database"]}://'
        f'{db_conf["postgres_user"]}:{db_conf["postgres_password"]}@'
        f'{db_conf["postgres_server"]}:{db_conf["postgres_port"]}/'
        f'{db_conf["postgres_db"]}'
    )

LOGGER.debug(f'Database-url : {DATABASE_URL}')

LOGGER.debug(f'Creating "notes" table ..')
notes_table = Table(
        "notes",
        Base.metadata,
        Column("id", Integer, primary_key=True),
        Column("title", String(50)),
        Column("description", String(50)),
        Column("created_date", DateTime, default=func.now(), nullable=False),
        )

LOGGER.debug(f'Creating "users" table ..')
users_table = Table(
        "users",
        Base.metadata,
        Column("id", Integer, primary_key=True),
        Column("email", String(128), nullable=False, unique=True),
        Column("password_hash", String(256), nullable=False, default=''),
        Column("first_name", String(128), nullable=False),
        Column("last_name", String(128), nullable=False),
        Column("created_at", DateTime, default=func.now()),
        Column("last_modified", DateTime, default=func.now()),
        Column("deleted_at", DateTime),
        Column("consecutive_resets", Integer, nullable=True, default=0),
        Column("consecutive_failures", Integer, nullable=True, default=0),
        Column("lockout_ends", DateTime),
        Column("reset_lockout_ends", DateTime),
        )

database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
login_manager = LoginManager(SECRET_KEY, tokenUrl='/auth/token', use_cookie=True)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
Base.metadata.create_all(engine)
session = Session(engine)
