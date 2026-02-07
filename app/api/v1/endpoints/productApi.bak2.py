from typing import List, Optional , Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, BackgroundTasks, File,Form


from repo import  userRepo, authRepo, fileRepo

##### BEGIN : DATABSE #####

from models import  schemas, user, product
# from loguru import logger
from pydantic import BaseModel, Json ,ValidationError, validator, Field, EmailStr
from database.mongodb  import AsyncIOMotorClient, get_database

# from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from core.config  import PRODUCT_UPLOAD_ROOT
import shutil

from utils import util
from utils.datetime_util  import now

import math
import uuid ,base64, re
from pathlib import Path
from datetime import datetime
import os 
import logging

router = APIRouter()

import logging
logger = logging.getLogger("salepie.product")


# # [pd-1][v2] Add new Item in shop 
# @router.post("/add-a-new-item-in-shop", tags=["product"])
# async def addANewItemInShop(
#     productIn: product.ProductItemIn,  
#     db: AsyncIOMotorClient = Depends(get_database),  
#     currentUser: user.UserDb = Depends(authRepo.get_current_active_user)
# ):
#     if not productIn:
#         raise HTTPException(status_code=400, detail="No input product data")

#     # 1. Prepare Data
#     current_time = now()
#     prod_uid = productIn.uid or str(util.getUuid())
#     domain_id = currentUser.domainId
    
#     # ตัวแปรสำหรับ Tracking เพื่อทำ Rollback
#     created_file_paths = []
#     inserted_product_id = None
#     inserted_image_ids = []

#     try:
#         # ==========================================
#         # STEP 1: Process Files (Save to Storage)
#         # ==========================================
        
#         # 1.1 Handle Main Image
#         main_image_meta = None
#         if productIn.mainImage and productIn.mainImage.dataUrl:
#             try:
#                 main_file_info = util.process_single_image(productIn.mainImage.dataUrl, domain_id)
#                 created_file_paths.append(main_file_info["path"]) # Track file
                
#                 # Update ข้อมูล Main Image สำหรับ ProductItem (Snapshot)
#                 main_image_meta = productIn.mainImage.model_dump()
#                 main_image_meta.update({
#                     "getUrl": main_file_info["getUrl"],
#                     "imageId": main_file_info["imageId"],
#                     "filename": main_file_info["filename"],
#                     "dataUrl": None # ไม่เก็บ base64 ลง DB เพื่อประหยัดที่
#                 })
#             except Exception as e:
#                 logger.exception("save image error")  
#                 raise HTTPException(status_code=400, detail=f"🪲🪲🪲 Error saving main image: {str(e)}")

#         # 1.2 Handle Gallery Images (List)
#         gallery_image_docs = []
        
#         # ใส่ Main Image ลงไปใน ProductImage Collection ด้วย
#         if main_image_meta:
#              img_doc = product.ProductImage(
#                 uid=main_image_meta["imageId"],
#                 domainId=domain_id,
#                 productItemId=prod_uid,
#                 seq=0,
#                 getUrl=main_image_meta["getUrl"],
#                 filename=main_image_meta["filename"],
#                 description=main_image_meta.get("description"),
#                 isMain=True,
#                 createBy=currentUser.email,
#                 createDateTime=current_time,
#                 updateBy=currentUser.email,
#                 updateDateTime=current_time
#             ).model_dump()
#              gallery_image_docs.append(img_doc)

#         # Loop รูปอื่นๆ ใน List
#         if productIn.images:
#             for idx, img_in in enumerate(productIn.images, start=1):
#                 if img_in.dataUrl:
#                     try:
#                         file_info = util.process_single_image(img_in.dataUrl, domain_id)
#                         created_file_paths.append(file_info["path"]) # Track file

#                         img_doc = product.ProductImage(
#                             uid=str(util.getUuid()),
#                             domainId=domain_id,
#                             productItemId=prod_uid,
#                             seq=img_in.seq if img_in.seq is not None else idx,
#                             getUrl=file_info["getUrl"],
#                             filename=file_info["filename"],
#                             description=img_in.description,
#                             isMain=False,
#                             createBy=currentUser.email,
#                             createDateTime=current_time,
#                             updateBy=currentUser.email,
#                             updateDateTime=current_time
#                         ).model_dump()
#                         gallery_image_docs.append(img_doc)
#                     except Exception as e:
#                         raise HTTPException(status_code=400, detail=f"Error saving gallery image {idx}: {str(e)}")

#         # ==========================================
#         # STEP 2: Database Operations
#         # ==========================================
        
#         # 2.1 Prepare Product Item Data
#         prod_data = productIn.model_dump()
#         prod_data.update({
#             "uid": prod_uid,
#             "domainId": domain_id,
#             "createBy": currentUser.email,
#             "createDateTime": current_time,
#             "updateBy": currentUser.email,
#             "updateDateTime": current_time,
#             "mainImage": main_image_meta, # เก็บแค่ Url ที่ process แล้ว
#             "images": [
                
#             ] # เราแยกไปเก็บ collection productImage แล้ว ตรงนี้อาจจะเว้นว่าง หรือเก็บ snapshot บางส่วน
#         })

#         # 2.2 Insert ProductItem
#         res_prod = await db["salepiev1"]["productItem"].insert_one(prod_data)
#         if not res_prod.acknowledged:
#             raise Exception("Failed to insert product item")
        
#         inserted_product_id = res_prod.inserted_id
#         # print("🎊🎊🎊🎊🎊 inserted_product_id",res_prod.inserted_id)

#         # 2.3 Insert ProductImages (Bulk Insert)
#         if gallery_image_docs:
#             res_imgs = await db["salepiev1"]["productImage"].insert_many(gallery_image_docs)
#             if not res_imgs.acknowledged:
#                 raise Exception("Failed to insert product images")
#             inserted_image_ids = res_imgs.inserted_ids

#         # ==========================================
#         # STEP 3: Success Response
#         # ==========================================
        
#         # ดึงข้อมูลที่เพิ่ง Save ออกมา return (เพื่อให้ได้ข้อมูลครบถ้วน)
#         saved_product = await db["salepiev1"]["productItem"].find_one({"uid": prod_uid})



#         productOut = product.ProductItemOut(**saved_product)
        
#         return {
#             "success": True, 
#             "data": productOut,
#             "message": f"Product created with {len(gallery_image_docs)} images."
#         }

#     except Exception as e:
#         # ==========================================
#         # ROLLBACK MECHANISM (Clean up mess)
#         # ==========================================
#         print(f"💔💔💔 Error occurred: {e}. ⌛️⌛️⌛️Initiating Rollback...")
#         logger.exception(f"⌛️⌛️⌛️ Error occurred: {e}. Initiating Rollback...")

#         # 1. Delete Files created
#         for fpath in created_file_paths:
#             try:
#                 if os.path.exists(fpath):
#                     os.remove(fpath)
#                     print(f"Rollback: Deleted file {fpath}")
#             except Exception as cleanup_err:
#                 print(f"Rollback Error (File): {cleanup_err}")

#         # 2. Delete Product Item (if inserted)
#         if inserted_product_id:
#             try:
#                 await db["salepiev1"]["productItem"].delete_one({"uid": prod_uid})
#                 print(f"Rollback: Deleted product {inserted_product_id}")
#             except Exception as cleanup_err:
#                 print(f"Rollback Error (Product DB): {cleanup_err}")

#         # 3. Delete Product Images (if inserted)
#         if inserted_image_ids:
#             try:
#                 await db["salepiev1"]["productImage"].delete_many({"uid": {"$in": inserted_image_ids}})
#                 print(f"Rollback: Deleted {len(inserted_image_ids)} images")
#             except Exception as cleanup_err:
#                 print(f"Rollback Error (Image DB): {cleanup_err}")

#         # Re-raise the exception to client
#         # raise HTTPException(status_code=500, detail=f"Operation failed and rolled back: {str(e)}")
       
#         raise HTTPException(status_code=500, detail="Something went wrong, system rolled back") from e



# 1. สร้าง Model สำหรับรับ Metadata ของรูป (ไม่ต้องมี dataUrl แล้ว)
class ProductImageMeta(BaseModel):
    seq: Optional[int] = 0
    isMain: bool = False             
    description: Optional[str] = None
    variantKey: Optional[str] = None   # ยังรับค่า variant ได้เหมือนเดิม
    variantValue: Optional[str] = None

# 2. Model สำหรับรับข้อมูลสินค้า (ตัด mainImageDataUrl และเปลี่ยน type ของ images)
class ProductItemForm(BaseModel):
    name: str
    code: Optional[str] = None
    # ... field อื่นๆ ...
    # รับ list ของ metadata แทน
    images_meta: Optional[List[ProductImageMeta]] = []


# [pd-1][v3] Add new Item in shop 
# @router.post("/product-with-image", tags=["product"])
# async def create_product_with_upload(
#     # ส่วนที่ 1: รับ JSON String แล้วแปลงเป็น Pydantic Model ทันที
#     # ✅ เปลี่ยนเป็นรับ String ธรรมดา
#     product_data: str = Form(...),
    
#     # ส่วนที่ 2: รับไฟล์รูปภาพทั้งหมดเป็น List
#     files: List[UploadFile] = File(default=None),
#     currentUser: user.UserDb = Depends(authRepo.get_current_active_user)
# ):
#     """
#     Client ต้องส่ง:
#     1. form-field ชื่อ 'product_data': ค่าเป็น JSON String เช่น {"name": "Test", "images_meta": [{"variantKey": "Color"}]}
#     2. form-field ชื่อ 'files': เลือกไฟล์รูปภาพ (Multiple files)
#     """

#     logger.info(f"💻💻💻💻💻Creating product for user: {product_data}")

#     try:
#         # ถ้าใช้ Pydantic V2
#         product_form = ProductItemForm.model_validate_json(product_data)
        
#         # ถ้าใช้ Pydantic V1 (เผื่อใครใช้ version เก่า)
#         # product_form = ProductItemForm.parse_raw(product_data)
        
#     except ValidationError as e:
#         raise HTTPException(status_code=422, detail=e.errors())
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")

#     # Validation: เช็คว่าจำนวนรูปกับ Metadata ตรงกันไหม (Optional)
#     if product_form.images_meta and files:
#         if len(product_form.images_meta) != len(files):
#             raise HTTPException(status_code=400, detail="จำนวนรูปภาพกับข้อมูล Metadata ไม่ตรงกัน")

#     # --- 1. Save ข้อมูล Product ลง DB (จำลอง) ---
#     new_product_uid = str(uuid.uuid4())
#     print(f"Creating Product: {product_form.name} (ID: {new_product_uid})")
    
#     saved_images = []

#     # --- 2. Loop จัดการรูปภาพ ---
#     if files:
#         # ใช้ zip เพื่อจับคู่ ไฟล์ที่ 1 กับ metadata ตัวที่ 1
#         # สมมติว่า Client เรียงลำดับมาตรงกัน
#         for idx, (file, meta) in enumerate(zip(files, product_form.images_meta)):
            
#             # สร้างชื่อไฟล์ใหม่
#             file_extension = file.filename.split(".")[-1]
#             new_filename = f"{new_product_uid}_{idx}.{file_extension}"
#             file_path = os.path.join(PRODUCT_UPLOAD_ROOT, currentUser.domainId , new_filename)
            
#             # Save file ลง Disk (แบบ Stream ไม่กิน RAM)
#             with open(file_path, "wb") as buffer: 
#                 shutil.copyfileobj(file.file, buffer)
                
#             # สร้าง Object ProductImage เพื่อเตรียมลง DB
#             image_record = {
#                 "uid": str(uuid.uuid4()),
#                 "productItemId": new_product_uid,
#                 "filename": new_filename,
#                 "path": file_path,
#                 "variantKey": meta.variantKey,     # ✅ ได้ค่าจาก JSON
#                 "variantValue": meta.variantValue, # ✅ ได้ค่าจาก JSON
#                 "isMain": meta.isMain
#             }
#             saved_images.append(image_record)
            
#             print(f"Saved Image: {new_filename} | Variant: {meta.variantKey}={meta.variantValue}")

#     return {
#         "status": "success",
#         "product_uid": new_product_uid,
#         "saved_images_count": len(saved_images),
#         "data": saved_images
#     }


# [pd-1][v4] Add new Item in shop 
@router.post("/product-with-image", tags=["product"])
async def create_product_with_upload(
    product_data: str = Form(...),
    files: List[UploadFile] = File(default=None),
    db: AsyncIOMotorClient = Depends(get_database),  # ต้อง Inject DB เข้ามาเพื่อ save
    currentUser: user.UserDb = Depends(authRepo.get_current_active_user)
):
    # --- 1. Validate JSON Data ---
    # try:
    productIn = product.ProductItemIn.model_validate_json(product_data)
   
    if productIn.images and files:
        if len(productIn.images) != len(files):
            raise HTTPException(status_code=400, detail="จำนวนรูปภาพกับข้อมูล Metadata ไม่ตรงกัน")

    # ตัวแปรสำหรับ Rollback (เก็บรายชื่อไฟล์ที่สร้างไปแล้ว)
    created_file_paths = []

    # 1. Prepare Data
    current_time = now()
    prod_uid =  str(util.getUuid())
    domain_id = currentUser.domainId
    
    # ตัวแปรสำหรับ Tracking เพื่อทำ Rollback
    created_file_paths = []
    inserted_product_id = None
    inserted_image_ids = []
    
    # ตัวแปรเก็บ ID เพื่อลบ DB กรณีพลาด
    inserted_product_uid = None 

    new_product_uid = str(uuid.uuid4())
    
    # กำหนด Path folder ล่วงหน้า
    upload_dir = os.path.join(PRODUCT_UPLOAD_ROOT, currentUser.domainId)
    os.makedirs(upload_dir, exist_ok=True)

    try:
        # =========================================================
        # STEP 1: Process & Save Files First (บันทึกไฟล์ก่อน)
        # =========================================================
        # เหตุผล: ถ้า save ไฟล์ไม่ผ่าน เราแค่ไม่ต้องบันทึก DB (ไม่เกิดขยะใน DB)
        # แต่ถ้าบันทึก DB ก่อน แล้ว save ไฟล์ไม่ผ่าน เราต้องไปตามลบ DB

        # 1.1 Handle Main Image
        main_image_meta = None
        if productIn.mainImage and productIn.mainImage.dataUrl:
            try:
                main_file_info = util.process_single_image(productIn.mainImage.dataUrl, domain_id)
                created_file_paths.append(main_file_info["path"]) # Track file
                
                # Update ข้อมูล Main Image สำหรับ ProductItem (Snapshot)
                main_image_meta = productIn.mainImage.model_dump()
                main_image_meta.update({
                    "getUrl": main_file_info["getUrl"],
                    "imageId": main_file_info["imageId"],
                    "filename": main_file_info["filename"],
                    "dataUrl": None # ไม่เก็บ base64 ลง DB เพื่อประหยัดที่
                })

                # 📌 สร้าง Doc สำหรับ Main Image เตรียมลง Collection productImage
                main_img_doc = {
                    "uid": main_image_meta["imageId"], # หรือ str(uuid.uuid4())
                    "domainId": domain_id,
                    "productItemId": new_product_uid,  # Link กับ Product ใหม่
                    "seq": 0,
                    "getUrl": main_file_info["getUrl"],
                    "filename": main_file_info["filename"],
                    "path": main_file_info["path"], # ควรเก็บ path ด้วยเผื่อลบ
                    "description": main_image_meta.get("description"),
                    "isMain": True,
                    "createBy": currentUser.email,
                    "createDateTime": current_time,
                    "updateBy": currentUser.email,
                    "updateDateTime": current_time
                }
                # ✅ ใส่ Main Image เข้า List รวม
                all_images_to_save.append(main_img_doc)
                logger.info("✅ Main image processed and added to save list.")
            except Exception as e:
                logger.exception("save image error")  
                raise HTTPException(status_code=400, detail=f"🪲🪲🪲 Error saving main image: {str(e)}")

        # 1.2 Handle Gallery Images (จาก Files Upload)
        # Check List Length
        # ตรวจสอบว่า field ใน model ชื่อ 'images' หรือ 'images_meta' ต้องใช้ให้ตรงกัน
        gallery_meta_list = productIn.images if hasattr(productIn, 'images') else []

        logger.info(f"🩷🩷🩷🩷 gallery_meta_list before  >>>>>>>>>>> {gallery_meta_list} ")
        
        if gallery_meta_list and files:
            if len(gallery_meta_list) != len(files):
                raise HTTPException(status_code=400, detail=f"Mismatch: {len(gallery_meta_list)} meta items vs {len(files)} files")

        
        # 📌 สร้างตัวแปรเดียวสำหรับเก็บรูป *ทั้งหมด* (Main + Gallery) เพื่อเตรียม Save
        all_images_to_save = []

        current_time = now()
        prod_uid = str(util.getUuid()) # หรือใช้ product_in.uid ถ้ามี
        domain_id = currentUser.domainId
        new_product_uid = str(uuid.uuid4())
    
        upload_dir = os.path.join(PRODUCT_UPLOAD_ROOT, currentUser.domainId)
        os.makedirs(upload_dir, exist_ok=True)
        
        # ตัวแปรสำหรับ Rollback
        inserted_product_uid = None
        
        
        # 1.2 Handle Gallery Images (List)# ใส่ Main Image ลงไปใน ProductImage Collection ด้วย
        # =========================================================
        # STEP 1.2: Process Image collection
        # =========================================================
        gallery_image_docs = []
        if main_image_meta:
             img_doc = product.ProductImage(
                uid=main_image_meta["imageId"],
                domainId=domain_id,
                productItemId=prod_uid,
                seq=0,
                getUrl=main_image_meta["getUrl"],
                filename=main_image_meta["filename"],
                description=main_image_meta.get("description"),
                isMain=True,
                createBy=currentUser.email,
                createDateTime=current_time,
                updateBy=currentUser.email,
                updateDateTime=current_time
            ).model_dump()
             gallery_image_docs.append(img_doc)
        
        saved_images_data = [] # เก็บข้อมูลเตรียมลง DB
        created_file_paths = []


        # logger.info(f"🧨🧨🧨🧨🧨 gallery_meta_list {gallery_meta_list} ")
        # logger.info(f"🎊🎊🎊🎊🎊 files {files} ")


        uploaded_result = util.upload_multiple_images(files, gallery_meta_list, upload_dir, new_product_uid)
        saved_images_data = uploaded_result["metadataImage"]
        
        # ไว้ลบไฟล์ตอน rollback
        created_file_paths = uploaded_result["created_file_paths"]

        logger.info(f"✅ uploaded_result  >>>>>>>>>>> {uploaded_result} ")
        # Extract Metadata and Process Files
        # if files and gallery_meta_list:
        #     logger.info(f"Processing {len(files)} gallery files...")
        #     # เช็คความยาวก่อนเพื่อความชัวร์ (Optional log)
        #     # logger.info(f"Files count: {len(files)}, Meta count: {len(product_in.images_meta)}")
        #     for idx, (file, meta) in enumerate(zip(files, gallery_meta_list)):
        #         logger.info(f"💚 💚 💚 💚 💚 files in  >>>>>>>>>>> {file.filename} ")
        #         file_extension = file.filename.split(".")[-1]
        #         new_filename = f"{new_product_uid}_{idx}.{file_extension}"
        #         file_path = os.path.join(upload_dir, new_filename)
        #         print(f"Processing file {file.filename} -> {new_filename}")
        #         # 1.1 ลอง Save ไฟล์
        #         try:
        #             with open(file_path, "wb") as buffer:
        #                 shutil.copyfileobj(file.file, buffer)
                    
        #             # บันทึก path ไว้ ถ้าเกิด error ภายหลังจะได้ตามลบถูก
        #             created_file_paths.append(file_path)

        #             logger.info(f"🎊🎊🎊🎊 created_file_paths  >>>>>>>>>>> {created_file_paths} ")

                    
        #         except Exception as file_err:
        #             logger.error(f"Failed to save file {new_filename}: {file_err}")
        #             raise Exception(f"File saving failed: {file_err}") # โยนไปให้ catch ใหญ่จัดการ Rollback

        #         # 1.2 เตรียม Data สำหรับลง DB (ยังไม่ลงจริง)
        #         image_record = {
        #             "uid": str(uuid.uuid4()),
        #             "productItemId": new_product_uid,
        #             "filename": new_filename,
        #             "getUrl": file_path,
        #             "variantKey": meta.variantKey,
        #             "variantValue": meta.variantValue,
        #             "isMain": meta.isMain,
        #             # ... fields อื่นๆ เช่น createBy, createTime ...
        #         }
        #         saved_images_data.append(image_record)

            # logger.info(f"🎊🎊🎊🎊 saved_images_data APPENDD!!!!  >>>>>>>>>>> {saved_images_data} ")

        # =========================================================
        # STEP 2: Database Operations (บันทึก DB)
        # =========================================================
        
        # 2.1 เตรียม Product Data
        product_doc = productIn.model_dump()
        product_doc.update({
            "uid": prod_uid,
            "domainId": domain_id,
            "createBy": currentUser.email,
            "createDateTime": current_time,
            "updateBy": currentUser.email,
            "updateDateTime": current_time,
            "mainImage": main_image_meta, # เก็บแค่ Url ที่ process แล้ว
            "images": [
                
            ] # เราแยกไปเก็บ collection productImage แล้ว ตรงนี้อาจจะเว้นว่าง หรือเก็บ snapshot บางส่วน
        })
        # ... fields อื่นๆ ...

        # --- เริ่ม Transaction (ถ้า MongoDB รองรับ) หรือ Sequence ---
        # กรณีนี้เขียนแบบ Sequence ปกติ แต่มี Rollback ใน except
        
        # Insert Product
        res_product = await db["salepiev1"]["productItem"].insert_one(product_doc)
        if not res_product.acknowledged:
             raise Exception("Failed to insert productItem")
        
        inserted_product_uid = res_product.inserted_id # Mark ว่าลง DB แล้ว


        # logger.info(f"✅ saved_images_data  >>>>>>>>>>> {saved_images_data} ")
        # Insert Images (ถ้ามี)
        if saved_images_data:
            res_images = await db["salepiev1"]["productImage"].insert_many(saved_images_data)
            if not res_images.acknowledged:
                raise Exception("Failed to insert productImages")
            
            # ✅ แก้ไขตรงนี้: วนลูปเอา _id ออกจาก list ก่อน return
            for img in saved_images_data:
                if "_id" in img:
                    img.pop("_id") 
                    # หรือถ้าอยากส่งกลับไปด้วยให้แปลงเป็น str: 
                    # img["_id"] = str(img["_id"])

        logger.info(f"✅ Transaction Complete: Product {new_product_uid} created.")
        logger.info(f"✅ Response: Product {res_product} created.")

        # ==========================================
        # STEP 3: Success Response
        # ==========================================
        
        # ดึงข้อมูลที่เพิ่ง Save ออกมา return (เพื่อให้ได้ข้อมูลครบถ้วน)
        saved_product = await db["salepiev1"]["productItem"].find_one({"uid": prod_uid})
        productOut = product.ProductItemOut(**saved_product)

        return {
            "status": "success",
            "data": productOut,
            "saveImageCount": len(saved_images_data),
            "message": f"Product created with {len(saved_images_data)} images."
        }

    except Exception as e:
        # =========================================================
        # 🛑 ROLLBACK ZONE: ทำความสะอาดเมื่อเกิด Error
        # =========================================================
        logger.error(f"❌ Error occurred: {str(e)}. Initiating Rollback...")
        
        # 1. ลบไฟล์ทั้งหมดที่เพิ่งสร้างไป
        for path in created_file_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    logger.info(f"Rollback: Deleted file {path}")
                except OSError as os_err:
                    logger.error(f"Rollback failed for file {path}: {os_err}")

        # 2. ลบข้อมูลใน DB (ถ้าถูก insert ไปแล้ว)
        if inserted_product_uid:
            try:
                # ลบ Product
                await db["salepiev1"]["productItem"].delete_one({"uid": inserted_product_uid})
                # ลบ Images (ใช้ productItemId ลบทีเดียวเกลี้ยง)
                await db["salepiev1"]["productImage"].delete_many({"productItemId": inserted_product_uid})
                logger.info(f"Rollback: Deleted DB records for {inserted_product_uid}")
            except Exception as db_err:
                logger.critical(f"Rollback DB failed! Data might be inconsistent: {db_err}")

        # ส่ง Error กลับไปหา Client
        raise HTTPException(status_code=500, detail=f"Operation failed: {str(e)}")



# # [pd-1] Add new Item in shop 
# @router.post("/add-a-new-item-in-shop",  tags=["product"])
# async def addANewItemInShop(
#     productIn: product.ProductItemIn,  
#     db: AsyncIOMotorClient =  Depends(get_database),  
#     currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
    
#     # print(f" **************** productIn>>> ",productIn)

#     # print(f" **************** procurrentUser ductIn>>> ",currentUser.email)
#     if not productIn:
#         raise HTTPException(status_code=400, detail="No input product data")
    
    
#     # 1. Prepare Data
#     current_time = now()
#     prod_uid = productIn.uid or str(util.getUuid())
#     domain_id = currentUser.domainId
    
#     # ตัวแปรสำหรับ Tracking เพื่อทำ Rollback
#     created_file_paths = []
#     inserted_product_id = None
#     inserted_image_ids = []

    

   
#     data = productIn.model_dump()

#     # ✅ เติม uid + timestamps ที่ DB model ต้องมี
#     data["uid"] = data.get("uid") or str(util.getUuid())
#     data["createBy"] = currentUser.email
#     data["createDateTime"] = data.get("createDateTime") or now()
#     # return v if v is not None else now()
#     data["domainId"] = currentUser.domainId
#     data["updateBy"] = currentUser.email
#     data["updateDateTime"] = now()

    
    

#     # dbuser.change_password(user.password)

#     # ✅ ถ้ามีรูป mainImageDataUrl -> เซฟไฟล์ แล้วใส่ URL ลง mainImage
#     mainImage = data.get("mainImage")  # เอาออกจาก payload ก่อนลง DB
#     main_data_url = mainImage["dataUrl"] if mainImage else None
#     if main_data_url:
#         meta = util.save_product_data_url_image(main_data_url, data["domainId"])
#         data["mainImage"] = meta         # ใช้แสดงผลหน้าเว็บ
#         # data["mainImage"] = meta                # (optional) เก็บ metadata เพิ่มได้
#     productDb = product.ProductItemDB(**data)

#     print(f" **************** productDb.createBy >>> ",productDb.createBy)
#     print(f" **************** productDb.createBy >>> ",productDb.createBy)
#     row = await db["salepiev1"]["productItem"].insert_one(productDb.model_dump())

#     productOut = product.ProductItemOut(**productDb.model_dump())  


#     return {"success": True,
#             "data": productOut
#           } 
 

# # [u-4]
# @router.get("/get-user-by-id/{uid}",  tags=["user"] )
# async def getUserByID( uid:str,   db: AsyncIOMotorClient =  Depends(get_database),  currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
   

#     # print(f" **************** current user >>> ",currentUser)

#     if uid is None or uid == "":
#             raise HTTPException(status_code=400, detail="uid is required")
    
#     aUser = await db["salepiev1"]["user"].find_one({ "uid" : uid , "deleted": { "$ne": True } , "domainId" : currentUser.domainId })

#     if aUser is None:
#         raise HTTPException(status_code=404, detail="User not found")

#     try:
#         userOut =  user.UserOut(**aUser)
#     except:
#         raise HTTPException(status_code=500, detail="Data Converting Error")

#     return userOut


# # [u-5] get user list with pagination
# @router.get("/get-user-list-in-domain",  tags=["user"] )
# async def getUserListInDomain(
#     db: AsyncIOMotorClient =  Depends(get_database),  
#     currentUser  : user.UserDb = Depends(authRepo.get_current_active_user),
#     page: int = Query(1, ge=1),  # Default page = 1
#     page_size: int = Query(10, ge=1, le=100),  # Default page_size = 10
#     q: Optional[str] = Query(None),
#     itemStatus: Optional[str] = Query(None),
#     roles: Optional[List[str]] = Query(None),
#     sortBy: Optional[str] = Query(None)
#     ):

#     # ============================================
#     #  Begin: Variable preparation
#     # ============================================
#     criteria = {}
    

#     print(f"roles >>>. {roles}")
    
#     start = (page - 1) * page_size
#     end = start + page_size
    
    
#     if q:
#         criteria["textSearch"] = q
#     else:
#         criteria["textSearch"] = ""
        
#     if itemStatus:
#         criteria["itemStatus"] = itemStatus

#     if sortBy:
#         sorting = sortBy

#     # ============================================
#     #  End: Variable preparation
#     # ============================================
   

#     rows = []

#     query = {
#                     "domainId": currentUser.domainId,
#                     "deleted": { "$ne": True },
#                     "$or": [
#                         { "email": { "$regex": criteria["textSearch"], "$options": "i" }},
#                         { "firstName": { "$regex": criteria["textSearch"], "$options": "i" }},
#                         { "lastName": { "$regex": criteria["textSearch"], "$options": "i" }},
#                         { "description": { "$regex": criteria["textSearch"], "$options": "i" }}
#                     ]
#                 }
    
#     # ++++++ เพิ่มส่วนนี้ครับ ++++++
#     if roles:
#         # $in จะหาว่าใน DB (ที่เป็น array) มีค่าใดค่าหนึ่งตรงกับใน input list หรือไม่
#         query["roles"] = { "$in": roles }
#     # +++++++++++++++++++++++++++

#     # นับจำนวนทั้งหมดก่อน (เพื่อให้ได้ totalItems ที่ถูกต้องตาม Filter)
#     totalItems =  await db["salepiev1"]["user"].count_documents(query)

#     # Query ข้อมูลตามหน้า
#     cursor = db["salepiev1"]["user"].find(query).sort("createDateTime", -1)
    
#     # Apply Pagination ในระดับ Database (เร็วกว่าและประหยัด Ram กว่า)
#     cursor.skip(start).limit(page_size)

#     # 3. ดึงข้อมูลจริง (*** ต้อง await ***)
#     rows = await cursor.to_list(length=page_size)

#     # resp =   [user.UserOut(**row) async for row in rows]
#     resp = [user.UserOut(**row) for row in rows]

    
#     if not resp:
#         return {
#             "success": True,
#             "page": 1,
#             "pageSize": 10,
#             "totalItems": 0,
#             "totalPages": 1,
#             "data": [],
#         } 
#         # raise HTTPException(
#         #           status_code=404, detail="Not Found Users"
#         #   )
    

#     # data = resp[start:end]
#     # ไม่ต้อง slice resp[start:end] อีกแล้ว เพราะ resp คือข้อมูลของ page นั้นๆ แล้ว
#     data = resp
   

#     return {
#         "success": True,
#         "page": page,
#         "pageSize": page_size,
#         "totalItems": totalItems,
#         "totalPages": math.ceil(totalItems / page_size),
#         "data": data,
#     }   


# # [u-7] Change user active status  
# @router.post("/change-user-active",  tags=["user"] )
# async def changeUserStatus( activeForm : user.ActiveForm,  db: AsyncIOMotorClient =  Depends(get_database),  currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
#     print(f"searchForm >>> ",activeForm.uid)
#     try:
#         row = await db["salepiev1"]["user"].find_one({ "uid" : activeForm.uid })
#         userDb =   user.UserDb(**row) 
#     except:
#         raise HTTPException(status_code=400, detail="Unable to get user")
    
#     userDb.isActive = activeForm.isActive
#     edit = await db["salepiev1"]["user"].update_one({"uid": activeForm.uid}, {'$set': userDb.model_dump() })

#     return {
#         "success": True
#     }


# # [u-6] Edit my profile
# @router.post("/edit-my-profile",  tags=["user"] )
# async def editMyProfile( 
#             editForm : user.UserEditProfile,  
#             db: AsyncIOMotorClient =  Depends(get_database),  
#             currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
#     # print(f"searchForm >>> ",searchForm.uid)

#     try:
#         row = await db["salepiev1"]["user"].find_one({ "uid" : currentUser.uid })
#         userDb =   user.UserDb(**row) 
#     except:
#         raise HTTPException(status_code=400, detail="Unable to get user")
    
#     userDb.firstName = editForm.firstName
#     userDb.lastName  = editForm.lastName
#     userDb.address   = editForm.address
#     userDb.phone     = editForm.phone
#     userDb.phone     = editForm.phone
#     userDb.isActive  = editForm.isActive
#     userDb.roles     = editForm.roles
#     userDb.status    = editForm.status
#     userDb.updateDateTime = datetime.now(),

#     # ---- handle images array ----
#     new_images = []

#     # print("editForm.images >>>>>>> {editForm.images}")

#     for idx, img in enumerate(editForm.images or []):
#         # ถ้าส่ง deleted มา → เก็บสถานะไว้ (ตามโครงสร้างคุณ)
#         print("* * * * *This is images ")
#         if img.deleted:
#             new_images.append({
#                 "seq": img.seq if img.seq is not None else idx,
#                 "deleted": True,
#             })
#             continue

#         if img.url:
#             saved = save_data_url_image(img.url, userDb.uid)
#             new_images.append({
#                 "seq": img.seq if img.seq is not None else idx,
#                 "deleted": False,
#                 **saved
#             })
#         else:
#             # ถ้าไม่มี dataUrl และไม่ deleted → ข้าม หรือจะ error ก็ได้
#             # raise HTTPException(400, "image missing dataUrl")
#             pass

#         # เลือกพฤติกรรม:
#         # (A) replace ทั้ง images
#         if new_images:
#             userDb.images = new_images
    
#     # userDb.admin = searchForm.admin
#     edit = await db["salepiev1"]["user"].update_one({"uid": currentUser.uid}, {'$set': userDb.model_dump() })
    
#     print (f"edit >>> ",edit.modified_count)
    
#     userOut = user.UserOut(**userDb.model_dump())


#     return{
#             "success": True,
#              "data": userOut
#            }



# # [u-3]
# @router.post("/delete-user/{userId}",  tags=["user"] )
# async def deleteUserInDomain( userId : str,  db: AsyncIOMotorClient =  Depends(get_database),  currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
#     print(f"userId >>> ",userId)
#     try:
#         result  = await db["salepiev1"]["user"].delete_one({ "uid" : userId })
       
#     except:
#         return{
#             "success": False,
#             "data": userOut
#         }
#     #     raise HTTPException(status_code=400, detail="Unable to delete user")
    
#     return "OK" # {"deleted_count": result.deleted_count}

# # [u-2]
# @router.post("/soft-delete/{userId}",  tags=["user"] )
# async def deleteUserInDomain( userId : str,  db: AsyncIOMotorClient =  Depends(get_database),  currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
#     # print(f"searchForm >>> ",userId)
#     row = await db["salepiev1"]["user"].find_one({ "uid" : userId })

#     if row is None:
#         raise HTTPException(status_code=404, detail="Not found user")

#     # try:
#     #     row = await db["salepiev1"]["user"].find_one({ "uid" : userId })
#     #     userDb =   user.UserDb(**row) 
#     # except:
#     #     raise HTTPException(status_code=400, detail="Not found user")
    
#     userDb =   user.UserDb(**row) 
#     userDb.deleted = True

#     try:
#         edit = await db["salepiev1"]["user"].update_one({"uid": userId}, {'$set': userDb.dict() })

#         # print(f"edit >>> ",edit)
       
#     except:
#         raise HTTPException(status_code=500, detail="Unable to delete user")
    
#     return "OK" # {"deleted_count": result.deleted_count}




# @router.post("/register",  tags=["user"] ,  response_model=user.UserUpdate)
# async def register_user(reguser: user.UserCreate,  db: AsyncIOMotorClient =  Depends(get_database)):
   
#     # logger.info(">>>>>>>>>>>> userReg  DB >>>>>>>>>>>>>>>>>>>>>")
#     try: 
#         userdb = await userRepo.createUser(db=db, create=reguser) 
#     except:
#         raise HTTPException(status_code=400, detail="Unable to save data to database")

#     return userdb

# USER_IMAGE_URL = "http://localhost:8000/static/uploads/user"
# UPLOAD_ROOT = Path("static/uploads/user")
# ALLOWED = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}
# MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5MB

# dataurl_re = re.compile(r"^data:(image\/(?:png|jpeg|webp));base64,(.+)$")

# def save_data_url_image(data_url: str, uid: str) -> dict:
#     m = dataurl_re.match(data_url or "")
#     if not m:
#         raise HTTPException(status_code=400, detail="Invalid image dataUrl")

#     content_type = m.group(1)
#     b64 = m.group(2)

#     raw = base64.b64decode(b64)
#     if len(raw) > MAX_IMAGE_BYTES:
#         raise HTTPException(status_code=400, detail="Image too large (max 5MB)")

#     user_dir = UPLOAD_ROOT / uid
#     user_dir.mkdir(parents=True, exist_ok=True)

#     ext = ALLOWED.get(content_type)
#     if not ext:
#         raise HTTPException(status_code=400, detail=f"Unsupported image type: {content_type}")

#     filename = f"staff_{uuid.uuid4().hex}{ext}"
#     path = user_dir / filename
#     path.write_bytes(raw)

#     return {
#         "getUrl" : f"{USER_IMAGE_URL}/{uid}/{filename}",
#         "path": str(path).replace("\\", "/"),
#         "filename": filename,
#         "contentType": content_type,
#         "size": len(raw),
#     }


# # [u-8] Edit my shop staff profile
# @router.post("/edit-staff-profile/{userId}",  tags=["user"] )
# async def editStaffProfile( 
#     userId : str, editForm : user.UserEditProfile,  
#     db: AsyncIOMotorClient =  Depends(get_database),  
#     currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
#     # print(f"editForm >>> ",editForm)

#     try:
#         row = await db["salepiev1"]["user"].find_one({ "domainId" : currentUser.domainId, "uid" : userId })
#         userDb =   user.UserDb(**row) 
#     except:
#         raise HTTPException(status_code=404, detail="Unable to get user")
    
#     userDb.firstName = editForm.firstName
#     userDb.lastName  = editForm.lastName
#     userDb.address   = editForm.address
#     userDb.phone     = editForm.phone
#     userDb.isActive  = editForm.isActive
#     userDb.roles     = editForm.roles
#     userDb.status    = editForm.status
#     userDb.updateDateTime = datetime.now()

#     # ---- handle images array ----
#     new_images = []

#     for idx, img in enumerate(editForm.images or []):
#         print(f"IMAGE ::: for loop ")
#         # ถ้าส่ง deleted มา → เก็บสถานะไว้ (ตามโครงสร้างคุณ)
#         if img.deleted:
#             new_images.append({
#                 "seq": img.seq if img.seq is not None else idx,
#                 "deleted": True,
#             })
#             continue
#         print(f"IMAGE ::: ON data Url")
#         if img.dataUrl:
#             print(f"IMAGE ::: img.dataUrl comes")
#             # ✅✅ 1. เพิ่ม Logic: ลบไฟล์เก่าทั้งหมดในโฟลเดอร์ของ User นี้ทิ้งก่อน
#             user_dir = UPLOAD_ROOT / userDb.uid
            
#             if user_dir.exists():
#                 for file_path in user_dir.iterdir():
#                     if file_path.is_file():
#                         try:
#                             file_path.unlink() # ลบไฟล์
#                             print(f"Deleted old file: {file_path}")
#                         except Exception as e:
#                             print(f"Error deleting {file_path}: {e}")
            
#             # ✅✅ 2. จากนั้นค่อยบันทึกไฟล์ใหม่
#             saved = save_data_url_image(img.dataUrl, userDb.uid)
#             print(f"* * * * *This is images {saved}")

#             new_images.append({
#                 "seq": img.seq if img.seq is not None else idx,
#                 "deleted": False,
#                 **saved
#             })

#             print(f"\n\n\n\n🧮🧮🧮🧮 new_images >>> ",new_images)
#         elif not img.getUrl :
#             print(f"IMAGE ::: not img.getUrl")
#             # ถ้าไม่มี dataUrl และไม่ deleted → ข้าม หรือจะ error ก็ได้
#             # raise HTTPException(400, "image missing dataUrl")
#             print(f"I NEED TO DELETE !!!! {userDb.email}'s image")
#             userDb.images = []
#             break
#         print(f"IMAGE ::: End each loop")
#         # เลือกพฤติกรรม:
#         # (A) replace ทั้ง images
#         if new_images:
#             userDb.images = new_images

#     print(f"IMAGE ::: End ALL loop")
    
    
#     # userDb.admin = searchForm.admin
#     edit = await db["salepiev1"]["user"].update_one({"uid": userId}, {'$set': userDb.model_dump() })
    
#     print (f"edit >>> ",edit.modified_count)
    
#     userOut = user.UserOut(**userDb.model_dump())


#     return{
#             "success": True,
#              "data": userOut
#            }

# # [u-1]
# @router.post("/create-staff",  tags=["user"])
# async def createStaff( userCreate: user.UserCreate,  db: AsyncIOMotorClient =  Depends(get_database), currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)):
#     # students = await retrieve_students()
#     # students = StudentSchema()
#     # students = await conn["alex_office_admin"]["movie"].find({})
#     userdb = await userRepo.getUserByEmail(db, userCreate.email)


#     if userdb:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
    
#     newuser = await userRepo.createUserInTheSameDomain(db=db, create=userCreate, currentUser=currentUser)

#     userOut = user.UserOut(**newuser.model_dump())
   
#     return {"success": True,
#              "data": userOut
#            }
#     # if row:
#     #     return Movie(**row)
    

# @router.post("/add-user-from-google",  tags=["user"])
# async def createUser( userCreate: user.SocialRegister,  db: AsyncIOMotorClient =  Depends(get_database)):
#     # students = await retrieve_students()
#     # students = StudentSchema()
#     # students = await conn["alex_office_admin"]["movie"].find({})
#     userdb = await userRepo.getUserByEmail(db, userCreate.email)


#     if userdb:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     userCreate.userType = "google"
    
#     newuser = await userRepo.addSocialUser(db=db, create=userCreate)
   
#     if newuser is None:
#         raise HTTPException(status_code=400, detail="Unable to add new user")
#     return newuser


# @router.put("/user",  tags=["user"])
# async def updateUser( updateUser: user.UserUpdate,  db: AsyncIOMotorClient =  Depends(get_database)):

#     # students = await retrieve_students()
#     # students = StudentSchema()
#     # students = await conn["alex_office_admin"]["movie"].find({})

#     # rows = await userRepo.create_user(userCreate)
#     updated = await userRepo.updateUser(db=db, update=updateUser)
   
#     # if row:
#     #     return Movie(**row)
  
#     return updated


# @router.post("/upload-image",  tags=["user"])
# async def image(image: UploadFile = File(...)):
#     with open("assets/images/user/destination.png", "wb") as buffer:
#         shutil.copyfileobj(image.file, buffer)
    
#     return {"filename": image.filename}



# @router.post("/send-email-text-template",  tags=["email"])
# def send_email_text_template():
#     smtp_server = "smtp.gmail.com"
#     port = 587  # For starttls
#     password = "Lll3ell-1234%"
#     sender_email = "v.blue.front1@gmail.com"
#     receiver_email = "belliecee@gmail.com"
#     message = MIMEMultipart("alternative")

#     message["Subject"] = "test with another lib"
#     message["From"] = sender_email
#     message["To"] = receiver_email
    
#     # text = """\
#     # Hi,
#     # How are you?
#     # Real Python has many great tutorials:
#     # www.realpython.com"""
#     html = """\
#     <html>
#                     <body style="margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, Helvetica, sans-serif;">
#                     <div style="width: 100%; background: #efefef; border-radius: 10px; padding: 10px;">
#                     <div style="margin: 0 auto; width: 90%; text-align: center;">
#                         <h1 style="background-color: rgba(0, 53, 102, 1); padding: 5px 10px; border-radius: 5px; color: white;">Subscription</h1>
#                         <div style="margin: 30px auto; background: white; width: 40%; border-radius: 10px; padding: 50px; text-align: center;">
#                         <h3 style="margin-bottom: 100px; font-size: 24px;">Bell</h3>
#                         <p style="margin-bottom: 30px;">Lorem ipsum dolor sit amet consectetur adipisicing elit. Eligendi, doloremque.</p>
#                         <a style="display: block; margin: 0 auto; border: none; background-color: rgba(255, 214, 10, 1); color: white; width: 200px; line-height: 24px; padding: 10px; font-size: 24px; border-radius: 10px; cursor: pointer; text-decoration: none;"
#                             href="https://fastapi.tiangolo.com/"
#                             target="_blank"
#                         >
#                             Let's Go
#                         </a>
#                         </div>
#                     </div>
#                     </div>
#                     </body>
#                     </html>
#     """


#     # Turn these into plain/html MIMEText objects
#     # part1 = MIMEText(text, "plain")
#     part2 = MIMEText(html, "html")


#     # Add HTML/plain-text parts to MIMEMultipart message
#     # The email client will try to render the last part first
#     # message.attach(part1)
#     message.attach(part2)
 
#     try:
#         context = ssl.create_default_context()
#         with smtplib.SMTP(smtp_server, port) as server:
#             server.ehlo()  # Can be omitted
#             server.starttls(context=context)
#             server.ehlo()  # Can be omitted
#             server.login(sender_email, password)
#             server.sendmail(sender_email, receiver_email, message.as_string())
#     except:
#         raise HTTPException(status_code=400, detail="Unable to send email")

    
#     return {"success": True}