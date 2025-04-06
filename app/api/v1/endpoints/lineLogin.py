# INSTALL pyjwt / httplib2 / google-auth

from typing import Optional
from datetime import datetime, timedelta

import jwt

# from jwt import PyJWTError

from fastapi import Depends, FastAPI, HTTPException, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.security.oauth2 import (
    OAuth2,
    OAuthFlowsModel,
    get_authorization_scheme_param,
)
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, JSONResponse, HTMLResponse
from starlette.requests import Request

from pydantic import BaseModel

import httplib2
from oauth2client import client
from google.oauth2 import id_token
from google.auth.transport import requests

from database.mongodb import AsyncIOMotorClient, get_database
from core.config import ACCESS_TOKEN_EXPIRE_HOURS
from models import user
from utils import util


LINE_API_URL = "https://api.line.me"
ACCESS_TOKEN_URL = f"{LINE_API_URL}/oauth2/v2.1/token"

USER_ID = "U7dce57c1b2811045dfd93638e208b611"
CHANNEL_SECRET = "5f9f1931951757d56bd8c33115cf474b"
REDIRECT_URI = "https://ecoupon.bispresso.com/line-callback"


ACCESS_TOKEN_EXPIRE_MINUTES = 30


from repo import userRepo, authRepo

import httpx
import asyncio
import json


router = APIRouter()


class LineLoginForm(BaseModel):
    grant_type: str = "authorization_code"
    code: str = "1234567890abcde"
    redirect_uri: str = ACCESS_TOKEN_URL
    client_id: str = USER_ID
    client_secret: str = CHANNEL_SECRET
    code_verifier: str = "wJKN8qz5t8SSI9lMFhBB6qwNkQBkuPZoCxzRhwLRUo1"


async def getToken(req_data):
    # *** แปลงข้อมูลจาก dict -> json

    json_data = json.dumps(req_data)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with httpx.AsyncClient(verify=False) as client:
        res = await client.post(ACCESS_TOKEN_URL, data=json_data, headers=headers)
    if res.status_code != 200:
        raise HTTPException(status_code=400, detail=res.text)
    return res


@router.post("/line-login")
# async def createShop(db: AsyncIOMotorClient =  Depends(get_database), req : ShopRegister = None, currentUser  : User = Depends(authRepo.get_current_active_user)):
async def LineLogin(
    req: LineLoginForm = None, db: AsyncIOMotorClient = Depends(get_database)
):
    # try:

    modelDict = req.dict()

    # modelDict["packageStart"] = datetime.strptime(modelDict["packageStart"], '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S.%f")
    # modelDict["packageEnd"] = datetime.strptime(modelDict["packageEnd"], '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S.%f")

    # modelDict["updateAt"] = datetime.today().strftime("%Y-%m-%d %H:%M:%S.%f")
    # modelDict["updateBy"] = "System"

    # regdb = ShopRegisterPackageUpdate(**modelDict)
    # regDict = regdb.dict()

    # print(f" model dict {modelDict}")
    # *** สำหรับส่ง API
    res = await getToken(modelDict)
    # *** ถ้าส่ง api ok ค่อย save

    if res.status_code != 200:
        print("API NOT SUCCESS")
        raise HTTPException(status_code=400, detail="API request unsuccessful")

    # #*** save ลง mongo
    # updaterow = await db["alex_office_admin"]["shopRegister"].update_one({"shopCode":regDict["shopCode"]}, {'$set': regDict})

    return res.text
