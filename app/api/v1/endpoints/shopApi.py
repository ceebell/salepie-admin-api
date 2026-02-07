from typing import List, Optional , Any, Dict

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks

from repo import  userRepo, authRepo
from models import  user

from datetime import datetime

##### BEGIN : DATABSE #####

from models import  schemas, user
# from loguru import logger
from pydantic import BaseModel, Json ,ValidationError, validator, Field, EmailStr
from database.mongodb  import AsyncIOMotorClient, get_database

# from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from core.config  import AlexEmail, ALEX_URL, AlexOffice_ClientID, AlexOffice_ApiKey
import shutil
from utils import util

##### BEGIN : HTTP CLIENT #####

import httpx
import asyncio
import json

router = APIRouter()


class ShopRegister(BaseModel):
    uid: Optional[str] = "" 
    username: Optional[str] = ""
    password: Optional[str] = ""
    shopName: Optional[str] = ""
    shopCode: Optional[str] = ""
    shopPackage : Optional[str] = ""
    shopStatusInfo: Optional[str] = ""
    shopLine : Optional[str] = ""
    shopPhone : Optional[str] = ""
    shopDescription: Optional[str] = ""
    trialStart: Optional[str] = ""
    trialEnd: Optional[str] = ""
    paid : Optional[bool] = ""
    packageStart: Optional[str] = ""
    packageEnd: Optional[str] = ""
    shopCategory: Optional[str] = ""
    shopAge : Optional[str] = ""
    shopBranchNumber : Optional[str] = ""

class ShopRegisterTrialUpdate(BaseModel):
    shopCode: Optional[str] = ""
    shopPackage : Optional[str] = ""
    shopStatusInfo: Optional[str] = ""
    trialStart: Optional[str] = ""
    trialEnd: Optional[str] = ""

class ShopRegisterPackageUpdate(BaseModel):
    shopCode: Optional[str] = ""
    shopPackage : Optional[str] = ""
    shopStatusInfo: Optional[str] = ""
    paid : Optional[bool] = False
    packageStart: Optional[str] = ""
    packageEnd: Optional[str] = ""

# class ShopRegisterPackageDb(BaseModel):
#     shopCode: Optional[str] = ""
#     shopPackage : Optional[str] = ""
#     shopStatusInfo: Optional[str] = ""
#     paid : Optional[bool] = False
#     packageStart: Optional[str] = ""
#     packageEnd: Optional[str] = ""
    


class ShopRegisterDb(BaseModel):
    uid: Optional[str] = "" 
    username: str
    shopName: Optional[str] = ""
    shopCode: Optional[str] = ""
    shopPackage : str
    shopLine : Optional[str] = ""
    shopPhone : Optional[str] = ""
    shopDescription: Optional[str] = ""
    shopStatusInfo: Optional[str] = ""
    shopCategory: str
    shopAge : Optional[str] = ""
    shopBranchNumber : Optional[str] = ""
    trialStart: Optional[datetime] = ""
    trialEnd: Optional[datetime] = ""
    paid : Optional[bool] = False
    packageStart: Optional[datetime] = ""
    packageEnd: Optional[datetime] = ""
    createDateTime: Optional[datetime] =  Field(default_factory=datetime.utcnow)
    updateAt: Optional[datetime] =  Field(default_factory=datetime.utcnow)
    createBy: Optional[str] = ""
    updateBy: Optional[str] = ""
    
class ShopRegisterView(BaseModel):
    uid: Optional[str] = "" 
    username: str
    shopName: Optional[str] = ""
    shopCode: Optional[str] = ""
    shopPackage : Optional[str] = ""
    shopLine : Optional[str] = ""
    shopPhone : Optional[str] = ""
    shopDescription: Optional[str] = ""
    shopStatusInfo: Optional[str] = ""
    shopCategory: str
    shopAge : Optional[str] = ""
    shopBranchNumber : Optional[str] = ""
    trialStart: Optional[datetime] = ""
    trialEnd: Optional[datetime] = ""
    paid : Optional[bool] = False
    packageStart: Optional[datetime] = ""
    packageEnd: Optional[datetime] = ""
    createDateTime: Optional[datetime] = ""
    updateAt: Optional[datetime] = ""
    createBy: Optional[str] = ""
    updateBy: Optional[str] = ""
    
    # "username" : "eric@gmail.com",
    # "password" : "asdfasdf",
    # "shopName" : "Eric Shop",
    # "ShopCode" : "ERS00001",
    # "ShopPackage" : "s",
    # "ShopLine" : "@Eric",
    # "ShopPhone" : "0999999999",
    # "ShopDescription" : "Eric Shop",
    # "ShopCategory" : "ร้านเช่าชุด",
    # "ShopAge" : "1-3",
    # "ShopBranchNumber" : "3"
    
CREATE_URL = f"{ALEX_URL}/api/user/test-register-shop"
async def create_shop_task(req_data):
    #*** แปลงข้อมูลจาก dict -> json
    json_data = json.dumps(req_data) 
    headers = {'Content-Type': 'application/json', 'ClientID': AlexOffice_ClientID, "APIKey": AlexOffice_ApiKey }
    async with httpx.AsyncClient(verify=False) as client:
        res = await client.post(CREATE_URL , data=json_data, headers=headers)
    
    print(f"SENDING API {res}")
    if res.status_code != 200:
        print("API NOT SUCCESS")
        raise HTTPException(status_code=400, detail=res.text)
        
    return res
#******************************************  
#*** 1.1 Create Shop 
#******************************************
@router.post("/create-shop",  tags=["shop"])
# async def createShop(db: AsyncIOMotorClient =  Depends(get_database), req : ShopRegister = None, currentUser  : User = Depends(authRepo.get_current_active_user)):
async def createShop( req : ShopRegister = None, db: AsyncIOMotorClient =  Depends(get_database)):
    try:
        # shopDb = ShopRegisterDb(**req.dict())
        # dbuser.change_password(user.password)
        modelDict = req.dict()
        modelDict["uid"] = util.getUuid()
        modelDict["shopCode"] = util.getShopCode()

        modelDict["trialStart"] = datetime.strptime(modelDict["trialStart"], '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S.%f")
        modelDict["trialEnd"] =  datetime.strptime(modelDict["trialEnd"], '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S.%f")
        modelDict["packageStart"] = datetime.strptime(modelDict["packageStart"], '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S.%f")
        modelDict["packageEnd"] = datetime.strptime(modelDict["packageEnd"], '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S.%f")

        
        #*** สำหรับส่ง API
        res = await create_shop_task(modelDict)
        #*** ถ้าส่ง api ok ค่อย save
        
        if res.status_code != 200:
            print("API NOT SUCCESS")
            raise HTTPException(status_code=400, detail="API request unsuccessful")
        
        
        
        modelDict["createDateTime"] = datetime.today().strftime("%Y-%m-%d %H:%M:%S.%f")
        modelDict["updateAt"] = datetime.today().strftime("%Y-%m-%d %H:%M:%S.%f")

        modelDict["createBy"] = "System"
        modelDict["updateBy"] = "System" 


        regdb = ShopRegisterDb(**modelDict)
        regDict = regdb.dict()
        

        # # #*** save ลง mongo
        row = await db["alex_office_admin"]["shopRegister"].insert_one(regDict)

    except:
        raise HTTPException(status_code=400, detail="Unable to create shop") 

    return modelDict

#******************************************  
#*** 1.2 Update Trial 
#*** ยืดเวลา trial
#*** Stop trial
#******************************************
async def update_trial_task(req_data):
    UPDATE_TRIAL_URL = f"{ALEX_URL}/api/user/update-trial"
    #*** แปลงข้อมูลจาก dict -> json
    json_data = json.dumps(req_data) 
    headers = {'Content-Type': 'application/json', 'ClientID': AlexOffice_ClientID, "APIKey": AlexOffice_ApiKey }
    async with httpx.AsyncClient(verify=False) as client:
        res = await client.post(UPDATE_TRIAL_URL , data=json_data, headers=headers)
    if res.status_code != 200:
        raise HTTPException(status_code=400, detail=res.text)
    return res

#{  
#     "shopCode": "20210927_84GBBI97",
#     "shopPackage": "l",
#     "statusInfo": "trial"  # {trial / notYet}
#     "trialStart": "2021-09-29",
#     "trialEnd": "2021-10-30",
# }

@router.post("/update-trial",  tags=["shop"])
# async def createShop(db: AsyncIOMotorClient =  Depends(get_database), req : ShopRegister = None, currentUser  : User = Depends(authRepo.get_current_active_user)):
async def updateTrial( req : ShopRegisterTrialUpdate = None, db: AsyncIOMotorClient =  Depends(get_database)):
    # try:
    
    modelDict = req.dict()
    modelDict["trialStart"] = datetime.strptime(modelDict["trialStart"], '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S.%f")
    modelDict["trialEnd"] =  datetime.strptime(modelDict["trialEnd"], '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S.%f")
    
    
    modelDict["updateAt"] = datetime.today().strftime("%Y-%m-%d %H:%M:%S.%f")
    modelDict["updateBy"] = "System" 


    regdb = ShopRegisterTrialUpdate(**modelDict)
    regDict = regdb.dict()

    # print(regDict)
    

    #*** สำหรับส่ง API
    res = await update_trial_task(modelDict)
    #*** ถ้าส่ง api ok ค่อย save
    
    if res.status_code != 200:
        print("API NOT SUCCESS")
        raise HTTPException(status_code=400, detail="API request unsuccessful")
    
    

    # #*** save ลง mongo
    updaterow = await db["alex_office_admin"]["shopRegister"].update_one({"shopCode":regDict["shopCode"]}, {'$set': regDict})

    # # #*** save ลง mongo
    # package_row = await db["alex_office_admin"]["shopPackage"].insert_one(regDict)

    # except:
    #     raise HTTPException(status_code=400, detail="Unable to edit trial") 

    return modelDict


#******************************************  
#*** 1.3 Update Package 
#*** update StatusInfo >>> เปลี่ยน status package
#*** update Package >>> เปลี่ยน package size S M L
#*** Stop package >>> stop package
#******************************************

async def update_package_task(req_data):
    UPDATE_PACKAGE_URL = f"{ALEX_URL}/api/user/update-package"
    #*** แปลงข้อมูลจาก dict -> json
    json_data = json.dumps(req_data) 
    headers = {'Content-Type': 'application/json', 'ClientID': AlexOffice_ClientID, "APIKey": AlexOffice_ApiKey }
    async with httpx.AsyncClient(verify=False) as client:
        res = await client.post(UPDATE_PACKAGE_URL , data=json_data, headers=headers)
    if res.status_code != 200:
        raise HTTPException(status_code=400, detail=res.text)
    return res
# {
#     "shopCode": "20210927_84GBBI97",
#     "shopPackage": "s",
#     "paid" : false,
#     "shopStatusInfo" : "notYet",
#     "packageStart": "2021-09-29",
#     "packageEnd": "2022-09-30"
# }


@router.post("/update-package",  tags=["shop"])
# async def createShop(db: AsyncIOMotorClient =  Depends(get_database), req : ShopRegister = None, currentUser  : User = Depends(authRepo.get_current_active_user)):
async def updatePackage( req : ShopRegisterPackageUpdate = None, db: AsyncIOMotorClient =  Depends(get_database)):
    # try:
        
    modelDict = req.dict()
    
    modelDict["packageStart"] = datetime.strptime(modelDict["packageStart"], '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S.%f")
    modelDict["packageEnd"] = datetime.strptime(modelDict["packageEnd"], '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S.%f")

    
    
    
    
    modelDict["updateAt"] = datetime.today().strftime("%Y-%m-%d %H:%M:%S.%f")
    modelDict["updateBy"] = "System" 


    regdb = ShopRegisterPackageUpdate(**modelDict)
    regDict = regdb.dict()

    
    # activePackage = await db["alex_office_admin"]["shopPackage"].find_one({"$and":[{"shopCode":regDict["shopCode"]} , {"active": True}]})

   
    
    # if not activePackage:
    #     raise HTTPException(status_code=400, detail="No Active Package") 

    # activePackage["updateAt"] = modelDict["updateAt"]
    # activePackage["packageStart"] = modelDict["packageStart"]
    # activePackage["packageEnd"] = modelDict["packageEnd"]
    # activePackage["shopPackage"] = modelDict["shopPackage"]
    # activePackage["paid"] = modelDict["paid"]
    # activePackage["shopStatusInfo"] = modelDict["shopStatusInfo"]
    

    print(f" model dict {modelDict}")
    #*** สำหรับส่ง API
    res = await update_package_task(modelDict)
    #*** ถ้าส่ง api ok ค่อย save
    
    if res.status_code != 200:
        print("API NOT SUCCESS")
        raise HTTPException(status_code=400, detail="API request unsuccessful")
    


    # #*** save ลง mongo
    updaterow = await db["alex_office_admin"]["shopRegister"].update_one({"shopCode":regDict["shopCode"]}, {'$set': regDict})
    # await db["alex_office_admin"]["shopPackage"].update_one( {"$and":[{"shopCode":regDict["shopCode"]} , {"active": True}]} , {'$set': activePackage})

    # except:
    #     raise HTTPException(status_code=400, detail="Unable to edit package") 

    return modelDict



   
#******************************************  
#*** 1.4 Get All 
#******************************************

GET_ALL_SHOP_URL = f"{ALEX_URL}/api/user/get-all-shop"
async def get_all_shop_task(req_data):
    #*** แปลงข้อมูลจาก dict -> json
    json_data = json.dumps(req_data) 
    headers = {'Content-Type': 'application/json', 'ClientID': AlexOffice_ClientID, "APIKey": AlexOffice_ApiKey }
    async with httpx.AsyncClient(verify=False) as client:
        res = await client.post(GET_ALL_SHOP_URL , data=json_data, headers=headers)
    
    if res.status_code != 200:
        print("API NOT SUCCESS")
        raise HTTPException(status_code=400, detail=res.text)
    return res

@router.post("/get-all-shop",  tags=["shop"])
# async def createShop(db: AsyncIOMotorClient =  Depends(get_database), req : ShopRegister = None, currentUser  : User = Depends(authRepo.get_current_active_user)):
async def getAllShop( db: AsyncIOMotorClient =  Depends(get_database)):
     #*** สำหรับส่ง API
    dataDict = dict()
    res = await get_all_shop_task(dataDict)

    return res.json()




#******************************************  
#*** 1.5 Renew Package 
#*** add new package
#******************************************

async def renew_package_task(req_data):
    RENEW_PACKAGE_URL = f"{ALEX_URL}/api/user/renew-package"
    #*** แปลงข้อมูลจาก dict -> json
    json_data = json.dumps(req_data) 
    headers = {'Content-Type': 'application/json', 'ClientID': AlexOffice_ClientID, "APIKey": AlexOffice_ApiKey }
    async with httpx.AsyncClient(verify=False) as client:
        res = await client.post(RENEW_PACKAGE_URL , data=json_data, headers=headers)
    if res.status_code != 200:
        raise HTTPException(status_code=400, detail=res.text)
    return res
# {
#     "shopCode": "20210927_84GBBI97",
#     "shopPackage": "s",
#     "paid" : false,
#     "shopStatusInfo" : "notYet",
#     "packageStart": "2021-09-29",
#     "packageEnd": "2022-09-30"
# }


@router.post("/renew-package",  tags=["shop"])
# async def createShop(db: AsyncIOMotorClient =  Depends(get_database), req : ShopRegister = None, currentUser  : User = Depends(authRepo.get_current_active_user)):
async def renewPackage( req : ShopRegisterPackageUpdate = None, db: AsyncIOMotorClient =  Depends(get_database)):
    # try:
    rows =  db["alex_office_admin"]["shopRegister"].find({ "shopCode" :  req.shopCode })
    shopList =   [row async for row in rows]
   
    print(f"shopList : {shopList}")  

    if len(shopList) <= 0:
        raise HTTPException(status_code=400, detail="Shop Code Not Found") 

    try:

        packages =  db["alex_office_admin"]["shopPackage"].find({ "shopCode" :  req.shopCode })
        packageList = [package["seq"] async for package in packages]
       
        if(len(packageList) <= 0 ):
            maxSeq = 0
        else:
            maxSeq = max(packageList)

        modelDict = req.dict()
        modelDict["packageStart"] = datetime.strptime(modelDict["packageStart"], '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S.%f")
        modelDict["packageEnd"] = datetime.strptime(modelDict["packageEnd"], '%Y-%m-%d').strftime("%Y-%m-%d %H:%M:%S.%f")

        
        #*** สำหรับส่ง API
        res = await renew_package_task(modelDict)
        #*** ถ้าส่ง api ok ค่อย save
        
        if res.status_code != 200:
            print("API NOT SUCCESS")
            raise HTTPException(status_code=400, detail="API request unsuccessful")
        
        regdb = ShopRegisterPackageUpdate(**modelDict)
        regDict = regdb.dict()

        renew = regDict.copy()

        renew["updateAt"] = datetime.today().strftime("%Y-%m-%d %H:%M:%S.%f")
        renew["updateBy"] = "System" 
        shop = shopList.pop()
        renew["seq"] = maxSeq + 1
        renew["uid"] =  util.getUuid()
        renew["shopName"] = shop["shopName"]
        renew["active"] = True


        # #*** save ลง mongo
        updaterow = await db["alex_office_admin"]["shopRegister"].update_one({"shopCode":regDict["shopCode"]}, {'$set': regDict})
        # # #*** save ลง mongo
        await db["alex_office_admin"]["shopPackage"].update_many({"shopCode":regDict["shopCode"]}, {'$set': {"active": False}})
        package_row = await db["alex_office_admin"]["shopPackage"].insert_one(renew)
    except:
        raise HTTPException(status_code=400, detail="Unable to edit package") 

    return modelDict





   
#******************************************  
#*** 1.6 Get A Shop 
#******************************************

async def get_one_shop_task(shopCode):
    GET_ONE_SHOP_URL = f"{ALEX_URL}/api/user/get-shop/{shopCode}"
    #*** แปลงข้อมูลจาก dict -> json
    # json_data = json.dumps(req_data) 
    headers = {'Content-Type': 'application/json', 'ClientID': AlexOffice_ClientID, "APIKey": AlexOffice_ApiKey }
    async with httpx.AsyncClient(verify=False) as client:
        res = await client.get(GET_ONE_SHOP_URL ,  headers=headers)
    
    if res.status_code != 200:
        print("API NOT SUCCESS")
        raise HTTPException(status_code=400, detail=res.text)
    return res

@router.get("/get-one-shop/{shopCode}",  tags=["shop"])
# async def createShop(db: AsyncIOMotorClient =  Depends(get_database), req : ShopRegister = None, currentUser  : User = Depends(authRepo.get_current_active_user)):
async def getOneShop( shopCode: str, db: AsyncIOMotorClient =  Depends(get_database)):
     #*** สำหรับส่ง API
    res = await get_one_shop_task(shopCode)
    return res.json()

