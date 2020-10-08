import os

from databases import Database
from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, create_engine
from sqlalchemy.sql import func

from src.api.logger import LOGGER

DATABASE_URL = os.getenv("DATABASE_URL", 'postgresql://amit:amit@db/asyncweb')

# SQLAlchemy
engine = create_engine(DATABASE_URL)
metadata = MetaData()

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
