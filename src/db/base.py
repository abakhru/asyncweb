import os

from databases import Database
from fastapi_login import LoginManager
from passlib.context import CryptContext
from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import func

from src.conf import config
from src.utils.logger import LOGGER

db_conf = config['database']
DATABASE_URL = os.getenv("DATABASE_URL", 'sqlite:////tmp/database.db')

if not DATABASE_URL:
    # postgresql://amit:amit@db/asyncweb
    DATABASE_URL = (
        f'{db_conf["database"]}://'
        f'{db_conf["postgres_user"]}:{db_conf["postgres_password"]}@'
        f'{db_conf["postgres_server"]}:{db_conf["postgres_port"]}/'
        f'{db_conf["postgres_db"]}'
    )

LOGGER.debug(f'Database-url : {DATABASE_URL}')
# SQLAlchemy
engine = create_engine(DATABASE_URL)
metadata = MetaData()
BASE = declarative_base()
SESSION_FACTORY = sessionmaker(bind=engine)
SESSION = scoped_session(SESSION_FACTORY)
session = SESSION_FACTORY()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
login_manager = LoginManager(secret=config['project']['secret'], tokenUrl='/auth/token')

LOGGER.debug(f'Creating "notes" table ..')
notes_table = Table(
    "notes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(50)),
    Column("description", String(50)),
    Column("created_date", DateTime, default=func.now(), nullable=False),
)

LOGGER.debug(f'Creating "users" table ..')
users_table = Table(
    "users",
    metadata,
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

# databases query builder
database = Database(DATABASE_URL)
