from app.api import notes, ping
from app.api.db import database, engine, metadata
from fastapi import FastAPI

metadata.create_all(engine)

app = FastAPI(__name__)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(ping.router)
# app.include_router(db_operations.router)
app.include_router(notes.router, prefix="/notes", tags=["notes"])

# uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 8000
