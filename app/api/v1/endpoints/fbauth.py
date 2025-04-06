
# # INSTALL pyjwt / httplib2 / google-auth

# from typing import Optional
# from datetime import datetime, timedelta

# import jwt
# from jwt import PyJWTError

# from fastapi import Depends, FastAPI, HTTPException, APIRouter
# from fastapi.encoders import jsonable_encoder

# from fastapi.openapi.docs import get_swagger_ui_html
# from fastapi.openapi.utils import get_openapi

# from starlette.status import HTTP_403_FORBIDDEN
# from starlette.responses import RedirectResponse, JSONResponse, HTMLResponse
# from starlette.requests import Request

# from pydantic import BaseModel

# import httplib2

# from database.mongodb  import AsyncIOMotorClient, get_database
# from core.config import ACCESS_TOKEN_EXPIRE_HOURS
# from models import  user
# from utils import util

# from repo import userRepo, authRepo
# from core.config  import FB_AlexOffice_ClientID, FB_AlexOffice_ClientSecret

# router = APIRouter()

# clientId = FB_AlexOffice_ClientID
# clientSecret = FB_AlexOffice_ClientSecret




# class FbLoginForm(BaseModel):
#     accessToken: str = None
#     data_access_expiration_time: str
#     expiresIn : int
#     graphDomain: str
#     signedRequest : str
#     userID: str

# @router.post("/facebook-swap-token",  tags=["facebook"])
# # DEBUG LINK >>> 'https://graph.facebook.com/debug_token?input_token=EAACY0wBkxHIBAIo23Un8q383jPhNlA8OZAx6BO64aoPOM95Xw1dT15fttVyEQaSLL9gwmqVgciEZCUnNFm3YPP6JQwdPBnb3H1K6wspr8G8BhUce1NwZB5UlNXVz3BIlkqA3bBXM5uXbGSfGJFZB8dPe2CZCJzqX1lyiuKyIMB7hReN6NuVrRMsYN86mfhFwPGsmFCqxc8QZDZD&access_token=168032012125298|uaWw54vZhV7vSwnzocGHmLPEkyI'
# # REQUEST EMAIL >>> curl -i -X GET "https://graph.facebook.com/v11.0/me?fields=id%2Cname%2Cemail&access_token=EAACY0wBkxHIBALtQY77OH9CudNOtdt4I3oZCnSZA7enJLNdaKuhm9OYpaefrEVVtAZCAvDkT7jtzUztCxWSMniy2jrktOOmp6TLLWd4b2WcTO9eXHuVXQxMpIW1DM68waQ2Q6PMkMEOR2bNVBCzzsYzm6hCqnJzX4RCHdMjYA5ZAFA2DA2s8CY8RUlX0LPBmDA02MAzIN5VptZCDRPfL4RdH8qIC02yPyrZAiIA1DG4Q4awj6PuOpZC"
# # async def createShop(db: AsyncIOMotorClient =  Depends(get_database), req : ShopRegister = None, currentUser  : User = Depends(authRepo.get_current_active_user)):
# async def facebook_login( req : FbLoginForm = None, db: AsyncIOMotorClient =  Depends(get_database)):
    
#     #*** userToken ได้มาจาก VUE.JS ที่ user login หน้า เว็บ
#     userToken = "EAACY0wBkxHIBALtQY77OH9CudNOtdt4I3oZCnSZA7enJLNdaKuhm9OYpaefrEVVtAZCAvDkT7jtzUztCxWSMniy2jrktOOmp6TLLWd4b2WcTO9eXHuVXQxMpIW1DM68waQ2Q6PMkMEOR2bNVBCzzsYzm6hCqnJzX4RCHdMjYA5ZAFA2DA2s8CY8RUlX0LPBmDA02MAzIN5VptZCDRPfL4RdH8qIC02yPyrZAiIA1DG4Q4awj6PuOpZC"
    
#     #*** ขอ appToken ก่อน ได้จาก ClientID + ClientSecret
#     appLink = 'https://graph.facebook.com/oauth/access_token?client_id=' + clientId + '&client_secret=' + clientSecret + '&grant_type=client_credentials'
#     appToken = requests.get(appLink).json()['access_token']
    
#     #*** debug token ที่ได้จาก VUE.JS ว่าเป็น ของ FACEBOOK หรือไม่  
        
    
#     debugLink = f"https://graph.facebook.com/debug_token?input_token={userToken}&access_token={appToken}"
#     userId = requests.get(debugLink).json()['data']['user_id']
    
#     #*** ขอ email ของ user
#     reqLink = f"https://graph.facebook.com/v11.0/me?fields=id,name,email&access_token={userToken}"
#     resData = requests.get(reqLink).json()
    
    
    