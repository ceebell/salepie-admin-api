from typing import List, Optional
import base64
from passlib.context import CryptContext
from datetime import datetime, timedelta


# from pymongo import MongoClient
# from bson.json_util import dumps

import jwt
# from jwt import PyJWTError
from jose import JWTError, jwt

from pydantic import BaseModel, Json,Field, ValidationError, validator, EmailStr

from fastapi import Depends, FastAPI, HTTPException, APIRouter , Header
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm, OAuth2
from fastapi.security.base import SecurityBase, SecurityBaseModel
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.utils import get_openapi

from starlette.status import HTTP_403_FORBIDDEN
from starlette.responses import RedirectResponse, Response, JSONResponse
from starlette.requests import Request

from core.config  import ACCESS_TOKEN_EXPIRE_HOURS

# import logging
# from mongoengine import *

# from loguru import logger
from utils import util
from uuid import UUID, uuid1
import json

from models import  clientInfo, user
# from loguru import logger


from repo import userRepo
from database.mongodb  import AsyncIOMotorClient, get_database


# to get a string like this run:
# openssl rand -hex 32
# SECRET_KEY = "0d85a71d5f9f42b221fd42ca7a6b1fe46ed8fb3a4bc0f365ad8e7dc1277d0829"
SECRET_KEY = "dfe34d0177aa124604f5f85c722a49432be12405d554ccab73da50bcc991d03777b4747f90d4972190df8284c3be5c24d41c46443e03c79c4d73d5a1d7a164e1" # เปลี่ยนเป็น key ของคุณ
ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ACCESS_TOKEN_EXPIRE_HOURS = 24

router = APIRouter()


# async def verify_token(x_token: str = Header(...)):
#     if x_token != "fake-super-secret-token":
#         raise HTTPException(status_code=400, detail="X-Token header invalid")


class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        header_authorization: str = request.headers.get("Authorization")
        cookie_authorization: str = request.cookies.get("Authorization")

        header_scheme, header_param = get_authorization_scheme_param(
            header_authorization
        )
        cookie_scheme, cookie_param = get_authorization_scheme_param(
            cookie_authorization
        )

        if header_scheme.lower() == "bearer":
            authorization = True
            scheme = header_scheme
            param = header_param

        elif cookie_scheme.lower() == "bearer":
            authorization = True
            scheme = cookie_scheme
            param = cookie_param

        else:
            authorization = False
            
        
        # print(f"\nheader_scheme : {header_scheme} \nheader_param = {header_param}")

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        return param



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="/token")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


# def normalize_password(password: str) -> str:
#     return hashlib.sha256(password.encode("utf-8")).hexdigest()

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     safe_password = normalize_password(plain_password)
#     return pwd_context.verify(safe_password, hashed_password)

# def get_password_hash(password: str) -> str:
#     safe_password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
#     return pwd_context.hash(safe_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)    



async def createClientInfo(create: clientInfo.ClientInfoCreate, db: AsyncIOMotorClient) -> user.UserDb:
    
    infodb = clientInfo.ClientInfoDb(**create.dict())
    
    infodb.id = util.getUuid()
    infodb.clientId = util.genRandomText(20)

    row = await db["alex_office_admin"]["clientInfo"].insert_one(infodb.dict())

    create = await userRepo.getUserByEmail(db=db, email=email)

    # if not infodb:
    #     return "NO_USER"
    # if not verify_password(password, userdb.hashedPassword):
    #     return "NOT_AUTHORIZED"
    return infodb


async def authenticateUser(db: AsyncIOMotorClient, email: str, password: str)-> user.UserDb:
    userdb = await userRepo.getUserByEmail(db=db, email=email)
    # logger.info("AUTH_REPO EMAIL: {0}",email)
    if not userdb:
        return "NO_USER"
    if not verify_password(password, userdb.hashedPassword):
        return "NOT_AUTHORIZED"
    return userdb


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    
    print(f"INPUT create_access_token >>> {to_encode}")
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_token(request: Request):
    
    # if not request.headers.get("Authorization"):
    #     raise HTTPException(status_code=401, detail="VERFIFY TOKEN Not authenticated")
    # print(f"\nverify_token request.cookies  {request.cookies } \n")

    if not request.cookies.get("Authorization"):
         raise HTTPException(status_code=401, detail="VERFIFY TOKEN Not authenticated")
    
    
    # print(f"\n ********************** \n")
    # header_authorization: str = request.headers.get("Authorization")
    cookie_authorization: str = request.cookies.get("Authorization")
    
    # header_scheme, header_param = get_authorization_scheme_param(
    #         header_authorization
    # )
    ncookie_scheme = ""
    cookie_value, cookie_param = get_authorization_scheme_param(
        cookie_authorization
    )

    # print(f"\nverify_token cookie_value : {cookie_value} \n")

    # param = ""
    # if header_scheme.lower() == "bearer":
    #     authorization = True
    #     scheme = header_scheme
    #     param = header_param

    # if cookie_scheme.lower() == "bearer":
    #     authorization = True
    #     scheme = cookie_scheme
    #     param = cookie_param

    # else:
    #     authorization = False

    # if not authorization or scheme.lower() != "bearer":
    #     raise HTTPException(
    #         status_code=401, detail="Not authenticated"
    #     )
       
        
    # if not param:
    #     raise HTTPException(
    #         status_code=401, detail="Not authenticated"
    #     )
    
    # print(f"\nverify_token FINAL param : {param}\n")
    
    return cookie_value




async def get_current_user(db: AsyncIOMotorClient =  Depends(get_database), token: str = Depends(verify_token)):
   
    # decoded = jwt.decode(token, options={"verify_signature": False}) # works in PyJWT >= v2.0
    
    try:
        # print(f"Decoding token: {token}")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                
        uid: str = payload.get("sub")
        email: str = payload.get("email")
        roles: str = payload.get("roles")

        # print(f"Payload decoded: uid={uid}, email={email}, roles={roles}")

                
        if email is None:
            raise HTTPException(
                status_code=403, detail="User not found"
            )
        
        
        
    except JWTError:
        print("JWTError: Jwt token invalid")
        raise HTTPException(
            status_code=403, detail="Jwt token invalid"
        )
    
    userDb = await userRepo.getUserByEmail(db=db, email=email)
    
   

    
    if userDb is None:
        print("JWTError: User not found")
        raise HTTPException(
            status_code=403, detail="User not found"
        )
    
    if userDb.deleted == True:
        print("JWTError: User is deleted")
        raise HTTPException(
            status_code=403, detail="User is deleted"
        )
        
    user_profile = user.UserProfile(**userDb.model_dump())

    # if userDb.activeToken != token:
    #     print("JWTError: Current session is no longer valid")
    #     raise HTTPException(
    #         status_code=403, detail="Current session is no longer valid"
    #     )
    return user_profile


# 2. Hero ของเรา: Class เช็ค Role แบบปรับเปลี่ยนได้
class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: user.UserDb = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, 
                detail="Operation not permitted"
            )
        return user
    
# ===========================================================
# ==== เวลาใช้ RoleChecker 
# ===========================================================

# # สร้าง "ยาม" ที่อนุญาตเฉพาะ Admin และ Owner
# allow_admin_and_owner = RoleChecker(["admin", "owner"])

# # สร้าง "ยาม" ที่อนุญาตเฉพาะ Owner เท่านั้น (เผื่อใช้เส้นอื่น)
# allow_owner_only = RoleChecker(["owner"])


# @app.get("/products")
# async def get_products(user: User = Depends(allow_admin_and_owner)):
#     # ถ้าเข้ามาถึงบรรทัดนี้ได้ แปลว่าเป็น Admin หรือ Owner แน่นอน
#     return {"message": f"Hello {user.username}, you are authorized!"}

# @app.delete("/products/{id}")
# async def delete_product(user: User = Depends(allow_owner_only)):
#     # เส้นนี้เข้าได้แค่ Owner คนเดียว
#     return {"message": "Product deleted"}

# async def get_current_user_authorized(roles: List,current_user: user.UserDb = Depends(get_current_user)):
    
#     if not current_user.isActive:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


async def get_current_active_user(current_user: user.UserDb = Depends(get_current_user)):
    # print("get_current_active_user @@@@@@@@@@@@@@@@@@@@")
    # print(current_user)
    if not current_user.isActive:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_shop_user(current_user: user.UserDb = Depends(get_current_user)):
    # print("get_current_active_user @@@@@@@@@@@@@@@@@@@@")
    # print(current_user)
    if not current_user.isActive:
        raise HTTPException(status_code=400, detail="Not Shop User")
    return current_user

async def get_current_admin_user(current_user: user.UserDb = Depends(get_current_user)):
    # print("get_current_active_user @@@@@@@@@@@@@@@@@@@@")
    # print(current_user)
    if current_user.admin != True:
        raise HTTPException(status_code=401, detail="Not Admin User")
    return current_user
