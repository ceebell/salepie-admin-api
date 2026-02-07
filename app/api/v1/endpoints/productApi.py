from typing import List, Optional , Any, Dict,Tuple

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
import json

router = APIRouter()

import logging
logger = logging.getLogger("salepie.product")


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
    productForm = product.ProductFormCreate.model_validate_json(product_data)

    productIn = productForm.product
    variants = productForm.variants
    variant_images = []
    variant_images = productForm.images

    
   
    # if productIn.images and files:
    #     if len(productIn.images) != len(files):
    #         raise HTTPException(status_code=400, detail="จำนวนรูปภาพกับข้อมูล Metadata ไม่ตรงกัน")

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

    # new_product_uid = str(uuid.uuid4())
    
    # กำหนด Path folder ล่วงหน้า
    upload_dir = os.path.join(PRODUCT_UPLOAD_ROOT, currentUser.domainId)
    os.makedirs(upload_dir, exist_ok=True)

    # ดึง list ของ metadata รูปภาพออกมา (ต้องมั่นใจว่าลำดับตรงกับ files)
    # main_image_meta = productIn.mainImage if hasattr(productIn, 'mainImage') else None
    main_image_meta_list = productIn.images if hasattr(productIn, 'images') else None

    

    try:

        # =========================================================
        # STEP 1: Process ALL Files in ProductIn (Not including VARIANTS) 
        # (รวม Main และ Gallery ทีเดียว)
        # =========================================================
        saved_images_data = []
        
        if files and variant_images:
            # ใช้ Utility เดิมของคุณจัดการ upload และ map ข้อมูล
            # 1.1 Save multiple files in server and extract metadata 
            # Using [u-81] 
            uploaded_result = util.upload_multiple_images(files, variant_images, upload_dir, prod_uid, domain_id)
            
            # 1.2 Save image metadata
            saved_images_data = uploaded_result["metadataImage"]
            
            # 1.3 Keep path for rollback
            created_file_paths.append(uploaded_result["created_file_paths"]) # Track file

            # logger.info(f"\n\n✅✅✅ uploaded_result['metadataImage']  >>>>>>>>>>> {json.dumps(uploaded_result['metadataImage'], default=str, indent=4, ensure_ascii=False)} \n\n")
            # logger.info(f"\n\n✅✅✅ uploaded_result['created_file_paths']  >>>>>>>>>>> {json.dumps(uploaded_result['created_file_paths'], default=str, indent=4, ensure_ascii=False)} \n\n")
        
            # 1.4 save metadata to productImage collection
           
            if saved_images_data and len(saved_images_data) > 0:
                # Convert saved_images_data to ProductImage model
                productImageDb = [product.ProductImage(
                    **img,                           # 1. แตกข้อมูลเดิมออกมา
                    createBy=currentUser.email,      # 2. เพิ่ม createBy
                    updateBy=currentUser.email       # 3. เพิ่ม updateBy
                    ).model_dump() for img in saved_images_data]
        
                res_images = await db["salepiev1"]["productImage"].insert_many(productImageDb)
                
                if not res_images.acknowledged:
                    raise Exception("Failed to insert productImages")
                    
                # ✅ แก้ไขตรงนี้: วนลูปเอา _id ออกจาก list ก่อน return
                for img in saved_images_data:
                    if "_id" in img:
                        img.pop("_id") 
                        # หรือถ้าอยากส่งกลับไปด้วยให้แปลงเป็น str: 
                        # img["_id"] = str(img["_id"])

            # for im in  productImageList:
            #     logger.info(f"\n\n🎅🏻🎅🏻🎅🏻🎅🏻🎅🏻 productImageList  >>>>>>>>>>> {json.dumps(im.model_dump(), default=str, indent=4, ensure_ascii=False)} \n\n")

            
        # =========================================================
        # STEP 2.2 Save variant collection
        # =========================================================
        
        # 📌 สร้างตัวแปรเดียวสำหรับเก็บรูป *ทั้งหมด* (Main + Gallery) เพื่อเตรียม Save
        variant_image_list = []

        # 2.1 Loop for save image from VARIANTS
        for variant in variants:
            # logger.info(f"\n\n👑👑👑👑👑 variant  >>>>>>>>>>> {json.dumps(variant.model_dump(), default=str, indent=4, ensure_ascii=False)} \n\n")

            # 2.1 Prepareing Data for each variant
            new_variant_uid = str(util.getUuid()) # หรือใช้ product_in.uid ถ้ามี
            domain_id = currentUser.domainId
            # variant_images = variant.images
            

            # variant_result = util.upload_multiple_images(files, variant_images, upload_dir, str(util.getUuid()), domain_id)
            # variant_image_list.append(uploaded_result)

            # for res in  uploaded_result:
            # logger.info(f"\n\n🎅🏻🎅🏻🎅🏻🎅🏻🎅🏻 variant_result  >>>>>>>>>>> {json.dumps(variant_result, default=str, indent=4, ensure_ascii=False)} \n\n")

            # productImageList.append(variant_result)
        # =========================================================
        # STEP 3 Save variant collection
        # =========================================================
        
        # ตัวแปรสำหรับ Rollback ****
        inserted_product_uid = None
        saved_images_variant = []
        created_file_paths_variant = []

        # saved_images_variant = uploaded_result["metadataImage"]
        
        # # ไว้ลบไฟล์ตอน rollback
        # created_file_paths_variant = uploaded_result["created_file_paths"]

        # logger.info(f"🦄🦄🦄🦄🦄🦄 uploaded_result  >>>>>>>>>>> {saved_images_variant} ")
       
        # =========================================================
        # STEP 4: Database Operations (บันทึก DB)
        # =========================================================
        
        # 4.1 เตรียม Product Data
        productDb = productIn.model_dump()
        productDb.update({
            "uid": prod_uid,
            "domainId": domain_id,
            "createBy": currentUser.email,
            "createDateTime": current_time,
            "updateBy": currentUser.email,
            "updateDateTime": current_time,
            # "mainImage": main_image_meta, # เก็บแค่ Url ที่ process แล้ว
            "images": [] # เราแยกไปเก็บ collection productImage แล้ว ตรงนี้อาจจะเว้นว่าง หรือเก็บ snapshot บางส่วน
        })
        # ... fields อื่นๆ ...

        # --- เริ่ม Transaction (ถ้า MongoDB รองรับ) หรือ Sequence ---
        # กรณีนี้เขียนแบบ Sequence ปกติ แต่มี Rollback ใน except
        
        # 4.2 Insert Product  
        res_product = await db["salepiev1"]["product"].insert_one(productDb)
        if not res_product.acknowledged:
             raise Exception("Failed to insert productItem")

        # logger.info(f"\n\n✨✨✨✨✨✨ res_product.inserted_id   >>>>>>>>>>> {str(res_product.inserted_id)} \n\n")
        
        inserted_product_uid = res_product.inserted_id # Mark ว่าลง DB แล้ว


        # logger.info(f"✅ saved_images_data  >>>>>>>>>>> {saved_images_data} ")
        # Insert Images (ถ้ามี)
        

        # *** ไม่มีแล้ว
        # 4.3 Save ProductImage (Main + Gallery)
        # productImageList = util.upload_multiple_images(files, variant_images, upload_dir, str(util.getUuid()), domain_id)
        # if productImageList and len(productImageList) > 0:
        #     # Convert saved_images_data to ProductImage model
        #     productImageDb = [product.ProductImage(
        #         **img,                           # 1. แตกข้อมูลเดิมออกมา
        #         createBy=currentUser.email,      # 2. เพิ่ม createBy
        #         updateBy=currentUser.email       # 3. เพิ่ม updateBy
        #         ).model_dump() for img in productImageList]
            
        #     res_images = await db["salepiev1"]["productImage"].insert_many(productImageDb)
        #     if not res_images.acknowledged:
        #         raise Exception("Failed to insert productImages")
            
        #     # ✅ แก้ไขตรงนี้: วนลูปเอา _id ออกจาก list ก่อน return
        #     for img in saved_images_data:
        #         if "_id" in img:
        #             img.pop("_id") 
        #             # หรือถ้าอยากส่งกลับไปด้วยให้แปลงเป็น str: 
        #             # img["_id"] = str(img["_id"])


        # 4.4 Save ProductVariant
        if variants and len(variants) > 0:
            variantDbList = [product.ProductVariantDB(
                **variant.model_dump(),
                uid = util.getUuid(),
                domainId = domain_id,
                productId = prod_uid,
                createBy=currentUser.email,
                updateBy=currentUser.email,
                ).model_dump() for variant in variants]
            
            res_variant = await db["salepiev1"]["productVariant"].insert_many(variantDbList)
            if not res_variant.acknowledged:
                raise Exception("Failed to insert variants")
            
            # ✅ แก้ไขตรงนี้: วนลูปเอา _id ออกจาก list ก่อน return
            for variant in variants:
                if "_id" in variant:
                    variant.pop("_id") 
                    # หรือถ้าอยากส่งกลับไปด้วยให้แปลงเป็น str: 
                    # variant["_id"] = str(variant["_id"])

        # logger.info(f"✅ Transaction Complete: Product {new_product_uid} created.")
        # logger.info(f"✅ Response: Product {res_product} created.")

        # ==========================================
        # STEP 3: Success Response
        # ==========================================
        
        # ดึงข้อมูลที่เพิ่ง Save ออกมา return (เพื่อให้ได้ข้อมูลครบถ้วน)
        

        try:
            saved_product = await db["salepiev1"]["product"].find_one({"uid": prod_uid})

            saved_images = await db["salepiev1"]["productImage"].find_one({"uid": prod_uid})

            productOut = product.ProductOut(**saved_product)

        except Exception as err:
            logger.error(f"Error fetching saved product: {err}")
            raise HTTPException(status_code=500, detail="Error retrieving saved product data")


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
        logger.error(f"❌ Error occurred: Initiating Rollback... {str(e)}")
        
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



# [pd-2][v1] View a new Item in shop 
@router.post("/product-view/{productId}", tags=["product"])
async def product_view(
    productId: str ,
    db: AsyncIOMotorClient = Depends(get_database),  # ต้อง Inject DB เข้ามาเพื่อ save
    currentUser: user.UserDb = Depends(authRepo.get_current_active_user)):
    
    # 1. Prepare Scope (Shop ID)
    current_shop_id = currentUser.domainId

    # ==========================================
    # 2. Fetch Data (Parallel Fetching optional but recommended)
    # ==========================================
    
    # 2.1 Get Product
    product_doc = await db["salepiev1"]["product"].find_one({
        "uid": productId, 
        "domainId": current_shop_id
    })
    
    if not product_doc:
        raise HTTPException(status_code=404, detail="Product not found")

    # 2.2 Get Variants
    cursor_variants = db["salepiev1"]["productVariant"].find({
        "productId": productId, 
        "domainId": current_shop_id
    })
    variants_docs = await cursor_variants.to_list(length=1000)

    # 2.3 Get Images
    cursor_images = db["salepiev1"]["productImage"].find({
        "productId": productId, 
        "domainId": current_shop_id
    })
    images_docs = await cursor_images.to_list(length=1000)

    # ==========================================
    # 3. Transform & Map to Models
    # ==========================================

    # --- 3.1 Handle Images List ---
    all_image_models: List[product.ProductImageOut] = []


    # 📌 Dictionary สำหรับจัดกลุ่มรูปของ Variant
    # Key = (variantKey, variantValue) เช่น ('color', 'red')
    # Value = List of Images
    variant_images_map: Dict[Tuple[str, str], List[product.ProductImageMinOut]] = {}
    grouped_images_map: Dict[Tuple[str, str], List[product.ProductImageMinOut]] = {}
    
    
    # ex::  {('color', 'black'): [ProductImageOut(uid='7cf75585-f495-4422-970a-39b9c69b5d2e', ...
    
    
    product_only_images_min_list = [] # สำหรับใส่ในตัว Product แม่ (images field)
    
    
    for img in images_docs:
        if "_id" in img: img.pop("_id")

        full_img_model = product.ProductImageOut(**img)
        min_img_model = product.ProductImageMinOut(**full_img_model.model_dump())

        # --- Logic จัดกลุ่ม ---
        v_key = full_img_model.variantKey or "main"
        
        # ✅ แก้ไขตรงนี้: ถ้า variantValue ไม่มีค่า (None หรือ "") ให้ใช้ "main"
        v_val = full_img_model.variantValue or "main"

        # สร้าง Key สำหรับ Group
        group_key = (v_key, v_val)

        if group_key not in grouped_images_map:
            grouped_images_map[group_key] = []
        
        grouped_images_map[group_key].append(min_img_model)

        # (Optional) ถ้าอยากเก็บแยก list สำหรับ Product แม่เหมือนเดิม ก็ยังทำได้
        if not full_img_model.variantKey and not full_img_model.variantValue:
            product_only_images_min_list.append(min_img_model)


    # --- 3.2 Handle Product ---
    if "_id" in product_doc: product_doc.pop("_id")
    
    # สร้าง Model ProductOutDetail
    # ใส่ images เฉพาะของ product เข้าไป (Pydantic จะ validate ว่าตรงกับ ProductImageInItemDB ไหม)
    # ✅ ตอนนี้ product_only_images_data จะมีข้อมูลครบแล้ว
    # Pydantic จะรับ Dict นี้ไปสร้างเป็น ProductImageMinOut ให้เอง
    # product_doc["images"] = [img.model_dump() for img in product_only_images_min_list]
    product_out = product.ProductOutDetail(**product_doc)

    logger.info(f"product_out: {product_out}\n\n")


    # --- 3.3 Handle Variants ---
    variant_out_list: List[product.ProductVariantOut] = []
    for var in variants_docs:
        if "_id" in var: var.pop("_id")
        var_model = product.ProductVariantOut(**var)
        
        # Mapping รูปเข้า Variant (ถ้าต้องการใส่ใน Variant Object ด้วย)
        # lookup_key = (var_model.variantKey, var_model.variantValue)
        # if lookup_key in grouped_images_map:
        #     var_model.images = grouped_images_map[lookup_key]
        
        variant_out_list.append(var_model)
        
        # 🧠 LOGIC ดึงรูปจาก Map มาใส่:
        # ใช้ Key เดียวกันกับตอนวนลูปรูปภาพ (variantKey, variantValue)
        # lookup_key = (var_model.variantKey, var_model.variantValue)
        
        # if lookup_key in variant_images_map:
        #     # ✅ ถ้าเจอรูปที่ Key ตรงกัน ก็ยัดใส่ list images ของ variant นั้นเลย
        #     # ✅ แบบใหม่: แปลงเป็น ProductImageMinOut เพื่อให้ Validator (add_base_url_prefix) ทำงาน
        #     var_model.images = [
        #         product.ProductImageMinOut(**img.model_dump()) 
        #         for img in variant_images_map[lookup_key]
        #     ]
        # variant_out_list.append(var_model)

    
    # --- 3.4 Prepare Final Grouped Images List ---
    # แปลงจาก Dictionary กลับเป็น List[ProductVariantImageGroup]
    final_grouped_images = []
    
    for (key, val), img_list in grouped_images_map.items():
        # สร้าง Group Object
        group_obj = product.ProductVariantImageGroup(
            variantKey=key,
            variantValue=val,
            images=img_list
        )
        final_grouped_images.append(group_obj)
        

    # ==========================================
    # 4. Final Response Construction
    # ==========================================
    
    # ประกอบร่างเป็น Root Model
    return product.ProductItemOutDetail(
        product=product_out,
        variants=variant_out_list,
        images=final_grouped_images # ✅ Uncomment บรรทัดนี้ได้เลย ถ้าแก้ Model แล้ว
    )


# [pd-3][v1] Product list 
@router.get("/product-in-shop", tags=["product"])
async def product_in_shop(
        page: int = Query(1, ge=1),  # Default page = 1
        page_size: int = Query(10, ge=1, le=100),  # Default page_size = 10
        q: Optional[str] = Query(None),
        itemStatus: Optional[str] = Query(None),
        color: Optional[List[str]] = Query(None),
        size: Optional[List[str]] = Query(None),
        sortBy: Optional[str] = Query(None),
        db: AsyncIOMotorClient =  Depends(get_database),  
        currentUser  : user.UserDb = Depends(authRepo.get_current_active_user)
        
    ):

    current_shop_id = currentUser.domainId
    
    # ============================================
    # 1. Build Pipeline Stages
    # ============================================
    pipeline = []

    # --- Stage 1: Match Product (กรองเบื้องต้นที่ระดับ Product) ---
    match_query = {
        "domainId": current_shop_id,
        "deleted": { "$ne": True }
    }

    if q:
        regex_pattern = { "$regex": q, "$options": "i" }
        match_query["$or"] = [
            { "name": regex_pattern },
            { "code": regex_pattern },
            { "brand": regex_pattern }
        ]

    if itemStatus:
        match_query["itemStatus"] = itemStatus
        
    pipeline.append({ "$match": match_query })


    # --- Stage 2: Lookup Variants (Join เพื่อเช็ค Color/Size) ---
    # จำเป็นต้อง join ถ้ามีการ filter ด้วย color หรือ size
    # (หรือถ้าอยากให้ sort by price แม่นยำจาก variant ก็ต้อง join)
    pipeline.append({
        "$lookup": {
            "from": "productVariant",       # ชื่อ collection ใน DB (เช็คให้ตรง)
            "localField": "uid",            # field ใน product
            "foreignField": "productId",    # field ใน productVariant
            "as": "variants"                # ชื่อ field ใหม่ที่จะงอกออกมา
        }
    })

    # --- Stage 3: Filter by Color / Size (กรองจากผลการ Join) ---
    variant_match_conditions = {}
    
    if color:
        # หาว่าใน array variants มีตัวไหนที่ field 'color' ตรงกับใน list ที่ส่งมาไหม
        # $in ใช้กับ array of objects ได้เลยใน MongoDB
        variant_match_conditions["variants.color"] = { "$in": color }
        
    if size:
        variant_match_conditions["variants.size"] = { "$in": size }
        
    if variant_match_conditions:
        pipeline.append({ "$match": variant_match_conditions })


    # --- Stage 4: Sorting ---
    sort_stage = { "createDateTime": -1 } # Default

    if sortBy:
        if sortBy == "price_asc":
            # เรียงตามราคาจาก variant ตัวแรก (หรือ logic อื่นตามต้องการ)
            sort_stage = { "variants.standardPrice": 1 } 
        elif sortBy == "price_desc":
            sort_stage = { "variants.standardPrice": -1 }
        elif sortBy == "name_asc":
            sort_stage = { "name": 1 }
        elif sortBy == "newest":
            sort_stage = { "createDateTime": -1 }
            
    pipeline.append({ "$sort": sort_stage })


    # --- Stage 5: Pagination & Count (ใช้ $facet เพื่อทำพร้อมกัน) ---
    pipeline.append({
        "$facet": {
            "metadata": [ { "$count": "total" } ],
            "data": [ 
                { "$skip": (page - 1) * page_size }, 
                { "$limit": page_size } 
                # Optional: Project เอา field variants ออกถ้าไม่อยากส่งกลับไปเยอะ
                # , { "$project": { "variants": 0 } } 
            ]
        }
    })

    # ============================================
    # 2. Execute Aggregation
    # ============================================
    result = await db["salepiev1"]["product"].aggregate(pipeline).to_list(length=1)
    
    # ดึงข้อมูลจาก Facet Result
    facet_result = result[0]
    
    # 1. Total Items
    total_items = 0
    if facet_result["metadata"]:
        total_items = facet_result["metadata"][0]["total"]
        
    # 2. Data Rows
    rows = facet_result["data"]
    
    # ============================================
    # 3. Transform Data
    # ============================================
    data_list = []
    ind = 1
    for row in rows:
        if "_id" in row: row.pop("_id")
        # เอา variants ออกก่อนส่งเข้า Model (ถ้า Model ProductOut ไม่ได้รับ variants)
        # หรือถ้าต้องการใช้ข้อมูลราคาจาก variant ก็ map ตรงนี้ได้
        print(f"{ind} >>> {row} \n\n")
        
        # if "variants" in row: del row["variants"] 
        
    # ============================================
    # 🔥 3. Transform & Filter Unique Colors
    # ============================================
    data_list = []
    
    for row in rows:
        if "_id" in row: row.pop("_id")
        
        # เตรียม Set เพื่อเก็บค่าที่ไม่ซ้ำ (Set ตัดตัวซ้ำอัตโนมัติ)
        unique_colors_set = set()
        unique_sizes_set = set()

        # ตัวแปรสำหรับเก็บ Variant ทั้งหมดที่จะส่งออกไป
        processed_variants = []


        # ตัวแปรหาช่วงราคา (Min/Max) จาก Variant เพื่อเอามาโชว์ที่ตัวแม่
        min_price = float('inf')
        max_price = float('-inf')
        
        # ตัวแปรสำหรับเก็บ Variant ตัวแทนสี (Logic เดิม)
        unique_color_variant_map = {} 

        # Process Variants สี / ไซส์ เป็น UNIQUE
        if "variants" in row and isinstance(row["variants"], list) and len(row["variants"]) > 0:
            for var in row["variants"]:
                # เก็บสี/ไซส์
                c_val = var.get("color")
                s_val = var.get("size")
                if c_val: unique_colors_set.add(c_val)
                if s_val: unique_sizes_set.add(s_val)

                # คำนวณราคา (ถ้ามี)
                price = var.get("standardPrice", 0) or 0
                if price > 0:
                    min_price = min(min_price, price)
                    max_price = max(max_price, price)

                # Logic กรอง Unique Color Variant
                if c_val and c_val not in unique_color_variant_map:
                    if "_id" in var: var.pop("_id")
                    
                    # ⚠️ แปลงเป็น Dict ทันที เพื่อป้องกัน Error ตอนเข้า Model แม่
                    try:
                        # สร้าง Model เพื่อ Validate ข้อมูลลูกก่อน
                        var_model = product.ProductVariantOutList(**var)
                        # แปลงกลับเป็น Dict เพื่อความปลอดภัย
                        unique_color_variant_map[c_val] = var_model.model_dump()
                        
                    except Exception as e_var:
                        print(f"⚠️ Skip variant {var.get('uid')} due to error: {e_var}")
                    
                    # processed_variants.append(var_model.model_dump())


           
            # เช็คว่า min_price ถูก update ไหม (ไม่ใช่ infinity)
            if min_price != float('inf'):
                row["standardPrice"] = min_price
                row["sellingPrice"] = min_price # หรือ logic อื่นตามต้องการ

        else:
            row["variants"] = []
            # ถ้าไม่มี variant เลย ให้ราคาเป็น 0 หรือตาม DB
            if "standardPrice" not in row: row["standardPrice"] = 0
            if "sellingPrice" not in row: row["sellingPrice"] = 0

        # Update row: Available Lists
        row["availableColors"] = sorted(list(unique_colors_set))
        row["availableSizes"] = sorted(list(unique_sizes_set))


        
        # ======================================================
        # 🏁 Final Mapping to Main Model
        # ======================================================
        try:
            item = product.ProductItemOutListNoVariants(**row)
            data_list.append(item)
        except Exception as e:
            # 🛑 ปริ้นท์ Error ตัวแดงออกมาดูเลยครับ ว่าพังที่ Field ไหน
            print(f"\n💥 CRITICAL PARSE ERROR [UID: {row.get('uid')}]:")
            print(f"Error Details: {e}")

    return {
        "success": True,
        "page": page,
        "pageSize": page_size,
        "totalItems": total_items,
        "totalPages": math.ceil(total_items / page_size) if page_size > 0 else 1,
        "data": data_list,
    }















































