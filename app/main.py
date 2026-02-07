from typing import List, Optional , Any, Dict
from fastapi import FastAPI, Body, HTTPException, Header, Response, Request, status
# Customize error responses
from fastapi.exceptions import RequestValidationError
# Customize error responses
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from starlette.requests import Request
from pydantic import BaseModel, Json ,ValidationError, validator, Field, EmailStr, ValidationError
import sys
import random, string

from pathlib import Path
from fastapi.staticfiles import StaticFiles # (2) Import ตัวนี้

# from pymongo import MongoClient
# from bson.json_util import dumps

from fastapi.exceptions import RequestValidationError

from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)

from starlette.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from api.v1.api import api_router

import datetime
from utils import util

# from loguru import logger

import logging
from core.logging import setup_logging
setup_logging(logging.INFO)

from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer


from models import user, schemas


from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi.middleware.cors import CORSMiddleware
# from starlette.middleware import Middleware
# from starlette.middleware.cors import CORSMiddleware

from fastapi.responses import RedirectResponse

templates = Jinja2Templates(directory="./templates")





# handler = logging.handlers.SysLogHandler(address=('localhost', 8000))
# ***logger.add(handler)
# ***logger.add("../Development/setartnew_log/apilog_{time}.log" , colorize=True, format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")

# logger.add("logs/file.log",colorize=True, format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from database.mongodb_utils import close_mongo_connection, connect_to_mongo


# import motor.motor_asyncio
from database.mongodb import AsyncIOMotorClient, get_database
from bson.objectid import ObjectId
# MONGO_DETAILS = "mongodb://bell84:Passwor@143.110.254.250:27017"
from sqlmodel import Field, Session, SQLModel, create_engine

# import handler ที่เราสร้างตะกี้มา
from handlers import custom_pydantic_validation_handler
# middleware = [
#     Middleware(CORSMiddleware,  allow_credentials=True,  allow_origins=["*"],allow_methods=["*"], allow_headers=["*"])
# ]router
# from database.mongodb  import AsyncIOMotorClient, get_database

app = FastAPI()


# ✅ ลงทะเบียนตรงนี้ครับ
app.add_exception_handler(ValidationError, custom_pydantic_validation_handler)

# ✅ Override Error 422
@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    
    # สร้าง list error แบบย่อ (เอาแค่ field ไหน ผิดว่าอะไร)
    simplified_errors = []
    for error in exc.errors():
        field = ".".join([str(x) for x in error["loc"][1:]]) # ตัด 'body' ออก
        simplified_errors.append({
            "field": field,
            "message": error["msg"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation Failed",
            "errors": simplified_errors # ✅ ส่งแบบย่อแทน
        },
    )



# org = ["*"]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=org,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# origins = [
#     "http://localhost.tiangolo.com",
#     "https://localhost.tiangolo.com",
#     "http://localhost",
#     "http://localhost:8080",
#     "http://127.0.0.1:8080",
# ]

#*** เอาออก ตอน Production
# app.mount("/static", StaticFiles(directory="static"), name="static")
static_dir = Path(__file__).resolve().parent / "static"   # ถ้า static อยู่ใต้ app/ ให้ปรับ path
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[ "http://localhost:8000",
    "http://localhost:3500",
        "http://127.0.0.1:3500",
        "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Set-Cookie"],  # เพิ่มบรรทัดนี้
)

# Logging zone
logger = logging.getLogger("salepie")

# *** MOTOR PYMONG
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)
# *** MOTOR PYMONG
app.include_router(api_router)


