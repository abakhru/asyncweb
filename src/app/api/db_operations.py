import json
import os

import psycopg2
from fastapi import APIRouter
from flask import request

router = APIRouter()
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()
table_name = "notes"


@router.route("/create", methods=["POST"])
async def create():
    name = request.json["Name"]
    sql = f"""insert into {table_name} values('{name}')"""
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
