import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from flask import render_template
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from flask import request

from src.conf import config
from src.db.base import database, engine, metadata
from src.routes import api_router

metadata.create_all(engine)

app = FastAPI(
    title=config['project']['project_name'],
    description=config['project']['project_description'],
    version="2.5.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=f"{config['project']['api_version_path']}/openapi.json",
)
# Middleware Settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=config['project']['backend_cors_origins'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get('/', status_code=200)
def home():
    # if not session.get('logged_in'):
    return templates.TemplateResponse("login.html", {"request": request, "id": id})
    # else:
    #     return JSONResponse(status_code=200, content={"message": "Welcome to Demo Server"})


if __name__ == '__main__':
    uvicorn.run(
        app=app,
        host=config['project']['server_host'],
        port=config['project']['server_port'],
        log_level='debug',
        debug=True,
        use_colors=True,
        # reload=True,
    )
