import json
import os
import sys

import psycopg2
from fastapi import APIRouter
from flask import request

from src.api.logger import LOGGER

router = APIRouter()
try:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
except (TypeError, ConnectionError) as e:
    LOGGER.critical(f'Database Connection failed. \n{e}')
    sys.exit(1)

cur = conn.cursor()
table_name = "users"


@router.route("/create", methods=["POST"])
async def create():
    json_req = request.json()
    sql = f"""INSERT INTO {table_name} (email, password_hash, first_name, last_name, consecutive_failures)
            VALUES 
            ({json_req.get('email').lower()}, {json_req.get('password')}, 
             {json_req.get('first_name')}, {json_req.get('last_name')}, 0)"""
    LOGGER.debug(f'Constructed SQL:\n{sql}')
    cur.execute(sql)
    conn.commit()
    response = {"Message": "Success"}
    return json.dumps(response)


@router.get("/read")
async def read():
    sql = f"""select * from {table_name}"""
    cur.execute(sql)
    data = cur.fetchall()
    response = {"Name": data[-1]}
    return json.dumps(response)


@router.route("/update", methods=["PUT"])
async def update():
    name = request.json["Name"]
    sql = f"""update {table_name} set name = '{name}'"""
    cur.execute(sql)
    conn.commit()
    response = {"Message": "Success"}
    return json.dumps(response)


@router.route("/delete", methods=["DELETE"])
async def delete():
    name = request.json["Name"]
    sql = f"""delete from {table_name} where name = '{name}'"""
    cur.execute(sql)
    conn.commit()
    response = {"Message": "Success"}
    return json.dumps(response)
