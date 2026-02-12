from passlib.context import CryptContext
from typing import List, Optional

# from loguru import logger
from models import user, schemas
from database.mongodb  import AsyncIOMotorClient, get_database
from utils import util
from datetime import datetime
from . import authRepo

from fastapi import APIRouter, Depends, HTTPException

import orjson

# from sqlalchemy.orm import Session


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    safe_password = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.hash(safe_password)


    
async def getUserByEmail( db: AsyncIOMotorClient , email: str) -> user.UserDb:

# print(f" email  >>>> ",email)

    row = await db["salepiev1"]["user"].find_one({ "email" :  email })
    # print(row)  

    if row:
        return user.UserDb(**row)

async def eCouponCreateUser(db: AsyncIOMotorClient, create: dict) -> dict:
    
    # print(create)
    dbuser = user.UserDb(**create.model_dump())
    # print(dbuser)



    # dbuser.change_password(user.password)
    dbuser.uid = util.getUuid()
    dbuser.hashedPassword = authRepo.get_password_hash(create["password"])

    row = await db["salepiev1"]["user"].insert_one(dbuser.dict())

    return dbuser.model_dump()
   

async def createUserInTheSameDomain(db: AsyncIOMotorClient, create: user.UserCreate, currentUser) -> user.UserDb:
    
    payload = create.model_dump()
    dbuser = user.UserDb(**payload)
    # dbuser.change_password(user.password)
    dbuser.uid = util.getUuid()

    # --- assign ให้อยู่ใน domain เดียวกับ current user ---
    dbuser.domainId = currentUser.domainId

    # --- ยังไม่ได้สร้าง Password ตอนนี้ สร้าง hash ให้กับ user นั้น  ---
    # dbuser.hashedPassword = authRepo.get_password_hash(create.password)
    row = await db["salepiev1"]["user"].insert_one(dbuser.model_dump())

    return dbuser


async def createUser(db: AsyncIOMotorClient, create: user.UserCreate) -> user.UserDb:
    
    payload = create.model_dump()
    dbuser = user.UserDb(**payload)
    # dbuser.change_password(user.password)
    dbuser.uid = util.getUuid()

    # dbuser.hashedPassword = authRepo.get_password_hash(create.password)
    row = await db["salepiev1"]["user"].insert_one(dbuser.model_dump())

    return dbuser

async def addSocialUser(db: AsyncIOMotorClient, create: user.SocialRegister) -> user.UserView:
    dbuser = user.UserDb(**create.dump_json())
    # dbuser.change_password(user.password)
    dbuser.id = util.getUuid()
    row = await db["salepiev1"]["user"].insert_one(dbuser.dump_json())
    
    # print(f"after insert_one {row}")
    
    if row :
        return user.UserView(**dbuser.dict())

    return None

# 

async def updateUser(db: AsyncIOMotorClient, update: user.UserUpdate) -> user.UserView:
    dbuser = await getUserByEmail(db, update.email)
    dbuser.password = update.password
    dbuser.isActive = update.isActive
    # dbuser.change_password(user.password)

    # row = await db["salepiev1"]["user"].insert_one(dbuser.dict())

    updated_at = await db["salepiev1"]["user"].update_one({"email": dbuser.email}, {'$set': dbuser.dict()})

    return dbuser

async def updateImage (db: AsyncIOMotorClient, userdb: user.UserDb, imageList: List) :
    
    updated_user = userdb.dict()
    
    
    existingImages = updated_user["images"]
    
    
    # print(f"\n\n\updated_user['images'] >>>> {updated_user['images']}\n\n\n")
    
    # print(f"\n\n\existingImages >>>> {existingImages}\n\n\n")
    
    updated_user = util.convertDateTime(updated_user)
    
    
    # print(f"\n\n\AFTER CONVERTING >>>> {updated_user}\n\n\n")
    
    # updated_user["tokenExpiredAt"] = updated_user["tokenExpiredAt"].strftime("%Y-%m-%d %H:%M:%S.%f")
    # updated_user["createDateTime"] = updated_user["createDateTime"].strftime("%Y-%m-%d %H:%M:%S.%f")
    # updated_user["updateDateTime"] = updated_user["updateDateTime"].strftime("%Y-%m-%d %H:%M:%S.%f")
    
    existingImages.extend(imageList)
    updated_user["images"] = existingImages
    # existingImages.append(imageList)
    
    
    # print(f"\n\n\nimages >>>> {existingImages}\n\n\n")
    
    
    updated = await db["salepiev1"]["user"].update_one({"email": updated_user["email"]}, {'$set': updated_user })

    # return user.UserView(**updated_user)
    return updated_user

async def userResponse(db: AsyncIOMotorClient, userdb: user.UserDb, activeToken: str, tokenExpiredAt:datetime) -> dict:
    userdb.activeToken = activeToken
    userdb.tokenExpiredAt = tokenExpiredAt
    
    resp = user.UserLoginResponse(**userdb.dict())
    # resp.accessToken = activeToken

    loginResp = dict()
    resp_dict = resp.dict()
    # resp_dict.update(
    # {
    #     "fullName": 'Jane Doe',
    #     "email": 'janedoe',
    #     "role": ['admin', "brand"],
    #     "refreshToken": 'ANnsdpfihpubfhsdf87897sdflaj',
    #     "ability": [
    #         {
    #           "action": 'manage',
    #           "subject": 'all',
    #         }
    #         # {
    #         # "action": 'read',
    #         # "subject": 'ACL',
    #         # },
    #         # {
    #         # "action": 'read',
    #         # "subject": 'Auth',
    #         # },
    #     ],
    #     "extras": {
    #         "eCommerceCartItemsCount": 5,
    #     }
    # }
    # )
    loginResp["userData"] = resp_dict
    loginResp["accessToken"] = activeToken
    # loginResp["refreshToken"] = activeToken
    
    # row = await db["salepiev1"]["user"].insert_one(dbuser.dict())
    # logger.info("updateToken >>> {0} ",loginResp)

    updated_at = await db["salepiev1"]["user"].update_one({"email": userdb.email}, {'$set': userdb.dict()})
    
    if updated_at.modified_count == 1:
        return loginResp
    else :
        return dict()


async def hardDelUser( db: AsyncIOMotorClient, email: str):
    row = await db["salepiev1"]["user"].find_one({ "email" :  email })
    # logger.info("USER_REPO EMAIL: {0}",row)

    if row:
        return user.UserDb(**row)
   
async def softDelUser( db: AsyncIOMotorClient, email: str):
    row = await db["salepiev1"]["user"].find_one({ "email" :  email })
    # logger.info("USER_REPO EMAIL: {0}",row)

    if row:
        return user.UserDb(**row)

def whenCreate( model : dict , email: str): 
    
    if "createBy" in model:
        model["createBy"] = email
    if "updateBy" in model:
        model["updateBy"] = email
    
    if "createDateTime" in model:
        model["createDateTime"] = model["createDateTime"].strftime("%Y-%m-%d %H:%M:%S.%f")
    if "updateAt" in model:
        model["updateAt"] = model["updateAt"].strftime("%Y-%m-%d %H:%M:%S.%f")
        
    if "updateDateTime" in model:
        model["updateDateTime"] = model["updateDateTime"].strftime("%Y-%m-%d %H:%M:%S.%f")
    
    return model

def convertDateTime( model : dict , fieldName: str): 
    if fieldName in model:
        model[fieldName] = model[fieldName].strftime("%Y-%m-%d %H:%M:%S.%f")
   
    
    return model

def whenUpdate( model : dict , email: str): 
    
    if "updateBy" in model:
        model["updateBy"] = email
    
    if "updateAt" in model:
            model["updateAt"] = model["updateAt"].strftime("%Y-%m-%d %H:%M:%S.%f")
        
    if "updateDateTime" in model:
        model["updateDateTime"] = model["updateDateTime"].strftime("%Y-%m-%d %H:%M:%S.%f")
    
    return model

# def convertDate( arr : List ): 
    
#     for model in arr:
#         if 

    
#     return model



