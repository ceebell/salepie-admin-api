from typing import List, Optional , Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from repo import  userRepo, authRepo

##### BEGIN : DATABSE #####

from models import  schemas, user, csharpModel
# from loguru import logger
from pydantic import BaseModel, Json ,ValidationError, validator, Field, EmailStr
from database.mongodb import AsyncIOMotorClient, get_database

from utils import util

from time import time
import httpx
import asyncio


router = APIRouter()

# *** https://stackoverflow.com/questions/63872924/how-can-i-send-an-http-request-from-my-fastapi-app-to-another-site-api
# *** https://www.python-httpx.org/quickstart


URL = "http://httpbin.org/uuid"

async def get_request(client):
    response = await client.get(URL)
    return response.text

async def get_task():
    async with httpx.AsyncClient() as client:
        r = await client.get('https://www.example.com/')
        # tasks = [get_request(client) for i in range(100)]
        # result = await asyncio.gather(*tasks)
        # print(result)
        return r.text

async def post_request(client):
    
    data={'key': 'value'}
    headers = {'user-agent': 'my-app/0.0.1'}
    
    response = await client.post(URL , data=data, headers=headers)
    return response.text

async def post_task():
    async with httpx.AsyncClient() as client:
        tasks = post_request(client)
        result = await asyncio.gather(*tasks)
        # print(result)
        return result





# @router.get('/',  tags=["alex"])
# async def f():
#     start = time()
#     res = await get_task()
#     print(f"res res res : \n\n {res}")
#     print("time: ", time() - start)
