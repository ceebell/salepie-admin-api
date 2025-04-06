from passlib.context import CryptContext
from typing import List, Optional
from pydantic import BaseModel, Json ,ValidationError, validator, Field, EmailStr

from loguru import logger
from models import user, schemas
from database.mongodb  import AsyncIOMotorClient, get_database
from utils import util

from datetime import datetime, date
from dateutil.parser import parse

from . import authRepo, utilRepo

from fastapi import APIRouter, Depends, HTTPException, UploadFile

import json
import uuid

# from sqlalchemy.orm import Session

import shutil
from utils import util
# import pandas as pd
import pyexcel
import pyexcel_xlsx
import base64

import os
os.path.abspath("mydir/")



class CouponFileDb(BaseModel):
    uid: Optional[str] = ""
    seq: Optional[int] = ""
    couponCode: Optional[str] = ""
    customerName: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    couponStatus : Optional[str] = ""
    startDateTime : Optional[date]
    endDateTime : Optional[date]
    accessCount: Optional[int] = 0
    sentSms: Optional[int] = 0
    usedDateTime : Optional[datetime]
    createDateTime : Optional[datetime]
    createdBy : Optional[str] = ""
    expireDateTime : Optional[date]
    campaignId : Optional[str] = ""
    domainId : Optional[str] = ""

# LOCAL_FOLDER = "assets/excel/"
LOCAL_FOLDER = "/var/www/couponImage/"

#*** https://levelup.gitconnected.com/how-to-save-uploaded-files-in-fastapi-90786851f1d3
#*** https://fastapi.tiangolo.com/tutorial/request-files/
async def uploadMultipleFile(files : List[UploadFile]) -> dict:

    fileList = []

    try:
        for file in files:
            new_guid = util.getUuid()
            tmp_file_name = file.filename.split(".")
            new_file_name = f"{new_guid}.{tmp_file_name[1]}"
            # sizeOfFile = await file.read()
            content = await file.read()
            file_size = len(content)



            aFile = dict()
            aFile["fileName"] = f"{new_file_name}"
            aFile["fileSize"] = file_size
            aFile["uploadedName"] = file.filename

            
            with open(f"{LOCAL_FOLDER}{new_file_name}", "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
        
            
            # a["size"] = file.size
            
            fileList.append(aFile)
    except:
        return json.loads('{"success" : False, "message":"something went wrong" }')

    res = dict()
    res["success"] = True
    res["result"] = fileList

    # aa = f"'success' : True, 'message': {json.dumps(fileList)} "
        
    return res


async def uploadSingleFile(file : UploadFile) -> dict:


    try:
        new_guid = util.getUuid()
        tmp_file_name = file.filename.split(".")
        new_file_name = f"{new_guid}.{tmp_file_name[1]}"
        # sizeOfFile = await file.read()
        content = await file.read()
        file_size = len(content)



        aFile = dict()
        aFile["fileName"] = f"{new_file_name}"
        aFile["fileSize"] = file_size
        aFile["uploadedName"] = file.filename

        
        with open(f"{LOCAL_FOLDER}{new_file_name}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)


            
        
    except:
        return json.loads('{"success" : False, "message":"something went wrong" }')

    res = dict()
    res["success"] = True
    res["result"] = aFile

    return res

#***************************************************
#*** [99.1] UPLOAD EXCEL
#***************************************************


async def uploadExcel(id: str, file : UploadFile, db: AsyncIOMotorClient,currentUser : user.UserDb) -> dict:

    camp =  await db["ecouponv1"]["campaign"].find_one( { "uid" : id } ) 

    # print(camp)

    if not camp:
        raise HTTPException(
                        status_code=400, detail="Bad request: Campaign ID Not Found"
                    )
    
    # campDict = camp.dict()
    
    


    

   

    couponPrefix = camp["code"]
    campaignId = camp["uid"]
    startDateTime =  camp["startDateTime"]
    endDateTime =  camp["endDateTime"]
    domainId = camp["domainId"]
    
    brand =  await db["ecouponv1"]["brand"].find_one( { "uid" : domainId } ) 

    if not brand:
        raise HTTPException(
                        status_code=400, detail="Bad request: Brand Not Found"
                    )

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
    
    #****************** Continue here!
    

    # itemList = [CouponOut(**row) async for row in rows  ]

    #*** function นี้สร้างคูปองอย่างเดียว
    brandCouponCredit =  brand["credit"]
    # brandSmsCredit =  brand["smsCredit"]

    # try:
    new_guid = str(uuid.uuid4())
    # tmp_file_name = file.filename.split(".")
    new_file_name = f"{new_guid}.xlsx"
    # sizeOfFile = await file.read()
    # content = await file.read()
    # file_size = len(content)



    aFile = dict()
    aFile["fileName"] = f"{new_file_name}"
    aFile["fileSize"] = ""

    localFolder = os.path.abspath(f"{LOCAL_FOLDER}")
    
    with open(f"{localFolder}/{new_file_name}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    excelArr = pyexcel.get_array(file_name=f"{localFolder}/{new_file_name}")

    # print("excelArr >>>> ",excelArr)

    timenow = datetime.now()
    
    # logger.info(f"Extract EXCEL file {new_file_name}")
    # logger.info(f"Extract length number of record {len(excelArr)}")
    

    customerList = []
    ind = 0
    for row in excelArr:


        if ind == 0:
            ind = ind + 1
            continue
        
        #*** ไม่มีเบอร์ลูกค้า
        if not row[0] :
            continue
        ### @@@ External code
        if len(row) <= 3:
            row.append("")
            
        # print(f"row[0] >>> {row[0]} row[1] >>> {row[1]} row[2] >>> {row[2]} row[3] >>> {row[3]}")

        exres = dict()
        exres["uid"] = str(uuid.uuid4())
        exres["phone"] = row[0]
        exres["email"] = row[1]
        exres["customerName"] = row[2]
        
        ### @@@[Edit][9Jan2023]
        exres["externalCode"] = row[3]
        
        exres["couponCode"] = f"{couponPrefix}{util.genUpperAlphaNumbericText(10)}"
        exres["couponStatus"] = f"ว่างอยู่"
        exres["startDateTime"] = parse(startDateTime).strftime("%Y-%m-%d")
        exres["endDateTime"] = parse(endDateTime).strftime("%Y-%m-%d")
        exres["expireDateTime"] = parse(endDateTime).strftime("%Y-%m-%d")
        recordNow =  datetime.now()
        exres["createDateTime"] = recordNow.strftime("%Y-%m-%d %H:%M:%S.%f")
        # exres["updateDateTime"] = timenow.strftime("%Y-%m-%d %H:%M:%S.%f")
        exres["createBy"] =  currentUser.username
        exres["campaignId"] =  campaignId
        exres["domainId"] =  domainId
        exres["sentSms"] = 0
        
        
        
        # print(f"type max = {type(the_maximum)} maximum >>> {the_maximum} for {row[1]}")
        
        the_maximum = the_maximum + 1
        exres["seq"] = the_maximum

        if brandCouponCredit > 0 :
            customerList.append(exres)
            brandCouponCredit = brandCouponCredit - 1
        else:
            break
        



        ind = ind + 1

    # db_data = List(CouponFileDb(**customerList))
    
    # print(customerList)

    updated = dict()
    updated["credit"] = brandCouponCredit

    try:
        db["ecouponv1"]["coupon"].insert_many(customerList) 
        # #*** (3) update brand
        edit =  db["ecouponv1"]["brand"].update_one({"uid" : domainId}, {'$set': updated} )
   
    except:
        return json.loads('{"success" : False, "message":"something went wrong" }')

    res = dict()
    res["success"] = True
    res["totalCoupon"] = len(customerList)
    res["totalSms"] = 0

    return res

#***************************************************
#******** [99.2]   UPLOAD EXCEL & SEND SMS      ****
#***************************************************

async def uploadExcelSendSms(id: str, file : UploadFile, db: AsyncIOMotorClient,currentUser : user.UserDb) -> dict:

    camp =  await db["ecouponv1"]["campaign"].find_one( { "uid" : id } ) 

    # print(camp)

    if not camp:
        raise HTTPException(
                        status_code=400, detail="Bad request: Campaign ID Not Found"
                    )

    res = dict()
    
    
    # campDict = camp.dict()

    # print(">>>>>>>>>>>>>> campaign upload file >>>>>>>>>> ")

    couponPrefix = camp["code"]
    campaignId = camp["uid"]
    startDateTime =  camp["startDateTime"]
    endDateTime =  camp["endDateTime"]
    domainId = camp["domainId"]
    
    brand =  await db["ecouponv1"]["brand"].find_one( { "uid" : domainId } ) 

    if not brand:
        raise HTTPException(
                        status_code=400, detail="Bad request: Brand Not Found"
                        
                    )

    

    #*** BEGIN: LOAD CAMPAIGN FOR SMSUSINGAMOUNT

    # campaign =  await db["ecouponv1"]["campaign"].find_one( { "uid" : couponId } ) 

    # if not campaign:
    #     raise HTTPException(
    #                     status_code=400, detail="Bad request: Campaign Not Found"
    #           )
    
    smsUsingAmount = 0
    if not camp["smsUsedCredit"]:
        smsUsingAmount = 0
        raise HTTPException(status_code=400, detail="Bad request: Need to set smsUsedCredit")
    else:
        smsUsingAmount =  camp["smsUsedCredit"]

    if not camp["smsContent"]:
        smsMessage = ""
    else:
        smsMessage = camp["smsContent"]

    if not camp["smsSender"]:
        res["success"] = False
        res["detail"] = "SMS_SENDER_NAME_REQUIRED"
        res["msg"] = "ยังไม่ได้ตั้งชื่อผู้ส่ง SMS"
        # res["totalItem"] = len(coupon_ids_changes)
        res["totalCoupon"] = 0
        res["totalSms"] = 0
        return res
    else:
        smsSender = camp["smsSender"] 

    #*** END: LOAD CAMPAIGN FOR SMSUSINGAMOUNT

    #*** LOAD smsUsingAmount
    # smsUsingAmount =  1
    # if brand["smsUsingAmount"]:
    #     smsUsingAmount = brand["smsUsingAmount"]
    
    
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
    


    #*** function นี้สร้างคูปอง และส่ง sms
    brandCouponCredit =  brand["credit"]
    brandSmsCredit =  brand["smsCredit"]

    # try:
    new_guid = str(uuid.uuid4())
    # tmp_file_name = file.filename.split(".")
    new_file_name = f"{new_guid}.xlsx"
    # sizeOfFile = await file.read()
    # content = await file.read()
    # file_size = len(content)



    aFile = dict()
    aFile["fileName"] = f"{new_file_name}"
    aFile["fileSize"] = ""
    
    localFolder = os.path.abspath(f"{LOCAL_FOLDER}")

    
    with open(f"{localFolder}/{new_file_name}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    excelArr = pyexcel.get_array(file_name=f"{localFolder}/{new_file_name}")

    # print("excelArr >>>> ",excelArr)

    timenow = datetime.now()

    customerList = []
    ind = 0
    sendingSms = 0
    res["success"] = True


    for row in excelArr:
        # print(row)
        if ind == 0:
            ind = ind + 1
            continue

        #*** ไม่มีเบอร์ลูกค้า
        if not row[0]:
            continue
        
        ### @@@ External code
        if len(row) <= 3:
            row.append("")

        exres = dict()
        exres["uid"] = str(uuid.uuid4())
        exres["phone"] = row[0]
        exres["email"] = row[1]
        exres["customerName"] = row[2]
        
        # [Edit][9Jan2023]
        exres["externalCode"] = row[3]
        
        exres["couponCode"] = f"{couponPrefix}{util.genUpperAlphaNumbericText(10)}"
        
        exres["startDateTime"] = parse(startDateTime).strftime("%Y-%m-%d")
        exres["endDateTime"] = parse(endDateTime).strftime("%Y-%m-%d")
        exres["expireDateTime"] = parse(endDateTime).strftime("%Y-%m-%d")
        recordNow =  datetime.now()
        exres["createDateTime"] = recordNow.strftime("%Y-%m-%d %H:%M:%S.%f")
        exres["createBy"] =  currentUser.username
        exres["campaignId"] =  campaignId
        exres["domainId"] =  domainId
        exres["sentSms"] = 1
        
        the_maximum = the_maximum + 1
        exres["seq"] = the_maximum

        if brandCouponCredit > 0   :
           
            exres["couponStatus"] = f"ว่างอยู่"       
            
            if brandSmsCredit > 0 and brandSmsCredit >= smsUsingAmount:
                # print("@@@@@@@@@@@@@@  BEGIN @@@@@@@@@@@@@@@@@@@@@@")
                sendingResult = utilRepo.sendSms(phone=exres["phone"] , coupon=exres["couponCode"] , couponStatus=exres["couponStatus"], smsMessage=smsMessage, smsSender=smsSender)
                # print("@@@@@@@@@@@@@@  END @@@@@@@@@@@@@@@@@@@@@@")
                if sendingResult == True:
                    brandSmsCredit = brandSmsCredit - smsUsingAmount
                    exres["couponStatus"] = f"ส่งออก"
                    sendingSms = sendingSms + 1
                else:
                    res["success"] = False
                    res["detail"] = "SMS_API_NOT_COMPLETE"
                    res["msg"] = "การส่ง SMS ไม่สมบูรณ์"
            
            brandCouponCredit = brandCouponCredit - 1
            customerList.append(exres)

        else:
            break
        
        ind = ind + 1
    
    # print(type(customerList))

    # customerJson = json.dumps(customerList)


    # print(len(customerList))

    updated = dict()
    updated["credit"] = brandCouponCredit
    updated["smsCredit"] = brandSmsCredit

    # print("&&&&&&&&&&&&&&  BEGIN INSERT MANY &&&&&&&&&&&&&&")

    if len(customerList) > 0:
        db["ecouponv1"]["coupon"].insert_many(customerList) 


    # print("&&&&&&&&&&&&&&  BEGIN UPDATE DB &&&&&&&&&&&&&&")

    if updated:
        edit = db["ecouponv1"]["brand"].update_one({"uid" : domainId}, {'$set': updated  } )
        
    # print("&&&&&&&&&&&&&&  BEGIN END DB &&&&&&&&&&&&&&")
    # except:
    #     return json.loads('{"success" : False, "message":"something went wrong" }')

    # print("&&&&&&&&&&&&&&  BEGIN END DB &&&&&&&&&&&&&&")

    totalCoupon = len(customerList)


    if totalCoupon > sendingSms:
        res["success"] = False
        res["detail"] = "INSUFFICIENT_SMS_CREDIT"
        res["msg"] = "เครดิต sms ไม่พอ"

    
    res["totalCoupon"] = totalCoupon
    res["totalSms"] = sendingSms * smsUsingAmount
    # res["result"] = customerList

    # print(res)

    return res

#***************************************************


async def base64Image(file : str) -> dict:

    res = dict()

    # เอา content
    img = file.split(",")

    # เอา สกุล
    detail = file.split(";")

    ext = ".png"

    if "jpeg" in detail[0]: 
        ext = ".jpeg"

    elif  "jpg" in detail[0]: 
        ext = ".jpg"


    # try:
    new_guid = util.getUuid()
    # tmp_file_name = file.filename.split(".")
    new_file_name = f"{new_guid}{ext}"
    # sizeOfFile = await file.read()

    try:

        # https://stackoverflow.com/questions/16214190/how-to-convert-base64-string-to-image
        imgdata = base64.b64decode(img[1])
        with open(f"{LOCAL_FOLDER}{new_file_name}", 'wb') as f:
            f.write(imgdata)
        
        
        # content = await imgdata.read()
        # file_size = len(content)

        aFile = dict()
        aFile["fileName"] = f"{new_file_name}"
        # aFile["fileSize"] = file_size

    
        
    except:
        res["success"] = False
        res["totalItem"] = 0
        res["result"] = None
        return res


    res["success"] = True
    res["totalItem"] = 0
    res["result"] = aFile

    return res