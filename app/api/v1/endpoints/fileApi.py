from typing import List, Optional , Any, Dict

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks


from repo import  userRepo, authRepo, fileRepo

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

from utils import util
import pandas as pd
import pyexcel
import pyexcel_xlsx


router = APIRouter()

class UploadedFile(BaseModel):
    dataFile: Optional[str] = "" 
    



@router.post("/upload-multiple-files",  tags=["file"])
async def upload_multiple_files(files: List[UploadFile] = File(...)):

    fileData = await fileRepo.uploadMultipleFile(files)
    return fileData

@router.post("/upload-file",  tags=["file"])
async def upload_file(file : UploadFile = File(...)):

    fileData = await fileRepo.uploadSingleFile(file)
    return fileData


#***************************************************


@router.post("/upload-excel/{id}",  tags=["file"])
# async def upload_excel(id : str, fileData :UploadFile = File(...),db: AsyncIOMotorClient =  Depends(get_database)  ):
async def upload_excel(id : str, fileData :UploadFile = File(...),db: AsyncIOMotorClient =  Depends(get_database) , currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)  ):
    # currentUser = user.UserDb
    fileData = await fileRepo.uploadExcel(id , fileData, db, currentUser )
    return fileData


@router.post("/upload-excel-send-sms/{id}",  tags=["file"])
async def upload_excel_send_sms(id : str, fileData :UploadFile = File(...),db: AsyncIOMotorClient =  Depends(get_database) , currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)  ):
    fileData = await fileRepo.uploadExcelSendSms(id , fileData, db, currentUser )
    return fileData

#***************************************************

@router.post("/base64-image",  tags=["file"])
async def upload_excel(fileObj : UploadedFile = None ):

    fileString = fileObj.dataFile
    print(f"fileString >>> {fileString}")
    fileData = await fileRepo.base64Image(fileString)
    return fileData
    
@router.post("/upload-image",  tags=["file"])
async def image(files: UploadFile = File(...)):
    rd = await file.read()
    print(len(rd))
    with open("assets/images/user/destination.png", "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # sizeOfFile = await file.read()
    content = await image.read()
    file_size = len(content)

    
    return rd

@router.post("/get-excel",  tags=["file"])
async def get_excel():


    loc = "assets/images/user/ced6641a-c65e-11ec-872e-6c4008ad0d26.xlsx"

    # df = pd.read_excel(loc)
    # print (df)
    
    excelArr = pyexcel.get_array(file_name=loc)

    print("excelArr >>>> ",excelArr)

 
    # wb = xlrd.open_workbook(loc)
    # sheet = wb.sheet_by_index(0)
    # sheet.cell_value(0, 0)
    
    # # Extracting number of rows
    # print(sheet.nrows)

    # return {"filename": image.filename}

