from pathlib import Path

from fastapi import APIRouter, HTTPException

from src.db import users_db
from src.api.models import UserDB, UserLoginSchema, UserSchema
from src.utils.logger import LOGGER

router = APIRouter()


@router.post("/create", response_model=UserDB, status_code=201)
async def create_user(payload: UserSchema):
    user_id = users_db.get_user(email=payload.email)
    if len(user_id):
        LOGGER.warning(f'{payload.email} already exists')
        raise HTTPException(status_code=422, detail=f"Duplicate user {payload.email}")
    user_id = await users_db.post(payload)
    response_object = {
        "id": user_id,
        "email": payload.email,
        "first_name": payload.first_name,
        "last_name": payload.last_name,
    }
    return response_object


@router.post("/login", response_model=UserLoginSchema, status_code=201)
async def login(payload: UserLoginSchema):
    pass


@router.post("/logout", response_model=UserLoginSchema, status_code=201)
async def logout(payload: UserLoginSchema):
    pass


@router.get("/{id}/", response_model=UserDB)
async def read_user(id: int = Path("..", gt=0)):
    user_id = await users_db.get(id)
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")
    return user_id


@router.put("/{id}/", response_model=UserDB)
async def update_user(id: int, payload: UserSchema):
    user_id = await users_db.get(id)
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = await users_db.put(id, payload)
    response_object = {
        "id": user_id,
        "first_name": payload.first_name,
        "last_name": payload.last_name,
    }
    return response_object


@router.delete("/delete/", response_model=UserDB, status_code=201)
async def delete_user(id: int):
    user_id = await users_db.get(id)
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")
    await users_db.delete(id)
    return user_id
