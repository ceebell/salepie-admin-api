from typing import List, Optional , Any, Dict

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks


from repo import  userRepo, authRepo, fileRepo, utilRepo, couponRepo

from loguru import logger

##### BEGIN : DATABSE #####

from models import  schemas, user
# from loguru import logger
from pydantic import BaseModel, Json ,ValidationError, validator, Field, EmailStr
from database.mongodb  import AsyncIOMotorClient, get_database

# from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from core.config  import AlexEmail
import shutil
import uuid

from utils import util

from datetime import datetime, date
from dateutil.parser import parse


import copy



router = APIRouter()


class BrandIn(BaseModel):
    # uid: Optional[str] = "" 
    username: str
    password: str
    name: str
    description: Optional[str] = ""
    # status: Optional[str] = ""
    credit: Optional[int] = 0
    smsCredit: Optional[int] = 0
    smsSender : Optional[str] = ""
    # smsText : Optional[str] = ""
    packageSize: Optional[str] = "s"
    # createDateTime : Optional[str] = ""
    # createdBy : Optional[str] = ""
    redeemCode:Optional[str] = ""
    # verificationCode: Optional[str] = ""
    # admin : Optional[bool] = False
    # smsSender: Optional[str] = ""
    # smsContent : Optional[str] = ""
    smsUsingAmount : Optional[int] = 1


class BrandEdit(BaseModel):
    # uid: Optional[str] = ""
    # username: str
    # password: str
    name: Optional[str] = ""
    description: Optional[str] = ""
    # status: Optional[str] = ""
    credit: Optional[int] = 0
    smsCredit: Optional[int] = 0
    # smsSender : Optional[str] = ""
    # smsText : Optional[str] = ""
    packageSize: Optional[str] = "s"
    # createDateTime : Optional[datetime] =  Field(default_factory=datetime.utcnow)
    # createdBy : Optional[str] = ""
    redeemCode:Optional[List[str]] = []
    # verificationCode: Optional[str] = ""
    # admin : Optional[bool] = False
    # smsSender: Optional[str] = ""
    # smsContent : Optional[str] = ""
    # smsUsingAmount : Optional[int] = 1

class BrandUpdate(BaseModel):
    uid: Optional[str] = ""
    # username: str
    # password: str
    name: Optional[str] = ""
    description: Optional[str] = ""
    # status: Optional[str] = ""
    credit: Optional[int] = 0
    smsCredit: Optional[int] = 0
    smsSender : Optional[str] = ""
    smsText : Optional[str] = ""
    packageSize: Optional[str] = "s"
    # createDateTime : Optional[datetime] =  Field(default_factory=datetime.utcnow)
    # createdBy : Optional[str] = ""
    redeemCode:Optional[List[str]] = []
    # verificationCode: Optional[str] = ""
    # admin : Optional[bool] = False
    # smsSender: Optional[str] = ""
    # smsContent : Optional[str] = ""
    # smsUsingAmount : Optional[int] = 1

class BrandUpdateRedeemCode(BaseModel):
    # uid: Optional[str] = ""
    # username: str
    # password: str
    # name: Optional[str] = ""
    # description: Optional[str] = ""
    # status: Optional[str] = ""
    # credit: Optional[int] = 0
    # smsCredit: Optional[int] = 0
    smsSender : Optional[str] = ""
    # smsText : Optional[str] = ""
    # packageSize: Optional[str] = "s"
    # createDateTime : Optional[datetime] =  Field(default_factory=datetime.utcnow)
    # createdBy : Optional[str] = ""
    redeemCode:Optional[List[str]] = []
    # verificationCode: Optional[str] = ""
    # admin : Optional[bool] = False
    # smsSender: Optional[str] = ""
    # smsContent : Optional[str] = ""
    # smsUsingAmount : Optional[int] = 1

class BrandUpdateCouponCredit(BaseModel):
    # uid: Optional[str] = ""
    # username: str
    # password: str
    # name: Optional[str] = ""
    # description: Optional[str] = ""
    # status: Optional[str] = ""
    credit: Optional[int] = 0
    # smsCredit: Optional[int] = 0
    # smsSender : Optional[str] = ""
    # smsText : Optional[str] = ""
    # packageSize: Optional[str] = "s"
    # createDateTime : Optional[datetime] =  Field(default_factory=datetime.utcnow)
    # createdBy : Optional[str] = ""
    # redeemCode:Optional[List[str]] = []
    # verificationCode: Optional[str] = ""
    # admin : Optional[bool] = False
    # smsSender: Optional[str] = ""
    # smsContent : Optional[str] = ""
    # smsUsingAmount : Optional[int] = 1

class BrandUpdateSmsCredit(BaseModel):
    # uid: Optional[str] = ""
    # username: str
    # password: str
    # name: Optional[str] = ""
    # description: Optional[str] = ""
    # status: Optional[str] = ""
    # credit: Optional[int] = 0
    smsCredit: Optional[int] = 0
    # smsSender : Optional[str] = ""
    # smsText : Optional[str] = ""
    # packageSize: Optional[str] = "s"
    # createDateTime : Optional[datetime] =  Field(default_factory=datetime.utcnow)
    # createdBy : Optional[str] = ""
    # redeemCode:Optional[List[str]] = []
    # verificationCode: Optional[str] = ""
    # admin : Optional[bool] = False
    # smsSender: Optional[str] = ""
    # smsContent : Optional[str] = ""
    # smsUsingAmount : Optional[int] = 1


class BrandDb(BaseModel):
    uid: Optional[str] = ""
    # username: str
    # password: str
    name: Optional[str] = ""
    description: Optional[str] = ""
    status: Optional[str] = ""
    credit: Optional[int] = 0
    smsCredit: Optional[int] = 0
    smsSender : Optional[str] = ""
    smsText : Optional[str] = ""
    packageSize: Optional[str] = "s"
    createDateTime : Optional[datetime] =  Field(default_factory=datetime.utcnow)
    createdBy : Optional[str] = ""
    redeemCode:Optional[List[str]] = []
    verificationCode: Optional[str] = ""
    admin : Optional[bool] = False
    smsSender: Optional[str] = ""
    # smsContent : Optional[str] = ""
    # smsUsingAmount : Optional[int] = 1


class BrandOut(BaseModel):
    uid: Optional[str] = ""
    # username: str
    # password: str
    name: Optional[str] = ""
    description: Optional[str] = ""
    status: Optional[str] = ""
    credit: Optional[int] = 0
    smsCredit: Optional[int] = 0
    smsSender : Optional[str] = ""
    smsText : Optional[str] = ""
    packageSize: Optional[str] = "s"
    createDateTime : Optional[datetime]
    createdBy : Optional[str] = ""
    redeemCode:Optional[List[str]] = []
    verificationCode: Optional[str] = ""
    # admin : Optional[bool] = False
    smsSender: Optional[str] = ""
    # smsContent : Optional[str] = ""
    # smsUsingAmount : Optional[int] = 1
    campaignCount : Optional[int] = 0
    ownerEmail: Optional[str]

class CampaignIn(BaseModel):
    # uid: Optional[str] = ""
    dataImage: Optional[str] = ""
    name: Optional[str] = ""
    code: Optional[str] = ""
    description: Optional[str] = ""
    status: Optional[str] = ""
    startDateTime : Optional[str] = ""
    endDateTime : Optional[str] = ""
    # createDateTime : Optional[datetime]
    createdBy : Optional[str] = ""
    totalAmount : Optional[float] = 0
    usedAmount : Optional[float] = 0
    domainId : Optional[str] = ""
    # termAndCondition : Optional[str] = ""
    # smsSender: Optional[str] = ""
    # smsContent : Optional[str] = ""
    smsUsedCredit : Optional[int] = 1
    # redeemType: Optional[str] = "" #*** code_redeem / self_redeem / no_redeem
    # displayCustomerInfo: Optional[str] = "" # notDisplay / display

class CampaignEdit(BaseModel):
    # uid: Optional[str] = ""
    dataImage: Optional[str] = ""
    name: Optional[str] = ""
    code: Optional[str] = ""
    description: Optional[str] = ""
    # status: Optional[str] = ""
    startDateTime : Optional[str] = ""
    endDateTime : Optional[str] = ""
    # createDateTime : Optional[datetime]
    # createdBy : Optional[str] = ""
    # totalAmount : Optional[float] = 0
    # usedAmount : Optional[float] = 0
    # domainId : Optional[str] = ""
    termAndCondition : Optional[str] = ""
    smsSender: Optional[str] = ""
    smsContent : Optional[str] = ""
    smsUsedCredit : Optional[int] = 1
    redeemType: Optional[str] = "" #*** code_redeem / self_redeem / no_redeem
    displayCustomerInfo: Optional[str] = "" # notDisplay / display

class CampaignUpdateTerm(BaseModel):
    # uid: Optional[str] = ""
    # dataImage: Optional[str] = ""
    # name: Optional[str] = ""
    # code: Optional[str] = ""
    # description: Optional[str] = ""
    # status: Optional[str] = ""
    # startDateTime : Optional[str] = ""
    # endDateTime : Optional[str] = ""
    # createDateTime : Optional[datetime]
    # createdBy : Optional[str] = ""
    # totalAmount : Optional[float] = 0
    # usedAmount : Optional[float] = 0
    # domainId : Optional[str] = ""
    termAndCondition : Optional[str] = ""
    # smsSender: Optional[str] = ""
    # smsContent : Optional[str] = ""
    # smsUsedCredit : Optional[int] = 1
    # redeemType: Optional[str] = "" #*** code_redeem / self_redeem / no_redeem


class CampaignDb(BaseModel):
    uid: Optional[str] = ""
    dataImage: Optional[str] = ""
    name: Optional[str] = ""
    description: Optional[str] = ""
    status: Optional[str] = ""
    startDateTime : Optional[datetime]
    endDateTime : Optional[datetime]
    createDateTime : Optional[datetime]
    createdBy : Optional[str] = ""
    totalAmount : Optional[float] = 0
    usedAmount : Optional[float] = 0
    domainId : str
    termAndCondition : Optional[str] = ""
    smsSender: Optional[str] = ""
    smsContent : Optional[str] = ""
    smsUsedCredit : Optional[int] = 1
    redeemType: Optional[str] = "" #*** code_redeem / self_redeem / no_redeem
    displayCustomerInfo: Optional[str] = "" # notDisplay / display

class CampaignOut(BaseModel):
    uid: Optional[str] = ""
    dataImage: Optional[str] = ""
    name: Optional[str] = ""
    code: Optional[str] = ""
    description: Optional[str] = ""
    status: Optional[str] = ""
    startDateTime : Optional[date]
    endDateTime : Optional[date]
    createDateTime : Optional[date]
    createBy : Optional[str] = ""
    totalAmount : Optional[float] = 0
    usedAmount : Optional[float] = 0
    domainId : Optional[str] = ""
    termAndCondition : Optional[str] = ""
    smsSender: Optional[str] = ""
    smsContent : Optional[str] = ""
    smsUsedCredit : Optional[int] = 1
    redeemType: Optional[str] = "" #*** code_redeem / self_redeem / no_redeem
    displayCustomerInfo: Optional[str] = "" # notDisplay / display


class CouponIn(BaseModel):
    # uid: Optional[str] = ""
    # seq: Optional[int] = 0
    # couponCode: Optional[str] = ""
    # externalCode : Optional[str] = ""
    customerName: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    couponStatus : Optional[str] = "ว่างอยู่"
    # startDateTime : Optional[date]
    # endDateTime : Optional[date]
    # accessCount: Optional[int] = 0
    # sentSms: Optional[int] = 0
    # usedDateTime : Optional[datetime]
    # usedBy : Optional[str] = ""
    # usedCode: Optional[str] = ""
    # createDateTime : Optional[date]
    # createBy : Optional[str] = ""
    # updateDateTime : Optional[datetime]
    # updateBy : Optional[str] = ""
    # expireDateTime : Optional[date]
    campaignId : Optional[str] = ""
    # domainId : Optional[str] = ""

class CouponEdit(BaseModel):
    uid: Optional[str] = ""
    # seq: Optional[int] = 0
    # couponCode: Optional[str] = ""
    # externalCode : Optional[str] = ""
    customerName: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    couponStatus : Optional[str] = "ว่างอยู่"
    # startDateTime : Optional[date]
    # endDateTime : Optional[date]
    # accessCount: Optional[int] = 0
    # sentSms: Optional[int] = 0
    # usedDateTime : Optional[datetime]
    # usedBy : Optional[str] = ""
    # usedCode: Optional[str] = ""
    # createDateTime : Optional[date]
    # createdBy : Optional[str] = ""
    # updateDateTime : Optional[datetime]
    # updateBy : Optional[str] = ""
    # expireDateTime : Optional[date]
    campaignId : Optional[str] = ""
    # domainId : Optional[str] = ""




class CouponDb(BaseModel):
    uid: Optional[str] = ""
    seq: Optional[int] = 0
    couponCode: Optional[str] = ""
    externalCode : Optional[str] = ""
    customerName: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    couponStatus : Optional[str] = ""
    startDateTime : Optional[date]
    endDateTime : Optional[date]
    accessCount: Optional[int] = 0
    sentSms: Optional[int] = 0
    usedDateTime : Optional[datetime]
    usedBy : Optional[str] = ""
    usedCode: Optional[str] = ""
    createDateTime : Optional[datetime]
    createBy : Optional[str] = ""
    updateDateTime : Optional[datetime]
    updateBy : Optional[str] = ""
    expireDateTime : Optional[date]
    campaignId : Optional[str] = ""
    domainId : Optional[str] = ""

class CouponUpdateStatus(BaseModel):
    # uid: Optional[str] = ""
    # seq: Optional[int] = 0
    # couponCode: Optional[str] = ""
    # customerName: Optional[str] = ""
    # phone: Optional[str] = ""
    # email: Optional[str] = ""
    couponStatus : Optional[str] = ""
    # startDateTime : Optional[date]
    # endDateTime : Optional[date]
    # accessCount: Optional[int] = 0
    # sentSms: Optional[int] = 0
    usedDateTime : Optional[datetime]
    usedBy : Optional[str] = ""
    usedCode: Optional[str] = ""
    # createDateTime : Optional[date]
    # createBy : Optional[str] = ""
    # updateDateTime : Optional[datetime]
    # updateBy : Optional[str] = ""
    # expireDateTime : Optional[date]
    # campaignId : Optional[str] = ""
    # domainId : Optional[str] = ""

class CouponCancelInput(BaseModel):
    uid: Optional[str] = ""
    # seq: Optional[int] = 0
    couponCode: Optional[str] = ""
    # customerName: Optional[str] = ""
    # phone: Optional[str] = ""
    # email: Optional[str] = ""
    # couponStatus : Optional[str] = ""
    # startDateTime : Optional[date]
    # endDateTime : Optional[date]
    # accessCount: Optional[int] = 0
    # sentSms: Optional[int] = 0
    # usedDateTime : Optional[datetime]
    # usedBy : Optional[str] = ""
    # usedCode: Optional[str] = ""
    # createDateTime : Optional[date]
    # createBy : Optional[str] = ""
    # updateDateTime : Optional[datetime]
    # updateBy : Optional[str] = ""
    # expireDateTime : Optional[date]
    # campaignId : Optional[str] = ""
    # domainId : Optional[str] = ""

class CouponUpdateAccessCount(BaseModel):
    # uid: Optional[str] = ""
    # seq: Optional[int] = 0
    # couponCode: Optional[str] = ""
    # customerName: Optional[str] = ""
    # phone: Optional[str] = ""
    # email: Optional[str] = ""
    # couponStatus : Optional[str] = ""
    # startDateTime : Optional[date]
    # endDateTime : Optional[date]
    accessCount: Optional[int] = 0
    # sentSms: Optional[int] = 0
    # usedDateTime : Optional[datetime]
    # usedBy : Optional[str] = ""
    # usedCode: Optional[str] = ""
    # createDateTime : Optional[date]
    # createdBy : Optional[str] = ""
    # updateDateTime : Optional[datetime]
    # updateBy : Optional[str] = ""
    # expireDateTime : Optional[date]
    # campaignId : Optional[str] = ""
    # domainId : Optional[str] = ""

class CouponUpdateSentSms(BaseModel):
    # uid: Optional[str] = ""
    # seq: Optional[int] = 0
    # couponCode: Optional[str] = ""
    # customerName: Optional[str] = ""
    # phone: Optional[str] = ""
    # email: Optional[str] = ""
    # couponStatus : Optional[str] = ""
    # startDateTime : Optional[date]
    # endDateTime : Optional[date]
    # accessCount: Optional[int] = 0
    sentSms: Optional[int] = 0
    # usedDateTime : Optional[datetime]
    # usedBy : Optional[str] = ""
    # usedCode: Optional[str] = ""
    # createDateTime : Optional[date]
    # createBy : Optional[str] = ""
    # updateDateTime : Optional[datetime]
    # updateBy : Optional[str] = ""
    # expireDateTime : Optional[date]
    # campaignId : Optional[str] = ""
    # domainId : Optional[str] = ""


class CouponOut(BaseModel):
    uid: Optional[str] = ""
    seq: Optional[int] = 0
    couponCode: Optional[str] = ""
    externalCode : Optional[str] = ""
    customerName: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    couponStatus : Optional[str] = ""
    startDateTime : Optional[date]
    endDateTime : Optional[date]
    accessCount: Optional[int] = 0
    sentSms: Optional[int] = 0
    usedDateTime : Optional[datetime]
    usedBy : Optional[str] = ""
    usedCode: Optional[str] = ""
    createDateTime : Optional[datetime]
    createBy : Optional[str] = ""
    updateDateTime : Optional[datetime]
    updateBy : Optional[str] = ""
    expireDateTime : Optional[date]
    campaignId : Optional[str] = ""
    domainId : Optional[str] = ""

class SearchForm(BaseModel):
    uid: Optional[str] = "" 
    page : Optional[int] = 1
    pageSize : Optional[int] = 10
    searchText: Optional[str] = "" 
    status: Optional[str] = ""

class QtyForm(BaseModel):
    qty: Optional[int] = 0

class CouponRedeem(BaseModel):
    couponCode: Optional[str] = ""
    redeemCode: Optional[str] = ""

class CouponUse(BaseModel):
    brandId: Optional[str] = ""
    verificationCode: Optional[str] = ""
    couponCode: Optional[str] = ""
   
#******************************************
#*** [1.1] Brand ADD [only admin]
#******************************************

@router.post("/brand-register",  tags=["ecoupon"] )
async def brand_register(brandIn: BrandIn,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
   
  

    brand = dict()
    brand["uid"] = util.getUuid()
    brand["name"] = brandIn.name
    brand["description"] = brandIn.description
    brand["createDateTime"] = datetime.now()
    brand["status"] = "active"
    brand["credit"] = brandIn.credit
    brand["packageSize"] = brandIn.packageSize
    brand["verificationCode"] = util.genRandomDigit(10)

    user = dict()
    # user["uid"] = util.getUuid()
    user["username"] = brandIn.username
    user["password"] = brandIn.password
    user["createDateTime"] = datetime.now()
    user["domainId"] = brand["uid"]


    userdb = await userRepo.getUserByEmail(db, brandIn.username)

    if userdb:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    

    # logger.info(">>>>>>>>>>>> userReg  DB >>>>>>>>>>>>>>>>>>>>>")
    try: 
        newuser = await userRepo.eCouponCreateUser(db=db, create=user)
        # row1 = await db["ecouponv1"]["user"].insert_one(user)
        row2 = await db["ecouponv1"]["brand"].insert_one(brand)
    except:
        raise HTTPException(status_code=400, detail="Unable to save data to database")

    # return userdb


#******************************************
#*** [1.2.1] Brand UPDATE [Only admin]
#******************************************

@router.post("/update-brand/{id}",  tags=["ecoupon"] )
async def update_brand(id: str , brandEdit: BrandEdit,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
# async def update_brand(id: str , brandEdit: BrandEdit,  db: AsyncIOMotorClient =  Depends(get_database)):
   
    updated = brandEdit.dict()

    try: 
        edit = await db["ecouponv1"]["brand"].update_one({"uid": id}, {'$set': updated })
    except:
        raise HTTPException(status_code=400, detail="Unable to save data to database")

    # return userdb


#******************************************
#*** [1.2.2] Brand UPDATE [Only shop]
#******************************************

@router.post("/shop/update-brand",  tags=["ecoupon"] )
async def update_brand( redeem: BrandUpdateRedeemCode,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
# async def update_brand(id: str , brandEdit: BrandEdit,  db: AsyncIOMotorClient =  Depends(get_database)):
   
    updated = redeem.dict()
    domainId = currentUser.domainId

    brand =  await db["ecouponv1"]["brand"].find_one( { "uid" : domainId } ) 

    if not brand:
        raise HTTPException(status_code=400, detail="Bad request: Not found brand")

    # print(updated)


    try: 
        edit = await db["ecouponv1"]["brand"].update_one({"uid": domainId}, {'$set': updated })
    except:
        raise HTTPException(status_code=400, detail="Unable to save data to database")





#******************************************
#*** [2.2.1] Campaign UPDATE [only admin]
#******************************************
@router.post("/update-campaign/{id}",  tags=["ecoupon"] )
async def update_campaign(id: str , campaignEdit: CampaignEdit,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
   
    updated = campaignEdit.dict()
    
    if campaignEdit.dataImage : 
        imgResult = await fileRepo.base64Image(file = campaignEdit.dataImage) 
        if imgResult["success"] == True :
            updated["dataImage"] = imgResult["result"]["fileName"]


    try:
        # await db["ecouponv1"]["campaign"].update_one({"domainId": domainId}, {'smsCredit' : updated })
        edit = await db["ecouponv1"]["campaign"].update_one({"uid": id}, {'$set': updated })
    except:
        raise HTTPException(status_code=400, detail="Unable to save data to database")

    # return userdb


#******************************************
#*** [2.2.2] ไม่ต้องมี Campaign UPDATE [only shop]
#******************************************
# @router.post("/shop/update-campaign",  tags=["ecoupon"] )
# async def update_campaign(id: str , campaignEdit: CampaignEdit,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
   
#     updated = campaignEdit.dict()

    
#     if campaignEdit.dataImage : 
#         imgResult = await fileRepo.base64Image(file = campaignEdit.dataImage) 
#         if imgResult["success"] == True :
#             updated["dataImage"] = imgResult["result"]["fileName"]

#     try: 
#         edit = await db["ecouponv1"]["campaign"].update_one({"uid": id}, {'$set': updated })
#     except:
#         raise HTTPException(status_code=400, detail="Unable to save data to database")

#     # return userdb


#******************************************
#*** [2.3] Campaign TERMS AND CONDITION [only shop]
#******************************************
@router.post("/update-campaign-term/{id}",  tags=["ecoupon"] )
async def update_campaign(id: str , campaign: CampaignUpdateTerm,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
   
    
    row =  await db["ecouponv1"]["campaign"].find_one( {"$and" :  [{ "uid" : id }, {"domainId" : currentUser.domainId} ] } ) 
    
    if not row:
        raise HTTPException(status_code=400, detail="Bad request: Not found campaign")
    
    updated = campaign.dict()

    # print(row["uid"])
    # print(updated)

    try: 
        edit = await db["ecouponv1"]["campaign"].update_one({"uid": id}, {'$set': updated })
    except:
        raise HTTPException(status_code=400, detail="Unable to save data to database")

    # return userdb





#******************************************
#*** [3.6] Coupon use [admin , shop]
#******************************************
@router.post("/coupon-used",  tags=["ecoupon"] )
async def update_campaign( use : CouponUse ,  db: AsyncIOMotorClient =  Depends(get_database) ):

    brand =  await db["ecouponv1"]["brand"].find_one( {"$and" :  [ { "uid" : use.brandId }, { "verificationCode" : use.verificationCode }  ] } )

    if not brand:
        raise HTTPException(
                        status_code=400, detail="Bad request: Not found Brand"
                    )

    

    row =  await db["ecouponv1"]["coupon"].find_one( {"$and" :  [{ "couponCode" : use.couponCode },{ "domainId" : brand["uid"]  } ] } ) 
        
   

    if not row:
        raise HTTPException(
                        status_code=400, detail="Bad request: Not found code"
                    )
        
    #*** ดักว่า ถ้า QR ถูกใช้แล้วจะใช้งานอีก ไม่ได้
    # if row:
    #     raise HTTPException(
    #                     status_code=400, detail="Bad request: Not found code"
    #                 )


    if(row["couponStatus"] != "ว่างอยู่" and row["couponStatus"] != "ส่งออก"):
        raise HTTPException(
                        status_code=400, detail="Bad request: this coupon is no longer available"
                    )
    



    coupon = CouponUpdateStatus(**row)

    # print(coupon)
    
    coupon.couponStatus = "ใช้แล้ว"
    timenow = datetime.now()
    coupon.usedDateTime = timenow.strftime("%Y-%m-%d %H:%M:%S.%f")
   
    updated = coupon.dict()
    updated["usedCode"] = "ByQRCode"

    # print(updated)
    

    try: 
        edit = await db["ecouponv1"]["coupon"].update_one({"couponCode": row["couponCode"]}, {'$set': updated })
    except:
        raise HTTPException(status_code=400, detail="Unable to save data to database")

    # return userdb
    
    
    
    
#******************************************
#*** [3.6.2] Staff Claim Coupon [admin , shop]
#******************************************
@router.post("/staff-claim",  tags=["ecoupon"] )
async def update_campaign( use : CouponUse ,  db: AsyncIOMotorClient =  Depends(get_database) , currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):

    campaign =  await db["ecouponv1"]["campaign"].find_one({ "uid" : use.brandId })
    

    if not campaign:
        raise HTTPException(
                        status_code=400, detail="Bad request: Not found campaign"
                    )
        
    brandId = campaign["domainId"]
        
    # staffName = use.verificationCode
    

    row =  await db["ecouponv1"]["coupon"].find_one( { "uid" : use.couponCode }) 
        
   

    if not row:
        raise HTTPException(
                        status_code=400, detail="Bad request: Not found code"
                    )
        
    #*** ดักว่า ถ้า QR ถูกใช้แล้วจะใช้งานอีก ไม่ได้
    # if row:
    #     raise HTTPException(
    #                     status_code=400, detail="Bad request: Not found code"
    #                 )


    if(row["couponStatus"] != "ว่างอยู่" and row["couponStatus"] != "ส่งออก"):
        raise HTTPException(
                        status_code=400, detail="Bad request: this coupon is no longer available"
                    )
    



    coupon = CouponUpdateStatus(**row)

    # print(coupon)
    
    coupon.couponStatus = "ใช้แล้ว"
    timenow = datetime.now()
    coupon.usedDateTime = timenow.strftime("%Y-%m-%d %H:%M:%S.%f")
   
    updated = coupon.dict()
    updated["usedCode"] = "StaffClaim"
    updated["claimedBy"] = currentUser.username
    # print(updated)
    

    try: 
        edit = await db["ecouponv1"]["coupon"].update_one({"couponCode": row["couponCode"]}, {'$set': updated })
    except:
        raise HTTPException(status_code=400, detail="Unable to save data to database")

    # return userdb


#******************************************
#*** [3.7] Coupon ACCESS COUNT [anonymous]
#******************************************
@router.post("/update-coupon-access-count/{code}",  tags=["ecoupon"] )
# async def update_coupon_access_count(code: str , edit: CouponUpdateAccessCount,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
async def update_coupon_access_count(code: str , edit: CouponUpdateAccessCount,  db: AsyncIOMotorClient =  Depends(get_database)):
   
    coupon =  await db["ecouponv1"]["coupon"].find_one( { "couponCode" : code } ) 

    
   
    if not coupon:
        raise HTTPException(
                        status_code=400, detail="Bad request: Not found code"
                    )

    #*** ดักว่า ถ้า QR ถูกใช้แล้วจะใช้งานอีก ไม่ได้

    # if coupon.couponStatus == 'ใช้แล้ว':
    #     return {"success" : False, "detail" : "ถูกใช้งานแล้ว"}


    couponDb = CouponDb(**coupon)

    # print(couponDb)

    

    campaign =  await db["ecouponv1"]["campaign"].find_one( { "uid" : couponDb.campaignId } ) 
    campaignOut = CampaignOut(**campaign)
    campaignOutDict = campaignOut.dict()
    
  
    couponDb.accessCount = couponDb.accessCount + 1
    
    # สำหรับ save to database 
    couponDb2 = copy.deepcopy(couponDb)
  

    couponOut = CouponOut(**couponDb.dict())

    access = CouponUpdateAccessCount(**couponDb2.dict())
    

    couponDisplay = {"success" : True ,   "campaign" : campaignOutDict , "coupon" : couponOut.dict()}

    try: 
        edit = await db["ecouponv1"]["coupon"].update_one({"couponCode" : code}, {'$set': access.dict()})
    except:
        raise HTTPException(status_code=400, detail="Unable to save data to database")

    return couponDisplay



#******************************************
#*** [3.8] Coupon redeem [customer]
#******************************************
@router.post("/coupon-redeem",  tags=["ecoupon"] )
async def redeem_campaign(redeem: CouponRedeem ,   db: AsyncIOMotorClient =  Depends(get_database)):

    couponCode = redeem.couponCode
    redeemCode = redeem.redeemCode

    # print(f"couponCode >>> {couponCode}")
    # print(f"redeemCode >>> {redeemCode}")

    row =  await db["ecouponv1"]["coupon"].find_one( { "couponCode" : couponCode } ) 
    
    if not row:
        raise HTTPException(
                        status_code=400, detail="Bad request: Not found Coupon"
                    )


    coupon = CouponUpdateStatus(**row)


    #*** ตรวจสอบ redeemCode 

    if(row["couponStatus"] != "ว่างอยู่" and row["couponStatus"] != "ส่งออก"):
        raise HTTPException(
                        status_code=400, detail="Bad request: this coupon is no longer available"
                    )
    

    brandId = row["domainId"]
    
    brand =  await db["ecouponv1"]["brand"].find_one( { "uid" : brandId } )
    
    if not brand:
        raise HTTPException(
                        status_code=400, detail="Bad request: Not found Shop"
                    )
    
    redeemCodeList = brand["redeemCode"]

    # print(f"redeemCodeList >>> {redeemCodeList}")
    # print(f"redeemCode >>> {redeemCode}")

    if isinstance(redeemCodeList, list) == False :
        raise HTTPException(status_code=400, detail="Not found redeem code")

    if redeemCode not in redeemCodeList:
        raise HTTPException(status_code=400, detail="Bad request: Redeem code is not correct")

    #*** ตรวจสอบ redeemCode 
    

    

    
    coupon.couponStatus = "ใช้แล้ว"
    timenow = datetime.now()
    coupon.usedDateTime = timenow.strftime("%Y-%m-%d %H:%M:%S.%f")
    coupon.usedCode = redeemCode
   
    updated = coupon.dict()
    updated["usedCode"] = redeemCode

    

    try: 
        edit = await db["ecouponv1"]["coupon"].update_one({"couponCode": couponCode}, {'$set': updated })
    except:
        raise HTTPException(status_code=400, detail="Unable to save data to database")

    return coupon


#******************************************
#*** [3.8.2] self-redeem [customer]
#******************************************
@router.put("/self-redeem",  tags=["ecoupon"] )
async def update_campaign(redeem: CouponRedeem ,   db: AsyncIOMotorClient =  Depends(get_database)):

    couponCode = redeem.couponCode
    # redeemCode = redeem.redeemCode

    # print(f"couponCode >>> {couponCode}")
    # print(f"redeemCode >>> {redeemCode}")

    row =  await db["ecouponv1"]["coupon"].find_one( { "couponCode" : couponCode } ) 
    
    if not row:
        raise HTTPException(
                        status_code=400, detail="Bad request: Not found Coupon"
                    )


    coupon = CouponUpdateStatus(**row)


    #*** ตรวจสอบ redeemCode 

    if(row["couponStatus"] != "ว่างอยู่" and row["couponStatus"] != "ส่งออก"):
        raise HTTPException(
                        status_code=400, detail="Bad request: this coupon is no longer available"
                    )
    

    
    coupon.couponStatus = "ใช้แล้ว"
    timenow = datetime.now()
    coupon.usedDateTime = timenow.strftime("%Y-%m-%d %H:%M:%S.%f")
   
    updated = coupon.dict()
    updated["usedCode"] = "self_redeem"

    

    try: 
        edit = await db["ecouponv1"]["coupon"].update_one({"couponCode": couponCode}, {'$set': updated })
    except:
        raise HTTPException(status_code=400, detail="Unable to save data to database")

    return coupon



#******************************************
#*** [3.9] Add Coupon Credit [Only admin]
#******************************************
@router.post("/add-coupon-credit/{brandId}",  tags=["ecoupon"] )
async def add_coupon_credit(brandId: str , form: QtyForm ,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_admin_user)):

    
    # if form.qty <= 0:
    #     raise HTTPException(status_code=400, detail="Bad request: Qty must be greater than 0")

    
    row =  await db["ecouponv1"]["brand"].find_one( { "uid" : brandId } ) 

    if not row:
        raise HTTPException(
                        status_code=400, detail="Bad request: Not found Shop"
                    )
    
    brand_db = BrandDb(**row)
    brand_db.credit = brand_db.credit + form.qty
    # print(row)
    
    updated = BrandUpdateCouponCredit(**brand_db.dict())
    # print(updated)

    timenow = datetime.now()

    # if not row["credit"]:
    #     row["credit"] = 0

    credit = dict()
    credit["uid"] = str(uuid.uuid4())
    credit["couponCredit"] = form.qty
    credit["priorCouponCredit"] = brand_db.credit
    credit["domainId"] =  brandId
    credit["brandName"] =  row["name"]
    credit["createDateTime"] = timenow.strftime("%Y-%m-%d %H:%M:%S.%f")
    credit["createBy"] =  currentUser.username

    

    try: 
        edit = await db["ecouponv1"]["brand"].update_one({ "uid" : brandId }, {'$set': updated.dict() })
        await db["ecouponv1"]["couponCreditLog"].insert_one(credit)
    except:
        raise HTTPException(status_code=400, detail="Unable to save data to database")


#******************************************
#*** [3.10] Add SMS Credit [Only admin]
#******************************************
@router.post("/add-sms-credit/{brandId}",  tags=["ecoupon"] )
async def add_sms_credit(brandId: str , form: QtyForm ,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_admin_user)):

    
    # if form.qty <= 0:
    #     raise HTTPException(status_code=400, detail="Bad request: Qty must be greater than 0")

    
    row =  await db["ecouponv1"]["brand"].find_one( { "uid" : brandId } ) 

    if not row:
        raise HTTPException(
                        status_code=400, detail="Bad request: Not found Shop"
                    )
    
    brand_db = BrandDb(**row)

    brand_db.smsCredit = brand_db.smsCredit + form.qty

    updated = BrandUpdateSmsCredit(**brand_db.dict())
    # print(updated)

    timenow = datetime.now()

    # if not row["smsCredit"]:
    #     row["smsCredit"] = 0

    credit = dict()
    credit["uid"] = str(uuid.uuid4())
    credit["smsCredit"] = form.qty
    credit["priorSmsCredit"] = brand_db.smsCredit
    credit["domainId"] =  brandId
    credit["brandName"] =  row["name"]
    credit["createDateTime"] = timenow.strftime("%Y-%m-%d %H:%M:%S.%f")
    credit["createBy"] =  currentUser.username


    try: 
        edit = await db["ecouponv1"]["brand"].update_one({ "uid" : brandId }, {'$set': updated.dict() })
        await db["ecouponv1"]["smsCreditLog"].insert_one(credit)
    except:
        raise HTTPException(status_code=400, detail="Unable to save data to database")

   
#******************************************
#*** [3.11] cancel coupon [admin / shop]
#******************************************

@router.post("/cancel-coupon",  tags=["ecoupon"] )
async def cancel_coupon( cancelList : List[CouponCancelInput] ,db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
    if not cancelList:
        raise HTTPException(status_code=400, detail="coupon list must contain at least one item")
    #*** (1) list of ids of coupons that will send SMS
    cancelListIds = [ xx.uid for xx in cancelList  ]

    #*** (2) find coupon in IDs list 
    coupons =   db["ecouponv1"]["coupon"].find( { "uid" :  {"$in" : cancelListIds}} ) 

    newCancelListIds = [ yy["uid"] async for yy in coupons if yy["couponStatus"] == "ว่างอยู่" or yy["couponStatus"] == "ส่งออก" ]

    if not coupons:
        raise HTTPException( status_code=400, detail="Bad request: Coupon ID Not Found")
    
    #*** (3) update 
    timenow = datetime.now()
    datetimenow = timenow.strftime("%Y-%m-%d %H:%M:%S.%f")

    try: 
        edit = await db["ecouponv1"]["coupon"].update_many({"uid" : { "$in" : newCancelListIds}}, { '$set': {"couponStatus" : "ยกเลิก", "updateDateTime": datetimenow, "updateBy": currentUser.username  } })
    except:
        raise HTTPException(status_code=400, detail="Unable to save data to database")

    

#******************************************
#*** [1.3] Brand List [only admin]
#******************************************

@router.post("/brand-list",  tags=["ecoupon"] )
async def brand_list(SearchForm: SearchForm,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_admin_user)):
   
    nameStr = f"{SearchForm.searchText}"
    rows =    db["ecouponv1"]["brand"].find( { "$and" : [ { "$or" : [{ "name" :  {'$regex':nameStr , '$options' : 'i'} } ,  { "description" :  {'$regex':nameStr , '$options' : 'i'} }] } , 
                                                          { "status" :  {'$regex':SearchForm.status  , '$options' : 'i'}  } 
                                                        ] 
                                             } ) 

    if not rows:
         raise HTTPException(
                    status_code=400, detail="Bad request: Not found"
                )

    res = [BrandOut(**row) async for row in rows  ]

    brandIds = [brandOne.uid for brandOne in res  ]

    # print(brandIds)


    campaingAll = db["ecouponv1"]["campaign"].find({ "domainId" : {"$in": brandIds } }).sort("createDateTime", -1)
    campaignList = [camp async for camp in campaingAll  ]

    userAll =  db["ecouponv1"]["user"].find({ "domainId" : {"$in": brandIds } }).sort("createDateTime", -1)
    userList = [user async for user in userAll  ]
    


    for r in res:
        campCount = [acmp for acmp in campaignList if acmp["domainId"] == r.uid]
        userTmp = filter(lambda x: x["domainId"] == r.uid , userList)
        userTmpList = list(userTmp)
        userOne = userTmpList[0]
        r.campaignCount = len(campCount)

        r.ownerEmail = userOne["username"]
        
    # res = [row async for row in rows  ]
    # res = []
    # async for row in rows:
    #     del row['_id'] 
    #     res.append(row)

    # print(res)
    return res


#******************************************
#*** [2.1.1] campaign List [only admin]
#******************************************

@router.post("/campaign-list/{brandId}",  tags=["ecoupon"] )
async def campaign_list(brandId: str,searchForm: SearchForm,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_admin_user)):
   
    # print("SEARCH FORM ")
    # print(searchForm)
    # nameStr = f"{SearchForm.searchText}"

    # print(">>>>>>>>>>>>>>>>>>>> brandId >>>>>>>>>>>>>>>>>>")
    # print(brandId)
    # print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    rows =    db["ecouponv1"]["campaign"].find( { "$and" : [ { "$or" : [{ "name" :  {'$regex':searchForm.searchText , '$options' : 'i'} } ,  { "description" :  {'$regex':searchForm.searchText , '$options' : 'i'} }] } , 
                                                        #   { "status" :  {'$regex':searchForm.status  , '$options' : 'i'}  } 
                                                        { "domainId" : brandId } 
                                                        ] 
                                             } ).sort("createDateTime", -1)

    if not rows:
         raise HTTPException(
                    status_code=400, detail="Bad request: Not found"
                )

    # rows =    db["ecouponv1"]["campaign"].find() 
    res = [CampaignOut(**row) async for row in rows  ]

   


    # print(rows)

    # res = []
    # async for row in rows:
    #     del row['_id'] 
    #     res.append(row)

    # print("LOAD campaign_list")
    # print(res)
  
    return res

#******************************************
#*** [2.1.2] campaign list [only shop]
#******************************************

@router.post("/shop/campaign-list",  tags=["ecoupon-shop"] )
async def campaign_list(searchForm: SearchForm,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_shop_user)):
   


    rows =    db["ecouponv1"]["campaign"].find( { "$and" : [ { "$or" : [{ "name" :  {'$regex':searchForm.searchText , '$options' : 'i'} } ,  { "description" :  {'$regex':searchForm.searchText , '$options' : 'i'} }] } , 
                                                        #   { "status" :  {'$regex':searchForm.status  , '$options' : 'i'}  } 
                                                        { "domainId" : currentUser.domainId } 
                                                        ] 
                                             } ).sort("createDateTime", -1)
    res = [CampaignOut(**row) async for row in rows  ]

 
    # print(res)
  
    return res

#******************************************
#*** [3.1.1] coupon list [only admin]
#******************************************
@router.post("/coupon-list/{campaignId}",  tags=["ecoupon"] )
async def coupon_list(campaignId: str, searchForm: SearchForm,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_admin_user)):
   

    #**** BEGIN : Page Operation

    # itemCount =     await db["ecouponv1"]["coupon"].count_documents({})
    # print(f"itemCount >>>. {itemCount}")

    if not searchForm.page :
        searchForm.page = 1
    
    if not searchForm.pageSize :
        searchForm.pageSize = 1

    itemCount = 0
    itemCount =  await db["ecouponv1"]["coupon"].count_documents( { "$and" : [ { "$or" : [{ "customerName" :  {'$regex':searchForm.searchText , '$options' : 'i'} } ,  { "couponCode" :  {'$regex':searchForm.searchText , '$options' : 'i'} } ,  { "phone" :  {'$regex':searchForm.searchText , '$options' : 'i'} }] } , 
                                                          { "couponStatus" :  {'$regex':searchForm.status  , '$options' : 'i'}  } ,
                                                          { "campaignId" : campaignId } 
                                                        ] 
                                             } )

    

    pageData = utilRepo.pageCalculation(searchForm.page , searchForm.pageSize , itemCount )

    # print(pageData)

    #**** END : Page Operation

    ### @@@ [transition]
    # rows =    db["ecouponv1"]["coupon"].find( { "$and" : [ { "$or" : [{ "customerName" :  {'$regex':searchForm.searchText , '$options' : 'i'} } ,  { "couponCode" :  {'$regex':searchForm.searchText , '$options' : 'i'} },  { "phone" :  {'$regex':searchForm.searchText , '$options' : 'i'} }] } , 
    #                                                       { "couponStatus" :  {'$regex':searchForm.status  , '$options' : 'i'}  } ,
    #                                                       { "campaignId" : campaignId } 
    #                                                     ] 
    #                                          } ).sort("createDateTime",-1).skip(pageData["skip"]).limit(pageData["limit"])
    
    rows =    db["ecouponv1"]["coupon"].find( { "$and" : [ { "$or" : [{ "customerName" :  {'$regex':searchForm.searchText , '$options' : 'i'} } ,  { "couponCode" :  {'$regex':searchForm.searchText , '$options' : 'i'} },  { "phone" :  {'$regex':searchForm.searchText , '$options' : 'i'} }] } , 
                                                          { "couponStatus" :  {'$regex':searchForm.status  , '$options' : 'i'}  } ,
                                                          { "campaignId" : campaignId } 
                                                        ] 
                                             } ).sort("seq",-1).skip(pageData["skip"]).limit(pageData["limit"])

    

    if not rows:
         raise HTTPException(
                    status_code=400, detail="Bad request: Not found"
                )

    itemList = [CouponOut(**row) async for row in rows  ]
    
    
    # print(itemList[0].dict())


    statRows =  db["ecouponv1"]["coupon"].find({ "campaignId" : campaignId })
    itemStat = [CouponOut(**statRow) async for statRow in statRows  ]

    stat = {
            "available" :  0,
            "posted" :  0,
            "used" :  0,
            "canceled" :  0
        }
    

    for st in itemStat:
        if st.couponStatus == "ว่างอยู่":
            stat["available"] = stat["available"] + 1
        elif st.couponStatus == "ส่งออก":
            stat["posted"] = stat["posted"] + 1
        elif st.couponStatus == "ใช้แล้ว":
            stat["used"] = stat["used"] + 1
        elif st.couponStatus == "ยกเลิก":
            stat["canceled"] = stat["canceled"] + 1
  
    return {
       "pageData" : pageData,
       "itemList" : itemList,
       "stat" :  stat
    }
    
    
    
#******************************************
#*** [xxx.add.1] coupon-add-seq [only admin]
#******************************************
@router.post("/coupon-add-seq",  tags=["ecoupon"] )
async def coupon_list(campaignId: str, searchForm: SearchForm,  db: AsyncIOMotorClient =  Depends(get_database)):
   

    #**** BEGIN : Page Operation

    # itemCount =     await db["ecouponv1"]["coupon"].count_documents({})
    # print(f"itemCount >>>. {itemCount}")

    if not searchForm.page :
        searchForm.page = 1
    
    if not searchForm.pageSize :
        searchForm.pageSize = 1

    itemCount = 0
    itemCount =  await db["ecouponv1"]["coupon"].count_documents( { "$and" : [ { "$or" : [{ "customerName" :  {'$regex':searchForm.searchText , '$options' : 'i'} } ,  { "couponCode" :  {'$regex':searchForm.searchText , '$options' : 'i'} } ,  { "phone" :  {'$regex':searchForm.searchText , '$options' : 'i'} }] } , 
                                                          { "couponStatus" :  {'$regex':searchForm.status  , '$options' : 'i'}  } ,
                                                          { "campaignId" : campaignId } 
                                                        ] 
                                             } )

    

    pageData = utilRepo.pageCalculation(searchForm.page , searchForm.pageSize , itemCount )

    # print(f"Item count >>> {itemCount}")

    #**** END : Page Operation

    rows =    db["ecouponv1"]["coupon"].find( { "$and" : [ { "$or" : [{ "customerName" :  {'$regex':searchForm.searchText , '$options' : 'i'} } ,  { "couponCode" :  {'$regex':searchForm.searchText , '$options' : 'i'} },  { "phone" :  {'$regex':searchForm.searchText , '$options' : 'i'} }] } , 
                                                          { "couponStatus" :  {'$regex':searchForm.status  , '$options' : 'i'}  } ,
                                                          { "campaignId" : campaignId } 
                                                        ] 
                                             } ).sort("createDateTime",1)
    
   

    

    if not rows:
         raise HTTPException(
                    status_code=400, detail="Bad request: Not found"
                )

    itemList = [CouponDb(**row).dict() async for row in rows  ]
    
    
    
    
    
    current_uid = ""
    ind = 0
    # try:
    for iitm in itemList : 
        # if ind > 1: break
        current_uid = iitm["uid"]
        
        
        iitm["startDateTime"] = iitm["startDateTime"].strftime("%Y-%m-%d")
        iitm["endDateTime"] = iitm["endDateTime"].strftime("%Y-%m-%d")
        iitm["expireDateTime"] = iitm["expireDateTime"].strftime("%Y-%m-%d")
        iitm["createDateTime"] = iitm["createDateTime"].strftime("%Y-%m-%d %H:%M:%S.%f")
        
        iitm["seq"] = ind + 1
        
        # print(current_uid)
        await db["ecouponv1"]["coupon"].update_one({"uid" : current_uid}, {'$set': iitm} )
        ind = ind + 1
    # except:
    #     print(f"update went wrong at uid >>> {current_uid}")

  
    return {
       
       "itemList" : itemList,
    }

#******************************************
#*** [3.1.2] coupon list [only shop]
#******************************************
@router.post("/shop/coupon-list/{campaignId}",  tags=["ecoupon-shop"] )
async def shop_coupon_list(campaignId: str,  searchForm: SearchForm,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
   
    #**** BEGIN : Page Operation

    # itemCount =     await db["ecouponv1"]["coupon"].count_documents({})
    # print(f"itemCount >>>. {itemCount}")

    if not searchForm.page :
        searchForm.page = 1
    
    if not searchForm.pageSize :
        searchForm.pageSize = 1

    itemCount = 0
    itemCount =  await db["ecouponv1"]["coupon"].count_documents( {  "$and" : [ { "$or" : [{ "customerName" :  {'$regex':searchForm.searchText , '$options' : 'i'} } ,  { "couponCode" :  {'$regex':searchForm.searchText , '$options' : 'i'} } ,  { "phone" :  {'$regex':searchForm.searchText , '$options' : 'i'} }  ] } , 
                                                                { "couponStatus" :  {'$regex':searchForm.status  , '$options' : 'i'}  } ,
                                                                { "campaignId" : campaignId } ,
                                                                {"domainId" : currentUser.domainId }
                                                        ] 
                                                    } )
                                             
    pageData = utilRepo.pageCalculation(searchForm.page , searchForm.pageSize , itemCount )

    # print(pageData)

    #**** END : Page Operation

    rows =    db["ecouponv1"]["coupon"].find( { "$and" : [ { "$or" : [{ "customerName" :  {'$regex':searchForm.searchText , '$options' : 'i'} } ,  { "couponCode" :  {'$regex':searchForm.searchText , '$options' : 'i'} }  ,  { "phone" :  {'$regex':searchForm.searchText , '$options' : 'i'} } ] } , 
                                                          { "couponStatus" :  {'$regex':searchForm.status  , '$options' : 'i'}  } ,
                                                          { "campaignId" : campaignId } ,
                                                          {"domainId" : currentUser.domainId }
                                                        ] 
                                             } ).sort("seq",-1).skip(pageData["skip"]).limit(pageData["limit"])


    if not rows:
         raise HTTPException(
                    status_code=400, detail="Bad request: Not found"
                )

    # rows =    db["ecouponv1"]["coupon"].find() 
    itemList = [CouponOut(**row) async for row in rows  ]

    

    statRows =   db["ecouponv1"]["coupon"].find( {  "$and" : [ 
                                                                { "campaignId" : campaignId } ,
                                                                {"domainId" : currentUser.domainId }
                                                        ] 
                                                    } )

    itemStat = [CouponOut(**statRow) async for statRow in statRows  ]

    stat = {
            "available" :  0,
            "posted" :  0,
            "used" :  0,
            "canceled" :  0
        }
    

    for st in itemStat:
        if st.couponStatus == "ว่างอยู่":
            stat["available"] = stat["available"] + 1
        elif st.couponStatus == "ส่งออก":
            stat["posted"] = stat["posted"] + 1
        elif st.couponStatus == "ใช้แล้ว":
            stat["used"] = stat["used"] + 1
        elif st.couponStatus == "ยกเลิก":
            stat["canceled"] = stat["canceled"] + 1


    return {
       "pageData" : pageData,
       "itemList" : itemList,
       "stat" :  stat 
    }

    
#******************************************
#*** [3.2] gen coupon [admin / shop]
#******************************************

@router.post("/gen-coupon/{campaignId}",  tags=["ecoupon"] )
async def gen_coupon(campaignId: str, qtyform : QtyForm ,db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
    
    if not campaignId:
        raise HTTPException(status_code=400, detail="Request parameter not valid")

    #*** (1)  find Campaign usin campaignId

    camp =  await db["ecouponv1"]["campaign"].find_one( { "uid" : campaignId } ) 


    if not camp:
        raise HTTPException(
                        status_code=400, detail="Bad request: Campaign ID Not Found"
                    )


    
    
    
    if not qtyform.qty:
        raise HTTPException(
                        status_code=400, detail="Bad request: Not found qty"
                    )

    domainId = ""


    if currentUser.admin == True:
        domainId = camp["domainId"]
    else:
        domainId = currentUser.domainId


    #*** Check coupon credit 

    brand =  await db["ecouponv1"]["brand"].find_one( { "uid" : domainId } ) 
    
    
    ### @@@ load coupon
    
    rows =    db["ecouponv1"]["coupon"].find( { "$and" : [  { "campaignId" : campaignId } ,
                                                            {"domainId" : domainId }
                                                            ] 
                                                } )
    if not rows:
         raise HTTPException(
                    status_code=400, detail="Bad request: Not found"
                )
         
    itemList = [row async for row in rows  ]
    
    maxSeq = -1
    for itm in itemList:
        if "seq" not in itm : 
            itm["seq"] = 0
            
        # print (f">>>>>>>>>>>>>> type [seq] >>>>>>>>>> { type(itm['seq']) } maxSeq >>>>>>>>>>>>>>>{ type(maxSeq)}")
        if int(itm["seq"]) >= int(maxSeq) : 
            maxSeq = itm["seq"]
            
    
    
    if maxSeq is None : 
        maxSeq = 0
       
    
    numberList = len(itemList)
    
    the_maximum = 0
    
    if int(numberList) > int(maxSeq):
        the_maximum =  numberList
    else : 
        the_maximum = maxSeq
   
   
   ### @@@ load coupon

    if not brand:
        raise HTTPException(
                        status_code=400, detail="Bad request: Brand Not Found"
                    )
    #*** function นี้สร้างคูปอง ONLY
    brandCouponCredit =  brand["credit"]
    # brandSmsCredit =  brand["smsCredit"]
    print(f"Brand coupno credit >>>> {brandCouponCredit}")
     #*** Check Credit  

    qty = qtyform.qty

    couponPrefix = camp["code"]
    campaignId = camp["uid"]
    startDateTime =  camp["startDateTime"]
    endDateTime =  camp["endDateTime"]
    domainId = camp["domainId"]

    timenow = datetime.now()

    couponList = []
    insufficient = qty
    for i in range(qty):
        
        if brandCouponCredit > 0:
            exres = dict()
            exres["uid"] = str(uuid.uuid4())
            exres["phone"] = ""
            exres["email"] = ""
            exres["customerName"] = ""
            exres["couponCode"] = f"{couponPrefix}{util.genUpperAlphaNumbericText(10)}"
            exres["couponStatus"] = f"ว่างอยู่"
            exres["startDateTime"] = parse(startDateTime).strftime("%Y-%m-%d")
            exres["endDateTime"] = parse(endDateTime).strftime("%Y-%m-%d")
            exres["expireDateTime"] = parse(endDateTime).strftime("%Y-%m-%d")
            recordNow =  datetime.now()
            exres["createDateTime"] = recordNow.strftime("%Y-%m-%d %H:%M:%S.%f")
            exres["createBy"] =  currentUser.username
            exres["campaignId"] =  campaignId
            exres["domainId"] =  domainId
            exres["sentSms"] = 0
            the_maximum = the_maximum + 1
            exres["seq"] = the_maximum

            brandCouponCredit = brandCouponCredit - 1
            insufficient = insufficient - 1

            # print(f"i ====>>>> {i}")

            couponList.append(exres)
        else:
            break


    # ind = ind + 1

    updated = dict()
    updated["credit"] = brandCouponCredit

    res = dict()

    
    

    try:
        # #*** (3) update brand
        edit = db["ecouponv1"]["brand"].update_one({"uid" : domainId}, {'$set': updated} )
        await db["ecouponv1"]["coupon"].insert_many(couponList) 

    except:
        res["success"] = False
        res["detail"] = "Unable to save data to database"
        res["insufficient"] = insufficient
        res = {
                "success" : False,
                "detail" : "Unable to save data to database",
                "insufficient" : insufficient
            }
        raise HTTPException(status_code=400, detail=res)

    # res = {
    #     "success" : True,
    #     "insufficient" : insufficient
    # }

    res["success"] = True
    # res["totalItem"] = len(coupon_ids_changes)
    res["totalCoupon"] = len(couponList)
    # res["totalSms"] = len(coupon_ids_changes)
    # res["result"] = couponSentList

    return res

#******************************************
#*** [2.2.1] add-campaign [only admin]
#******************************************
@router.post("/add-campaign/{brandId}",  tags=["ecoupon"] )
async def add_campaign(brandId: str, campaignIn: CampaignIn,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_admin_user)):
   
    # print(CampaignIn)
    campaign = dict()
    campaign["uid"] = util.getUuid()
    campaign["name"] = campaignIn.name
    campaign["code"] = campaignIn.code
    campaign["description"] = campaignIn.description
    campaign["createDateTime"] = datetime.now()
    campaign["status"] = "active"
    # campaign["credit"] = campaignIn.credit
    # campaign["packageSize"] = campaignIn.packageSize

    campaign["startDateTime"] = campaignIn.startDateTime
    campaign["endDateTime"] = campaignIn.endDateTime
    campaign["totalAmount"] = campaignIn.totalAmount
    campaign["usedAmount"] = campaignIn.usedAmount
    campaign["domainId"] = brandId

    # print(campaignIn.dataImage)

    if campaignIn.dataImage : 
        imgResult = await fileRepo.base64Image(file = campaignIn.dataImage) 
        if imgResult["success"] == True :
            campaign["dataImage"] = imgResult["result"]["fileName"]
   

    # logger.info(">>>>>>>>>>>> userReg  DB >>>>>>>>>>>>>>>>>>>>>")

    # print(">>>>>>>>>>>> userReg  DB >>>>>>>>>>>>>>>>>>>>>")
    # print(campaign)

    try: 
        row1 = await db["ecouponv1"]["campaign"].insert_one(campaign)
    except:
        raise HTTPException(status_code=400, detail="Unable to save data to database")

    # return userdb

#******************************************
#*** [2.2.2] shop add campaign เองไม่ได้ !!!!! add-campaign [only shop]
#******************************************
# @router.post("/shop/add-campaign",  tags=["ecoupon"] )
# async def add_campaign_forshop(campaignIn: CampaignIn,  db: AsyncIOMotorClient =  Depends(get_database)  , currentUser  : user.UserDb = Depends(authRepo.get_current_shop_user)   ):
   
#     #*** Diff with admin
#     domainId = currentUser.domainId
#     brand =  await db["ecouponv1"]["brand"].find_one( { "uid" : domainId } ) 

#     if not brand:
#         raise HTTPException(status_code=400, detail="Bad request: Not found brand")

#     # print(updated)

#     # print(CampaignIn)
#     campaign = dict()
#     campaign["uid"] = util.getUuid()
#     campaign["name"] = campaignIn.name
#     campaign["code"] = campaignIn.code
#     campaign["description"] = campaignIn.description
#     campaign["createDateTime"] = datetime.now()
#     campaign["status"] = "active"
#     # campaign["credit"] = campaignIn.credit
#     # campaign["packageSize"] = campaignIn.packageSize

#     campaign["startDateTime"] = campaignIn.startDateTime
#     campaign["endDateTime"] = campaignIn.endDateTime
#     campaign["totalAmount"] = campaignIn.totalAmount
#     campaign["usedAmount"] = campaignIn.usedAmount
#     #*** Diff with admin
#     campaign["domainId"] = domainId

#     # print(campaignIn.dataImage)

#     if campaignIn.dataImage : 
#         imgResult = await fileRepo.base64Image(file = campaignIn.dataImage) 
#         if imgResult["success"] == True :
#             campaign["dataImage"] = imgResult["result"]["fileName"]
   

#     # logger.info(">>>>>>>>>>>> userReg  DB >>>>>>>>>>>>>>>>>>>>>")

#     # print(">>>>>>>>>>>> userReg  DB >>>>>>>>>>>>>>>>>>>>>")
#     # print(campaign)

#     try: 
#         row1 = await db["ecouponv1"]["campaign"].insert_one(campaign)
#     except:
#         raise HTTPException(status_code=400, detail="Unable to save data to database")

#     # return userdb

#******************************************
#*** [1.4.1] load-single-brand/ [only admin]
#******************************************

@router.post("/load-single-brand/{id}",  tags=["ecoupon"] )
async def load_single_brand(id: Optional[str] = None,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_admin_user)):
   
    row =  await db["ecouponv1"]["brand"].find_one( { "uid" : id } ) 
   
    if row:
        return BrandOut(**row)
    else:
        raise HTTPException(
                        status_code=400, detail="Bad request: Unable to update record"
                    )
   
    return res


#******************************************
#*** [1.4.2] load-single-brand/ [only shop]
#******************************************

@router.post("/shop/load-single-brand",  tags=["ecoupon"] )
async def load_single_brand_shop(id: Optional[str] = None,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_shop_user)):
   
    row =  await db["ecouponv1"]["brand"].find_one( { "uid" : currentUser.domainId } ) 
   
    if row:
        return BrandOut(**row)
    else:
        raise HTTPException(
                        status_code=400, detail="Bad request: Unable to update record"
                    )
   
    return res



#******************************************
#*** [2.4] load-single-campaign
#******************************************
@router.post("/load-single-campaign/{id}",  tags=["ecoupon"] )
async def load_single_campaign(id: Optional[str] = None,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
   
    #*** load campaing
    row =    await db["ecouponv1"]["campaign"].find_one( { "uid" : id } ) 
   
    if row:
        return CampaignOut(**row)
    else:
        raise HTTPException(
                        status_code=400, detail="Bad request: Unable to update record"
                    )

    
   
    return res


# @router.post("/load-single-coupon/{id}",  tags=["ecoupon"] )
# async def load_single_coupon(id: Optional[str] = None,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
   
#     row =    await db["ecouponv1"]["coupon"].find_one( { "uid" : id } ) 
   
#     if row:
#         return couponOut(**row)
#     else:
#         raise HTTPException(
#                         status_code=400, detail="Bad request: Unable to update record"
#                     )
   
#     return res


#******************************************
#*** [1.4.2] load-single-brand/ [only shop]
#******************************************

@router.post("/shop/load-single-brand",  tags=["ecoupon"] )
async def load_single_brand_shop(id: Optional[str] = None,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
   
    row =  await db["ecouponv1"]["brand"].find_one( { "uid" : currentUser.domainId } ) 
   
    if row:
        return BrandOut(**row)
    else:
        raise HTTPException(
                        status_code=400, detail="Bad request: Unable to update record"
                    )
   
    return res

#******************************************
#*** [4.1] Sending multiple SMSs (กด click check แล้วส่ง sms)
#******************************************

@router.post("/sending-multiple-sms",  tags=["ecoupon"] )
async def sending_sms(couponList: List[CouponEdit],  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
    # print(">>>>>>>>>>>>>. couponList >>>>>>>>>>>>>>>>")
    # print(couponList)

    if not couponList:
        raise HTTPException(status_code=400, detail="Request parameter not valid")

    res = dict()

    #*** (1) list of ids of coupons that will send SMS
    couponListIds = [ xx.uid for xx in couponList  ]

    rows =     db["ecouponv1"]["coupon"].find( 
                                                { "campaignId" : couponList[0].campaignId } 
                                                        
                                             ).sort("createDateTime",-1)


    coupon_db = [CouponDb(**row) async for row in rows if row["couponStatus"] == "ว่างอยู่" or row["couponStatus"] == "ส่งออก" ]



    domainId = coupon_db[0].domainId

    brand =  await db["ecouponv1"]["brand"].find_one( { "uid" : domainId } ) 

    if not brand:
        raise HTTPException(
                        status_code=400, detail="Bad request: Brand Not Found"
                    )



    #*** BEGIN: LOAD CAMPAIGN FOR SMSUSINGAMOUNT


    campaign =  await db["ecouponv1"]["campaign"].find_one( { "uid" : couponList[0].campaignId } ) 

    if not campaign:
        raise HTTPException(
                        status_code=400, detail="Bad request: Campaign Not Found"
                    )
    
    smsUsingAmount = 0
    if not campaign["smsUsedCredit"]:
        smsUsingAmount = 0
        raise HTTPException(status_code=400, detail="Bad request: Need to set smsUsedCredit")
    else:
        smsUsingAmount =  campaign["smsUsedCredit"]

    if not campaign["smsContent"]:
        smsMessage = ""
    else:
        smsMessage = campaign["smsContent"] 

    
    if not campaign["smsSender"]:
        res["success"] = False
        res["detail"] = "SMS_SENDER_NAME_REQUIRED"
        res["msg"] = "ยังไม่ได้ตั้งชื่อผู้ส่ง SMS"
        # res["totalItem"] = len(coupon_ids_changes)
        res["totalCoupon"] = 0
        res["totalSms"] = 0
        return res
    else:
        smsSender = campaign["smsSender"] 

     #*** END: LOAD CAMPAIGN FOR SMSUSINGAMOUNT

   
    # if brand["smsUsingAmount"]:
    #     smsUsingAmount = brand["smsUsingAmount"]


                                         
    #*** function ส่งแค่ sms
    brandSmsCredit =  brand["smsCredit"]



    newCouponListIds = [ yy.uid for yy in coupon_db  ]

    #*** (2) Filter only Coupon that has id in couponListIds (1)
    couponSentList = []
    coupon_ids_changes = []
    res["success"] = True

    
    for a_coupon in coupon_db:
        if a_coupon.couponStatus != "ว่างอยู่" and a_coupon.couponStatus != "ส่งออก" :
            continue
        if a_coupon.uid in couponListIds:
            #*** (2.1) ส่ง SMS
            #*** ไม่มีเบอร์ลูกค้า
            if not a_coupon.phone : 
                continue
            else: 
                #*** BEGIN: ส่ง SMS
                #***  Check sms credit before sending
                # print(f"brandSmsCredit >>> {brandSmsCredit > 0}")
                # print(f"smsUsingAmount >>> {smsUsingAmount}")
                if brandSmsCredit > 0 and brandSmsCredit >= smsUsingAmount : 
                    # print("@@@@@@@@@@@@@@  BEGIN @@@@@@@@@@@@@@@@@@@@@@")
                    sendingResult = utilRepo.sendSms(phone=a_coupon.phone , coupon=a_coupon.couponCode, couponStatus=a_coupon.couponStatus, smsMessage=smsMessage, smsSender=smsSender)
                    # print("@@@@@@@@@@@@@@  END @@@@@@@@@@@@@@@@@@@@@@")
                    #*** END: ส่ง SMS
                    if sendingResult == True:
                        brandSmsCredit = brandSmsCredit - smsUsingAmount
                        couponSentList.append(a_coupon.dict())
                        coupon_ids_changes.append(a_coupon.uid)
                    else:
                        res["success"] = False
                        res["detail"] = "SMS_API_NOT_COMPLETE"
                        res["msg"] = "การส่ง SMS ไม่สมบูรณ์"
                        # res["totalItem"] = len(coupon_ids_changes)
                        res["totalCoupon"] = 0
                        res["totalSms"] = 0

                else:
                    res["success"] = False
                    res["detail"] = "INSUFFICIENT_SMS_CREDIT"
                    res["msg"] = "เครดิต sms ไม่พอ"
                    # res["totalItem"] = len(coupon_ids_changes)
                    res["totalCoupon"] = 0
                    res["totalSms"] = len(coupon_ids_changes) * smsUsingAmount
                    return res
    
    #*** function ส่งแค่ sms
    updated = dict()
    updated["smsCredit"] = brandSmsCredit

    #*** (3) update 
    try: 
        edit = await db["ecouponv1"]["coupon"].update_many({"uid" : { "$in" : coupon_ids_changes}}, { "$inc" : { "sentSms" : 1  } , '$set': {"couponStatus" : "ส่งออก"  } })

        db["ecouponv1"]["brand"].update_one({"uid" : domainId}, {'$set': updated  } )
    except:
        raise HTTPException(status_code=400, detail="Unable to save data to database")

    # res["totalItem"] = len(coupon_ids_changes)
    res["totalCoupon"] = 0
    res["totalSms"] = len(coupon_ids_changes) * smsUsingAmount
    # res["result"] = couponSentList


    print(res)

    return res 

    
#******************************************
#*** [4.2] Sending Single SMS (กด icon รูปจรวด)
#******************************************

@router.post("/sending-single-sms/{couponId}",  tags=["ecoupon"] )
async def sending_single_sms(couponId: str,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
    

    if not couponId:
        raise HTTPException(status_code=400, detail="Request parameter not valid")

    res = dict()

    row =  await db["ecouponv1"]["coupon"].find_one( { "uid" : couponId } ) 

    if not row:
        raise HTTPException(status_code=400, detail="Bad request: Not found code")

    #*** (1.1) Check couponStatus ว่าโอเคหรือไม่

    if row["couponStatus"] != "ว่างอยู่" and row["couponStatus"] != "ส่งออก" :
        raise HTTPException(status_code=400, detail="Bad request: SMS not available for this status")

    coupon_db = CouponDb(**row)
    

    #*** (1) list of ids of coupons that will send SMS
    domainId = coupon_db.domainId
    brand =  await db["ecouponv1"]["brand"].find_one( { "uid" : domainId } ) 

    if not brand:
        raise HTTPException(
                        status_code=400, detail="Bad request: Brand Not Found"
                    )



    #*** BEGIN: LOAD CAMPAIGN FOR SMSUSINGAMOUNT

    campaign =  await db["ecouponv1"]["campaign"].find_one( { "uid" : row["campaignId"] } ) 

    if not campaign:
        raise HTTPException(
                        status_code=400, detail="Bad request: Campaign Not Found"
                    )
    
    smsUsingAmount = 0
    if not campaign["smsUsedCredit"]:
        smsUsingAmount = 0
        raise HTTPException(status_code=400, detail="Bad request: Need to set smsUsedCredit")
    else:
        smsUsingAmount =  campaign["smsUsedCredit"]

    if not campaign["smsContent"]:
        smsMessage = ""
    else:
        smsMessage = campaign["smsContent"] 

    # print(campaign["smsSender"])

    if not campaign["smsSender"]:
        res["success"] = False
        res["detail"] = "SMS_SENDER_NAME_REQUIRED"
        res["msg"] = "ยังไม่ได้ตั้งชื่อผู้ส่ง SMS"
        # res["totalItem"] = len(coupon_ids_changes)
        res["totalCoupon"] = 0
        res["totalSms"] = 0
        
        return res
    else:
        smsSender = campaign["smsSender"] 

    #*** END: LOAD CAMPAIGN FOR SMSUSINGAMOUNT


    #*** LOAD smsUsingAmount
    # smsUsingAmount =  1
    # if brand["smsUsingAmount"]:
    #     smsUsingAmount = brand["smsUsingAmount"]
    

    #*** function ส่งแค่ sms
    brandSmsCredit =  brand["smsCredit"]




    #*** ถ้าไม่มีเบอร์ ไม่ให้ส่ง
    # if not coupon_db.phone:
    #     raise HTTPException(
    #                     status_code=400, detail="Bad request: No customer information")

    #*** (2) Filter only Coupon that has id in couponListIds (1)
    # print(f"brandSmsCredit >>> {brandSmsCredit > 0}")
    # print(f"brandSmsCredit >>> {brandSmsCredit}")
    # print(f"brandSmsCredit >= smsUsingAmount >>> {brandSmsCredit >= smsUsingAmount}")



    #*** (2.1) ส่ง SMS
    changeStatus = f"ว่างอยู่"
    if brandSmsCredit > 0 and brandSmsCredit >= smsUsingAmount :
        # print("@@@@@@@@@@@@@@  BEGIN @@@@@@@@@@@@@@@@@@@@@@")
        sendingResult = utilRepo.sendSms(phone=coupon_db.phone , coupon=coupon_db.couponCode , couponStatus=coupon_db.couponStatus, smsMessage=smsMessage, smsSender=smsSender)
        # print("@@@@@@@@@@@@@@  END @@@@@@@@@@@@@@@@@@@@@@")
        if sendingResult == True:
            brandSmsCredit = brandSmsCredit - smsUsingAmount
            changeStatus = f"ส่งออก"
        else:
            res["success"] = False
            res["detail"] = "SMS_API_FAILED"
            res["msg"] = "โปรดตรวจสอบชื่อผู้ส่งหรือข้อมูลอื่นๆ SMS"
            # res["totalItem"] = len(coupon_ids_changes)
            res["totalCoupon"] = 0
            res["totalSms"] = 0
            return res
    else:
        res["success"] = False
        res["detail"] = "INSUFFICIENT_SMS_CREDIT"
        res["msg"] = "เครดิตคูปองไม่พอ"
        # res["totalItem"] = len(coupon_ids_changes)
        res["totalCoupon"] = 0
        res["totalSms"] = 0
        return res

    updated = dict()
    updated["smsCredit"] = brandSmsCredit

    #*** (3) update 
    try: 
        edit = await db["ecouponv1"]["coupon"].update_one({"uid" : coupon_db.uid}, { "$inc" : { "sentSms" : 1  } , '$set': {"couponStatus" : changeStatus  } })

        await db["ecouponv1"]["brand"].update_one({"uid" : domainId}, {'$set': updated  } )
    except:
        raise HTTPException(status_code=400, detail="Unable to save data to database")


    print("@@@@@@@@@@@@@@  BEGIN @@@@@@@@@@@@@@@@@@@@@@")
    res["success"] = True
    # res["totalItem"] = len(coupon_ids_changes)
    res["totalCoupon"] = 0
    res["totalSms"] = smsUsingAmount
    # res["result"] = couponSentList

    return res 
   

#******************************************
#*** [x.x.x] Brand TEST
#******************************************

# @router.post("/brandtest",  tags=["ecoupon"] )
# # async def update_brand(id: str , brandEdit: BrandEdit,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
# async def brandTest(brandEditList: List[BrandUpdate] ,  db: AsyncIOMotorClient =  Depends(get_database)):
   
#     if not brandEditList:
#         raise HTTPException(status_code=400, detail="Request parameter not valid")

#     #*** (1) list of ids of coupons that will send SMS
#     ids = [ xx.uid for xx in brandEditList]

#     rows =   db["ecouponv1"]["brand"].find({"uid" : { "$in" : ids}})

#     rList = [ r async for r in rows]

#     ind = 0
#     for rl in rList : 
#         rl["name"] = brandEditList[ind].name
#         rl["description"] = brandEditList[ind].description
#         rl["credit"] = brandEditList[ind].credit
#         rl["packageSize"] = brandEditList[ind].packageSize
#         ind = ind + 1

#     # print("_-_--___-_____------ ROW")
#     # print(rList)
#     # print("ROW___------_-_--___-__ ")
    
#     # updated = brandEdit.dict()

#     edit = await db["ecouponv1"]["brand"].update_many({}, {'$set': rList })

#     # try: 
#     #     edit = await db["ecouponv1"]["brand"].update_many({"uid": id}, {'$set': updated })
#     # except:
#     #     raise HTTPException(status_code=400, detail="Unable to save data to database")


