from typing import List, Optional , Any, Dict

from fastapi import APIRouter, Depends, HTTPException


from repo import  userRepo, authRepo, apiRepo

##### BEGIN : DATABSE #####

from models import  schemas, user, ApiModel
# from loguru import logger
from pydantic import BaseModel, Json ,ValidationError, validator, Field, EmailStr
from database.mongodb import AsyncIOMotorClient, get_database

from utils import util


router = APIRouter()


   
@router.get("/getAllFields")
async def getAllFields( db: AsyncIOMotorClient =  Depends(get_database)):
    rows = db["alex_office_admin"]["csharpModel"].find({})
    
    if rows:
        xList = [ csharpModel.CsharpModelView(**row) async for row in rows  ]
        yList = [];
        for item in xList :
            tmp = item.dict()
        
            if tmp["fields"] :
                # y[len(y):] = item["fields"] 
                yList.extend(tmp["fields"])   
        return yList
    else:
        raise HTTPException(
                        status_code=400, detail="Bad request: Unable to get records"
                    )




@router.post("/createApi",  tags=["api"])
async def createApi(create: ApiModel.ApiModelInput,  db: AsyncIOMotorClient =  Depends(get_database)):
    #*** แปลงให้อยู่ในรูป database 
    apiDb = ApiModel.ApiModelDb(**create.dict())

    #*** Check unique in certain field
    uni = await apiRepo.checkUnique( db=db,  table="apiModel" , filed="modelName", value=apiDb.modelName )

    print(uni)

    if not uni:
        raise HTTPException(
                        status_code=400, detail="Model name has been taken"
                    )

    apiDb.uid = util.getUuid()

    row = await db["genapi"]["apiModel"].insert_one(apiDb.dict())
    
    if row:
        # res = apiDb.dict()
        return apiDb
    else:
        raise HTTPException(
                        status_code=400, detail="Bad request: Unable to update record"
                    )

@router.post("/updateApi/{id}",  tags=["api"])
async def updateApi(id : str ,input: ApiModel.ApiModelInput,  db: AsyncIOMotorClient =  Depends(get_database)):
    
    apiDb = ApiModel.ApiModelDb(**input.dict())
    apiDict = apiDb.dict()

    row = await db["genapi"]["apiModel"].update_one({"uid": id}, {'$set': apiDb.dict()})
    
    if row:
        # res = apiDb.dict()
        return apiDb
    else:
        raise HTTPException(
                        status_code=400, detail="Bad request: Unable to update record"
                    )


@router.get("/getModel/{name}",  tags=["api"])
async def getModel(name : str,  db: AsyncIOMotorClient =  Depends(get_database)):
    
    nameStr = f"{name}"

    
    res = await db["genapi"]["apiModel"].find_one({ "modelName" :  {'$regex':nameStr , '$options' : 'i'}}) 
    
    if res:
        # res = apiDb.dict()
        return ApiModel.ApiModelView(**res)
    else:
        raise HTTPException(
                        status_code=400, detail="Could not be found"
                    )

