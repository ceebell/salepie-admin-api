import os
from typing import List
import uuid
import random
import string
import base64

from datetime import datetime,timezone

# from git import List
from core.config import MAX_IMAGE_BYTES, ALLOWED, dataurl_re, PRODUCT_IMAGE_URL, PRODUCT_UPLOAD_ROOT, ALLOWED_EXTENSIONS
from fastapi import HTTPException, UploadFile
from pydantic import BaseModel, Json ,ValidationError, validator, Field, EmailStr
import re
import logging
import shutil

import json


logger = logging.getLogger("salepie.utils.util")


def getUuid():
    uid = str(uuid.uuid4())
    return uid

def base64Encoding(text):
    text_string_bytes = text.encode("ascii")
    base64_bytes = base64.b64encode(text_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string

def base64Encoding(base64text):
    text_string_bytes = base64text.encode("ascii")
    sample_string_bytes = base64.b64decode(text_string_bytes)
    base64_string = sample_string_bytes.decode("ascii")
    return base64_string

def genRandomText(number):
    code = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k = number))
    return code

def genUpperAlphaNumbericText(number):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k = number))
    return code

def genRandomDigit(number):
    code = ''.join(random.choices(string.digits, k = number))
    return code


def getShopCode():
    code_date = datetime.today().strftime("%Y%m%d")
    print(f"code_date = {code_date}")
    code_suff = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 8))
    print(f"code = {code_suff}")
    # code_a = ''.join(code_date , "_" , code)
    res = f"{code_date}_{code_suff}"
    print(f"result  = {res}")
    return res

def convertDateTime(obj):
    
    # print(f"convertDateTime >>>>>>>>> {obj}")
    keys = list(obj.keys())
    
    for aKey in keys:
        # value = obj['aKey']
        print(f"{aKey} >>>>>>>>> {obj[aKey]}")
        if(aKey.lower().find("at") > -1 or aKey.lower().find("datetime") > -1):
            if(obj[aKey]):
                print(aKey)
                obj[aKey] = obj[aKey].strftime("%Y-%m-%d %H:%M:%S.%f")
    return obj



def save_product_data_url_image(data_url: str, domainId: str) -> dict:
    m = dataurl_re.match(data_url or "")
    if not m:
        raise HTTPException(status_code=400, detail="Invalid image dataUrl")

    content_type = m.group(1)
    b64 = m.group(2)

    try:
        raw = base64.b64decode(b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 payload")

    if len(raw) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail="Image too large (max 5MB)")

    ext = ALLOWED.get(content_type)
    if not ext:
        raise HTTPException(status_code=400, detail=f"Unsupported image type: {content_type}")

    prod_dir = PRODUCT_UPLOAD_ROOT / domainId
    prod_dir.mkdir(parents=True, exist_ok=True)

    filename = f"main_{uuid.uuid4().hex}{ext}"
    path = prod_dir / filename
    path.write_bytes(raw)

    return {
        "seq": 0,
        "getUrl": f"{PRODUCT_IMAGE_URL}/{domainId}/{filename}",
        "path": str(path).replace("\\", "/"),
        "filename": filename,
        "contentType": content_type,
        "size": len(raw),
    }


# --- Helper Function สำหรับ Save File ---
# [u-80] - upload single base64 image ---to disk and return metadata]
# def upload_single_image(file: UploadFile , gallery_meta: dict, upload_dir: str, new_product_uid: str, domainId: str) -> dict:
#     saved_images_data = [] # เก็บข้อมูลเตรียมลง DB
#     # logger.info(f"🧨🧨🧨🧨🧨 gallery_meta {gallery_meta} ")
#     # logger.info(f"🎊🎊🎊🎊🎊 files {file} ")
    

#     created_file_paths = []
#     # Extract Metadata and Process Files
#     if file and gallery_meta:
       
#         file_extension = file.filename.split(".")[-1]
#         new_filename = f"{new_product_uid}_main.{file_extension}"
#         file_path = os.path.join(upload_dir, new_filename)
#         # print(f"Processing file {file.filename} -> {new_filename}")
#         # 1.1 ลอง Save ไฟล์
#         try:
#             with open(file_path, "wb") as buffer:
#                 shutil.copyfileobj(file.file, buffer)
            
#             # บันทึก path ไว้ ถ้าเกิด error ภายหลังจะได้ตามลบถูก
#             created_file_paths.append(file_path)

#             # logger.info(f"🎊🎊🎊🎊 created_file_paths  >>>>>>>>>>> {created_file_paths} ")

            
#         except Exception as file_err:
#             logger.error(f"Failed to save file {new_filename}: {file_err}")
#             raise Exception(f"File saving failed: {file_err}") # โยนไปให้ catch ใหญ่จัดการ Rollback

            
#         # 1.2 เตรียม Data สำหรับลง DB (ยังไม่ลงจริง)
#         record = {
#             "uid": str(uuid.uuid4()),
#             "productItemId": new_product_uid,
#             "filename": new_filename,
#             "getUrl": file_path,
#             "variantKey": gallery_meta.variantKey,
#             "variantValue": gallery_meta.variantValue,
#             "isMain": gallery_meta.isMain,
#             # ... fields อื่นๆ เช่น createBy, createTime ...
#         }
#         saved_images_data.append(record)


#     return {
#         "count": 1,
#         "metadataImage": saved_images_data,
#         "created_file_paths": created_file_paths
#     }




# [u-81] - upload multiple images with upload stream ---to disk and return metadata]
def upload_multiple_images(files: List[UploadFile] , gallery_meta_list: List[dict], upload_dir: str, new_product_uid: str, domainId: str) -> dict:
    saved_images_data = [] # เก็บข้อมูลเตรียมลง DB
    # logger.info(f"🧨🧨🧨🧨🧨 gallery_meta_list {gallery_meta_list} ")
    # logger.info(f"🎊🎊🎊🎊🎊 files {files} ")
    

    created_file_paths = []
    # Extract Metadata and Process Files
    if files and gallery_meta_list:
        logger.info(f"\nProcessing {len(files)} gallery files...\n")
        # เช็คความยาวก่อนเพื่อความชัวร์ (Optional log)
        # logger.info(f"Files count: {len(files)}, Meta count: {len(product_in.images_meta)}")
        for idx, (file, meta) in enumerate(zip(files, gallery_meta_list)):
            # logger.info(f"💚 💚 💚 💚 💚 files in  >>>>>>>>>>> {file.filename} ")
            file_extension = file.filename.split(".")[-1]
            new_filename = f"{str(uuid.uuid4())}_{idx}.{file_extension}"
            file_path = os.path.join(upload_dir, new_filename)


            # logger.info(f"\n\n🦑🦑🦑🦑🦑 new_filename >>>>>>>>>>> {new_filename} \n\n")
            # print(f"Processing file {file.filename} -> {new_filename}")
            # 1.1 ลอง Save ไฟล์
            try:
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # บันทึก path ไว้ ถ้าเกิด error ภายหลังจะได้ตามลบถูก
                created_file_paths.append(file_path)

                # logger.info(f"🎊🎊🎊🎊 created_file_paths  >>>>>>>>>>> {created_file_paths} ")
                # for cre in created_file_paths:
                #     logger.info(f"\n\n🪼🪼🪼🪼🪼 created_file_paths  >>>>>>>>>>> {json.dumps(cre, default=str, indent=4, ensure_ascii=False)} \n\n")
            
            except Exception as file_err:
                logger.error(f"Failed to save file {new_filename}: {file_err}")
                raise Exception(f"File saving failed: {file_err}") # โยนไปให้ catch ใหญ่จัดการ Rollback

            
            # 1.2 เตรียม Data สำหรับลง DB (ยังไม่ลงจริง)
            record = {
                "uid": str(uuid.uuid4()),
                "productId": new_product_uid,
                "domainId": domainId,
                "filename": new_filename,
                "getUrl": f"{PRODUCT_IMAGE_URL}/{domainId}/{new_filename}",
                "path": file_path,
                "variantKey": getattr(meta, "variantKey", None),
                "variantValue": getattr(meta, "variantValue", None),
                "isMain": getattr(meta, "isMain", False),
                "uploadingFilename" : file.filename,
                # ... fields อื่นๆ เช่น createBy, createTime ...
            }
            saved_images_data.append(record)


    return {
        "count": len(saved_images_data),
        "metadataImage": saved_images_data,
        "created_file_paths": created_file_paths
    }






















































