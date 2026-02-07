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
# os.path.abspath("mydir/")



# [V0.1]
# def filterItems( products: List[dict], criteria: Optional[dict]=None):
    
    
#     filtered = [
#         product for product in products if all(
#             product.get(key, '').lower() in [v.lower() for v in values]
#             for key, values in criteria.items()
#         )
#     ]
    
#     # print("filtered >>> ",filtered)
    
#     return filtered

# [V0.3]
def match_criteria(product: dict, criteria: dict) -> bool:
    """ ตรวจสอบว่าสินค้าตรงกับเงื่อนไขทั้งหมด """
    for key, values in criteria.items():
        # print(f"match_criteria key: {key} values: {values} >>> product: {product}")
        if key == "textSearch":  # ค้นหาโดย q
            q_lower = str(values).lower()
            if not (
                q_lower in str(product.get("title", "")).lower() or
                q_lower in str(product.get("prod_id", "")).lower() or
                q_lower in str(product.get("product_sku", "")).lower() or
                q_lower in str(product.get("name", "")).lower()
            ):
                return False
        else:  # ค้นหาตาม key อื่น ๆ เช่น color, size
            # กำจัด key ที่มี : เผื่อเจอ "color:" แบบผิด
            product_keys = {k.rstrip(":"): v for k, v in product.items()}
            if key in product_keys:
                product_value = product_keys[key]

                if isinstance(product_value, list):
                    if not any(str(v).lower() in [str(val).lower() for val in values] for v in product_value):
                        return False
                else:
                    if str(product_value).lower() not in [str(val).lower() for val in values]:
                        return False
            else:
                return False  # key ไม่พบเลยใน product
    return True


# [V0.2]
def filterItems(itemList: List[dict], criteria: dict):
    """ กรองสินค้าตาม criteria ที่กำหนด """
    return [itm for itm in itemList if match_criteria(itm, criteria)]


def sortData(filtered_products: List[dict], sortBy: str):
    # **เพิ่มส่วนนี้สำหรับการเรียงลำดับ**
    if sortBy:
        if sortBy == "newest":
            filtered_products.sort(key=lambda x: x["prod_id"], reverse=True)  # สมมติ id เป็น sequential
        elif sortBy == "best-selling":
            filtered_products.sort(key=lambda x: x.get("progress_percent", 0), reverse=True)
        elif sortBy == "price-asc":
            filtered_products.sort(key=lambda x: float(x["list_price"].replace("$", "")))
        elif sortBy == "price-desc":
            filtered_products.sort(key=lambda x: float(x["list_price"].replace("$", "")), reverse=True)
        elif sortBy == "name":
            filtered_products.sort(key=lambda x: float(x["name"]))

    return filtered_products

    # แบ่งข้อมูลตามหน้า