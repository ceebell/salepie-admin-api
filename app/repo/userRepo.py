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

def get_password_hash(password):
    return pwd_context.hash(password)


    
async def getUserByEmail( db: AsyncIOMotorClient, username: str) -> user.UserDb:

    # print(f" username  >>>> ",username)

    row = await db["ecouponv1"]["user"].find_one({ "username" :  username })
    # print(row)  

    if row:
        return user.UserDb(**row)

async def eCouponCreateUser(db: AsyncIOMotorClient, create: dict) -> dict:
    
    # print(create)
    dbuser = user.UserDb(**create)
    # print(dbuser)



    # dbuser.change_password(user.password)
    dbuser.uid = util.getUuid()
    dbuser.hashedPassword = authRepo.get_password_hash(create["password"])

    row = await db["ecouponv1"]["user"].insert_one(dbuser.dict())

    return dbuser.dict()
   

async def createUser(db: AsyncIOMotorClient, create: user.UserCreate) -> user.UserDb:
    dbuser = user.UserDb(**create.dict())
    # dbuser.change_password(user.password)
    dbuser.uid = util.getUuid()
    dbuser.hashedPassword = authRepo.get_password_hash(create.password)
    row = await db["ecouponv1"]["user"].insert_one(dbuser.dict())

    return dbuser

async def addSocialUser(db: AsyncIOMotorClient, create: user.SocialRegister) -> user.UserView:
    dbuser = user.UserDb(**create.dict())
    # dbuser.change_password(user.password)
    dbuser.id = util.getUuid()
    row = await db["ecouponv1"]["user"].insert_one(dbuser.dict())
    
    # print(f"after insert_one {row}")
    
    if row :
        return user.UserView(**dbuser.dict())

    return None

# 

async def updateUser(db: AsyncIOMotorClient, update: user.UserUpdate) -> user.UserView:
    dbuser = await getUserByEmail(db, update.username)
    dbuser.password = update.password
    dbuser.isActive = update.isActive
    # dbuser.change_password(user.password)

    # row = await db["ecouponv1"]["user"].insert_one(dbuser.dict())

    updated_at = await db["ecouponv1"]["user"].update_one({"username": dbuser.username}, {'$set': dbuser.dict()})

    return dbuser

async def updateImage (db: AsyncIOMotorClient, userdb: user.UserDb, imageList: List) :
    
    updated_user = userdb.dict()
    
    
    existingImages = updated_user["images"]
    
    
    # print(f"\n\n\updated_user['images'] >>>> {updated_user['images']}\n\n\n")
    
    # print(f"\n\n\existingImages >>>> {existingImages}\n\n\n")
    
    updated_user = util.convertDateTime(updated_user)
    
    
    # print(f"\n\n\AFTER CONVERTING >>>> {updated_user}\n\n\n")
    
    # updated_user["tokenExpiredAt"] = updated_user["tokenExpiredAt"].strftime("%Y-%m-%d %H:%M:%S.%f")
    # updated_user["createAt"] = updated_user["createAt"].strftime("%Y-%m-%d %H:%M:%S.%f")
    # updated_user["update_At"] = updated_user["update_At"].strftime("%Y-%m-%d %H:%M:%S.%f")
    
    existingImages.extend(imageList)
    updated_user["images"] = existingImages
    # existingImages.append(imageList)
    
    
    # print(f"\n\n\nimages >>>> {existingImages}\n\n\n")
    
    
    updated = await db["ecouponv1"]["user"].update_one({"username": updated_user["username"]}, {'$set': updated_user })

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
    #     "username": 'janedoe',
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
    
    # row = await db["ecouponv1"]["user"].insert_one(dbuser.dict())
    # logger.info("updateToken >>> {0} ",loginResp)

    updated_at = await db["ecouponv1"]["user"].update_one({"username": userdb.username}, {'$set': userdb.dict()})
    
    if updated_at.modified_count == 1:
        return loginResp
    else :
        return dict()


async def hardDelUser( db: AsyncIOMotorClient, username: str):
    row = await db["ecouponv1"]["user"].find_one({ "username" :  username })
    # logger.info("USER_REPO EMAIL: {0}",row)

    if row:
        return user.UserDb(**row)
   
async def softDelUser( db: AsyncIOMotorClient, username: str):
    row = await db["ecouponv1"]["user"].find_one({ "username" :  username })
    # logger.info("USER_REPO EMAIL: {0}",row)

    if row:
        return user.UserDb(**row)

def whenCreate( model : dict , username: str): 
    
    if "createBy" in model:
        model["createBy"] = username
    if "updateBy" in model:
        model["updateBy"] = username
    
    if "createAt" in model:
        model["createAt"] = model["createAt"].strftime("%Y-%m-%d %H:%M:%S.%f")
    if "updateAt" in model:
        model["updateAt"] = model["updateAt"].strftime("%Y-%m-%d %H:%M:%S.%f")
        
    if "update_At" in model:
        model["update_At"] = model["update_At"].strftime("%Y-%m-%d %H:%M:%S.%f")
    
    return model

def convertDateTime( model : dict , fieldName: str): 
    if fieldName in model:
        model[fieldName] = model[fieldName].strftime("%Y-%m-%d %H:%M:%S.%f")
   
    
    return model

def whenUpdate( model : dict , username: str): 
    
    if "updateBy" in model:
        model["updateBy"] = username
    
    if "updateAt" in model:
            model["updateAt"] = model["updateAt"].strftime("%Y-%m-%d %H:%M:%S.%f")
        
    if "update_At" in model:
        model["update_At"] = model["update_At"].strftime("%Y-%m-%d %H:%M:%S.%f")
    
    return model

# def convertDate( arr : List ): 
    
#     for model in arr:
#         if 

    
#     return model



