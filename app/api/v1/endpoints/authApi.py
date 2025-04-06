from typing import List, Optional
import base64, string, random
from passlib.context import CryptContext
from datetime import datetime, timedelta


# from pymongo import MongoClient
from bson.json_util import dumps

import jwt
# from jwt import PyJWTError
from jose import JWTError, jwt

from pydantic import BaseModel, Json,Field, ValidationError, validator, EmailStr

from fastapi import Depends, FastAPI, Cookie, HTTPException, APIRouter , Header , File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm, OAuth2, HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.base import SecurityBase, SecurityBaseModel
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.utils import get_openapi

from starlette.status import HTTP_403_FORBIDDEN
from fastapi.responses import RedirectResponse, Response, JSONResponse
from starlette.requests import Request

from fastapi.middleware.cors import CORSMiddleware

from core.config  import ACCESS_TOKEN_EXPIRE_HOURS
# import logging
# from mongoengine import *

# from loguru import logger
from utils import util
import json

##### BEGIN : DATABSE #####
# from pydantic_sqlalchemy import sqlalchemy_to_pydantic
# from pydantic_sqlalchemy import sqlalchemy_to_pydantic

from models import  user, clientInfo
# from loguru import logger


from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates



from time import process_time, sleep

# from utils.database import SessionLocal, engine
# schemas.Base.metadata.create_all(bind=engine)

# from sqlalchemy.orm import Session

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

##### END : DATABSE #####

from repo import userRepo, authRepo
from database.mongodb  import AsyncIOMotorClient, get_database

#### BEGIN : MONGO CLIENT
# client = MongoClient("mongodb://admin:password@127.0.0.1:8999") #host uri  
# db = client.bisinnoco #Select the database  
#### END   : MONGO CLIENT


# to get a string like this run:
# openssl rand -hex 32
# SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7569f6f0f4caa6cf63b88e8d3e7"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()


templates1 = Jinja2Templates(directory="./templates1")




class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

class UserRegister(BaseModel):
    uid: str 
    username: str
    password: str
    userType: Optional[str] = None 
    description: Optional[str] = None
    active: bool = None
    
class SocialRegister(BaseModel):
    uid: str 
    username: str
    userType: Optional[str] = None 
    description: Optional[str] = None
    active: bool = None

class UserIn(BaseModel):
    # uid: str  = Field(default_factory=str(uuid1))
    uid : str = None
    username: EmailStr 
    password: str
    description: Optional[str] = None
    createDateTime: datetime =  Field(default_factory=datetime.utcnow)
    creation_datetime : datetime = None
    active: bool = None

class UserUpdate(BaseModel):
    uid: str
    username: EmailStr 
    createDateTime: datetime

class LoginForm(BaseModel):
    username: EmailStr 
    password: str



class User():
    pass
    creation_date : datetime =  Field(default_factory=datetime.utcnow)
    modified_date : datetime =  Field(default_factory=datetime.utcnow)

class UserOut(UserIn):
    pass


class UserInDB(UserIn):
    hashed_password: str


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

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        return param



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="/api_login")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# templates = Jinja2Templates(directory="/templates")
# app.mount("app/templates", StaticFiles(directory="templates"), name="templates")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)




def authenticate_user(username: str, password: str):
    user = user_repo.get_user_by_email(dbs , username)
    if not user:
        return "NO_USER"
    if not verify_password(password, user.password_hashed):
        return "NOT_AUTHORIZED"
    return user






@router.get("/page/htmlform", response_class=HTMLResponse)
def form_post(request: Request):
    result = "Type a number"
    return templates1.TemplateResponse('form.html', context={'request': request, 'result': result})

# "https://YOUR_DOMAIN/authorize?
#   response_type=code&
#   client_id=YOUR_CLIENT_ID&
#   code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM&
#   code_challenge_method=S256&
#   redirect_uri=YOUR_CALLBACK_URL&
#   scope=appointments%20contacts&
#   audience=appointments:api&
#   state=xyzABC123"





@router.post("/createClient",  tags=["auth"])
async def create_client(create: clientInfo.ClientInfoCreate, db: AsyncIOMotorClient = Depends(get_database)):
    
    userdb = await authRepo.createClientInfo(create=create , redirectUrl=clientInfo.redirectUrl, db=db )


@router.get("/get-to-redirect",  tags=["auth"])
async def getAPILogin(request: Request):
    html_content = """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1 style="padding-top: 150px; font-size:70px; color:#777777; text-align:center ">Please wait for a while</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@router.get("/show_cookie",  tags=["auth"])
async def getAPILogin(request: Request):
    return request.cookies.get("user-session");
    
    
    
@router.get("/get_api_login",  tags=["auth"])
async def getAPILogin(db: AsyncIOMotorClient =  Depends(get_database) ):
        loginForm = LoginForm
        loginForm.username = "testuser1@example.com"
        loginForm.password = 'password1'
        
        userdb = await authRepo.authenticateUser(db=db, username=loginForm.username, password=loginForm.password)
   
   
        if userdb == "NO_USER" : 
            raise HTTPException(status_code=400, detail="This user is not registered")

        if userdb == "NOT_AUTHORIZED" : 
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            

        access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        tokenExpiredAt = datetime.now() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        access_token = create_access_token(
            data={"sub": loginForm.username}, expires_delta=access_token_expires
        )

        res = await userRepo.userResponse(db=db, userdb=userdb, activeToken=access_token, tokenExpiredAt=tokenExpiredAt)

        res['userData']["tokenExpiredAt"] = res['userData']["tokenExpiredAt"].strftime("%Y-%m-%d %H:%M:%S.%f")
        res['userData']["createAt"] = res['userData']["createAt"].strftime("%Y-%m-%d %H:%M:%S.%f")
        res['userData']["update_At"] = res['userData']["update_At"].strftime("%Y-%m-%d %H:%M:%S.%f")

        # print(res)

        # content = {"access_token": access_token, "token_type": "bearer"}
        response = JSONResponse(content=res)
        response.set_cookie(key="user-session", value=access_token, httponly=True, secure=True)
        return response
        
# [1] ส่ง params {response_type} {client_id} {state} 
@router.get("/authorize")
async def read_item( response:Response, response_type: Optional[str] , client_id: Optional[str] = None, code_challenge:  Optional[str] = None, code_challenge_method: Optional[str] = None, redirect_uri: Optional[str] = None, scope: Optional[str] = None, audience: Optional[str] = None, state: Optional[str] = None, db: AsyncIOMotorClient =  Depends(get_database) ):
    # N = 30
    # code = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k = N))
    # print("The generated random string : " + str(res))
    item = {"response_type": response_type,"client_id": client_id,"code_challenge": code_challenge, "code_challenge_method": code_challenge_method, "redirect_uri":redirect_uri, "scope": scope,  "audience": audience, "state": state}
    
    
    # print(state)
    
    if (response_type != "authorization_code") or (not response_type) :
        raise HTTPException(
                        status_code=400, detail="Bad request: response_type must be authorization_code"
                    )

    if not client_id:
        raise HTTPException(
                        status_code=400, detail="Bad request: No Client ID"
                    )
    # *** เช็ค redirect_rule ถ้า clientID และ redirect_url ตรงกัน
    # *** ให้ redirect กลับตาม code and state ตาม redirect_url

    if not redirect_uri:
        raise HTTPException(
                        status_code=400, detail="Bad request: Need redirect url"
                    )
    
    code = 'test-xxxxxxx'
    N_code = 30
    code = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k = N_code))
    state = item["state"]
    request = "Hello Request"
    result = "Hello Result"
    redirect_uri = "http://localhost:8080"
    
    # me = await userRepo.getUserByEmail(db=db, username=username)
    
    # if not me:
    #     raise HTTPException(
    #                     status_code=400, detail="This Email has not been registered"
    #                 )
    
    
    response = dict()
    response.update({"result": "success","content": { "code": code, "state": state } })
    return response
    
#     response.headers['Access-Control-Allow-Origin'] = '*'
    
#     redirect_url = f"{redirect_uri}/authorization/{state}"
#     headers = 'Access-Control-Allow-Origin', '*'
#     print(response)
#     return  RedirectResponse( url=redirect_url)
#     # return templates1.TemplateResponse('form.html', context={'request': request, 'result': result})


@router.post("/api_login",  tags=["auth"])
async def login_for_access_token(loginForm: LoginForm , db: AsyncIOMotorClient =  Depends(get_database) ):
 
    userdb = await authRepo.authenticateUser(db=db, username=loginForm.username, password=loginForm.password)
   
    if userdb == "NO_USER" : 
        raise HTTPException(status_code=400, detail="This user is not registered")

    if userdb == "NOT_AUTHORIZED" : 
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        

    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    tokenExpiredAt = datetime.now() + access_token_expires
    access_token = authRepo.create_access_token(
        data={"sub": loginForm.username, "iss": "wtg.promo", "nonce": util.genRandomText(32) }, expires_delta=access_token_expires
    )

    # print(f"access_token {access_token}")

    res = await userRepo.userResponse(db=db, userdb=userdb, activeToken=access_token, tokenExpiredAt=tokenExpiredAt)


    res['userData']["tokenExpiredAt"] = res['userData']["tokenExpiredAt"].strftime("%Y-%m-%d %H:%M:%S.%f")
    res['userData']["createAt"] = res['userData']["createAt"].strftime("%Y-%m-%d %H:%M:%S.%f")
    res['userData']["update_At"] = res['userData']["update_At"].strftime("%Y-%m-%d %H:%M:%S.%f")
  


    # content = {"access_token": access_token, "token_type": "bearer"}
    response = JSONResponse(content=res)
    response.set_cookie(key="user-session", value=access_token, httponly=True, secure=True)
    return response



@router.post("/check-authentication",  tags=["auth"])
async def check_authentication(db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
 
    # print(currentUser)

    userView = user.UserView(**currentUser.dict())    
    # print(userView)
    
    return userView



@router.get("/thelogin",  tags=["auth"])
async def getLogin():
    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    tokenExpiredAt = datetime.now() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"sub": "hello"}, expires_delta=access_token_expires
    )
    spl = access_token.split('.')
    jwt_hb = f"{spl[0]}.{spl[1]}"
    jwt_s = spl[2]
    content = {"access_token": jwt_hb, "token_type": "bearer"}
    response = JSONResponse(content=res)
    response.set_cookie(key="jwt_signature", value=jwt_s, httponly=True)
    return response






@router.get("/logout",  tags=["auth"])
async def route_logout_and_remove_cookie():
    response = RedirectResponse(url="/")
    response.delete_cookie("Authorization", domain="localhost")
    return response


@router.get("/openapi.json")
async def get_open_api_endpoint(currentUser: User = Depends(authRepo.get_current_active_user)):
    return JSONResponse(get_openapi(title="FastAPI", version=1, routes=app.routes))


@router.get("/docs")
async def get_documentation(currentUser: User = Depends(authRepo.get_current_active_user)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")
