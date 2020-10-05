import uvicorn
from fastapi import FastAPI

from src.api import db_operations, notes, ping
from src.api.db import database, engine, metadata

metadata.create_all(engine)

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(ping.router)
app.include_router(db_operations.router)
app.include_router(notes.router, prefix="/notes", tags=["notes"])


if __name__ == '__main__':
    uvicorn.run(app=app, host="0.0.0.0", port=8000, log_level='debug', debug=True, use_colors=True)
