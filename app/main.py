import uvicorn
from fastapi import Depends, FastAPI

from app.api.db import database, engine, metadata
from app.server.auth.jwt_bearer import JWTBearer
from app.server.routes import admin, db_operations, notes, ping, student

metadata.create_all(engine)

app = FastAPI()
token_listener = JWTBearer()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app, sighs."}


app.include_router(ping.router)
app.include_router(db_operations.router)
app.include_router(notes.router, prefix="/notes", tags=["notes"])
app.include_router(admin.router, tags=["Administrator"], prefix="/admin")
app.include_router(student.router, tags=["Students"], prefix="/student",
                   dependencies=[Depends(token_listener)])


if __name__ == '__main__':
    uvicorn.run(app=app, host="0.0.0.0", port=8000, log_level='debug', debug=True, use_colors=True)
