from passlib.context import CryptContext

from loguru import logger
from models import user, schemas
from database.mongodb  import AsyncIOMotorClient, get_database
from utils import util
from datetime import datetime
from . import authRepo

import orjson

# from sqlalchemy.orm import Session


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)


    
async def getUserByEmail( db: AsyncIOMotorClient, email: str) -> user.UserDb:
    row = await db["alex_office_admin"]["user"].find_one({ "email" :  email })
    # logger.info("USER_REPO EMAIL: {0}",row)   

    if row:
        return user.UserDb(**row)
   

async def createUser(db: AsyncIOMotorClient, create: user.UserCreate) -> user.UserDb:
    dbuser = user.UserDb(**create.dict())
    # dbuser.change_password(user.password)
    dbuser.id = util.getUuid()
    dbuser.hashedPassword = authRepo.get_password_hash(create.password)
    row = await db["alex_office_admin"]["user"].insert_one(dbuser.dict())

    return dbuser

async def updateUser(db: AsyncIOMotorClient, update: user.UserUpdate) -> user.UserDb:
    dbuser = await getUserByEmail(db, update.email)
    dbuser.password = update.password
    dbuser.isActive = update.isActive
    # dbuser.change_password(user.password)

    # row = await db["alex_office_admin"]["user"].insert_one(dbuser.dict())

    updated_at = await db["alex_office_admin"]["user"].update_one({"email": dbuser.email}, {'$set': dbuser.dict()})

    return dbuser

async def userResponse(db: AsyncIOMotorClient, userdb: user.UserDb, activeToken: str, tokenExpiredAt:datetime) -> dict:
    userdb.activeToken = activeToken
    userdb.tokenExpiredAt = tokenExpiredAt
    
    resp = user.UserLoginResponse(**userdb.dict())
    resp.accessToken = activeToken

    loginResp = dict()
    resp_dict = resp.dict()
    resp_dict.update(
    {
        "fullName": 'Jane Doe',
        "username": 'janedoe',
        "role": 'staff',
        "refreshToken": 'ANnsdpfihpubfhsdf87897sdflaj',
        "ability": [
            {
              "action": 'manage',
              "subject": 'all',
            }
            # {
            # "action": 'read',
            # "subject": 'ACL',
            # },
            # {
            # "action": 'read',
            # "subject": 'Auth',
            # },
        ],
        "extras": {
            "eCommerceCartItemsCount": 5,
        }
    }
    )
    loginResp["userData"] = resp_dict
    loginResp["accessToken"] = activeToken
    loginResp["refreshToken"] = activeToken
    
    # row = await db["alex_office_admin"]["user"].insert_one(dbuser.dict())
    # logger.info("updateToken >>> {0} ",loginResp)

    updated_at = await db["alex_office_admin"]["user"].update_one({"email": userdb.email}, {'$set': userdb.dict()})
    
    if updated_at.modified_count == 1:
        return loginResp
    else :
        return dict()


async def hardDelUser( db: AsyncIOMotorClient, email: str):
    row = await db["alex_office_admin"]["user"].find_one({ "email" :  email })
    # logger.info("USER_REPO EMAIL: {0}",row)

    if row:
        return user.UserDb(**row)
   
async def softDelUser( db: AsyncIOMotorClient, email: str):
    row = await db["alex_office_admin"]["user"].find_one({ "email" :  email })
    # logger.info("USER_REPO EMAIL: {0}",row)

    if row:
        return user.UserDb(**row)

