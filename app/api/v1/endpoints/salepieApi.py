from typing import List, Optional , Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query

from repo import  userRepo, authRepo, filterRepo

##### BEGIN : DATABSE #####

from models import  schemas, user, csharpModel
# from loguru import logger
from pydantic import BaseModel, Json ,ValidationError, validator, Field, EmailStr
from database.mongodb import AsyncIOMotorClient, get_database
from database.mongodb_utils import close_mongo_connection, connect_to_mongo

from fastapi.encoders import jsonable_encoder

from utils import util

from time import time
import httpx
import asyncio
import stripe

import math
import uuid

from models.product import *
from models.product import *

router = APIRouter()

from sqlmodel import Field, Session, SQLModel, create_engine

@router.get("/get-product/{shopId}")
async def get_product(shopId: str,db: AsyncIOMotorClient =  Depends(get_database)) :
  
  if not shopId :  
    raise HTTPException(status_code=400, detail="Bad request: Not found code" )
  
  rows =     db["salepiev1"]["productItem"].find( 
                                                { "shopInfoId" : shopId } 
                                                        
                                             ).sort("createDateTime",-1)
  

  products = [ProductItemDB(**row) async for row in rows ]
  
  return products
    

@router.post("/product")
async def create_product(item: ProductIn, db: AsyncIOMotorClient =  Depends(get_database)) :
    
    if not item:
        raise HTTPException(status_code=400, detail="Bad request: Not found code" )
    timenow = datetime.now()
    now_str = timenow.strftime("%Y-%m-%d %H:%M:%S.%f")
    uid = util.getUuid()
    
    

    product_db = ProductDB(
        **item.dict(), 
        uid=uid
    )
    # product_db.uid = util.getUuid()
    product_db.createDateTime = timenow
    product_db.updateDateTime = timenow
    product_db.latestDateIncoming = timenow
    
    print(f"product_db >>>>>>  {product_db.model_dump()}")
    # >> เก็บลง database ที่นี่ถ้าต้องการ <<
    
    try: 
        # encoded = jsonable_encoder(product_db)  # ✅ สำคัญ
        encoded = jsonable_encoder(product_db, custom_encoder={datetime: lambda v: v.isoformat()})
        await db["salepiev1"]["productItem"].insert_one(encoded)
        # campaign =  await db["salepiev1"]["productItem"].insert_one( product_db.model_dump() ) 

    except Exception as e:
        import traceback
        traceback.print_exc()  # log เต็ม
        raise HTTPException(status_code=422, detail=f"Unable to save data: {str(e)}")
    
    return """product created successfully"""


@router.get("/products")
async def get_products(
    page: int = Query(1, ge=1),  # Default page = 1
    page_size: int = Query(10, ge=1, le=100),  # Default page_size = 10
    q: Optional[str] = Query(None),  
    color:  Optional[List[str]] = Query(None),
    size: Optional[List[str]] = Query(None),
    sortBy: Optional[str] = Query(None)
):
    """
    API for fetching paginated data.
    """
    start = (page - 1) * page_size
    end = start + page_size
    

    # สร้าง dictionary สำหรับเก็บ criteria จาก query parameters
    criteria = {}
    textSearch = ""
    sorting = ""
    
    # if categoryId:
    #     criteria["categoryId"] = categoryId
    if color:
        criteria["color"] = color
    if size:
        criteria["size"] = size
    if q:
        criteria["textSearch"] = q.strip()
    
    print(f"criteria >>>>>>  {criteria}")
    
    if sortBy:
        sorting = sortBy
    # print(f"sorting >>>>>>  {sorting}")
    
    

    
    
    # ตัวอย่างข้อมูล

    products = [
             {
                "image": "/media/store/client/600x600/11.png",
                "name": "Cloud Shift Lightweight Runner Pro Edition",
                "rating": 5.0,
                "sku": "SH-001-BLK-42",
                "brand": "Nike",
                "category": "Sneakers",
                "price": 99.00,
                "old_price": None,
                "discount": None,
                "actions": ["Add to Cart"]
                },
                {
                "image": "/media/store/client/600x600/12.png",
                "name": "Titan Edge High Impact Stability Lightweight Trainers",
                "rating": 3.5,
                "sku": "SNK-XY-WHT-10",
                "brand": "Adidas",
                "category": "Running Shoes",
                "price": 65.99,
                "old_price": None,
                "discount": None,
                "actions": ["Add to Cart"]
                },
                {
                "image": "/media/store/client/600x600/13.png",
                "name": "Wave Strike Dynamic Boost Sneaker",
                "rating": 4.7,
                "sku": "BT-A1-YLW-8",
                "brand": "Timberland",
                "category": "Boots",
                "price": 120.00,
                "old_price": None,
                "discount": None,
                "actions": ["Add to Cart"]
                },
                {
                "image": "/media/store/client/600x600/14.png",
                "name": "Wave Strike Dynamic Boost Sneaker",
                "rating": 3.2,
                "sku": "SD-Z9-BRN-39",
                "brand": "Birkenstock",
                "category": "Sandals",
                "price": 140.00,
                "old_price": 179.00,
                "discount": "SAVE 15 %",
                "actions": ["Add to Cart"]
                },
                {
                "id": 1,
                "image":  "/media/store/client/600x600/15.png",
                "name": "Titan Edge High Impact Stability Lightweight Trainers",
                "sku": "SNK-555-GRY-11",
                "rating": 3.5,
                "price": 65.99,
                "originalPrice": None,
                "discount": None,
                "brand": "New Balance",
                "category": "Sneakers"
                },
                {
                "id": 2,
                "image":  "/media/store/client/600x600/16.png",
                "name": "Velocity Boost Xtreme High Shock Absorbers",
                "sku": "SH-222-BLU-40",
                "rating": 4.9,
                "price": 280.00,
                "originalPrice": 315.00,
                "discount": "SAVE 15 %",
               
                "brand": "Puma",
                "category": "Sneakers",
                },
                {
                "id": 3,
                "image":  "/media/store/client/600x600/2.png",
                "name": "Velocity Boost Xtreme High Shock Absorbers",
                "sku": "BT-777-BLK-9",
                "rating": 4.9,
                "price": 110.00,
                "originalPrice": None,
                "discount": None,
                "brand": "UGG",
                "category": "Boots"
                },
                {
                "id": 4,
                "image":  "/media/store/client/600x600/1.png",
                "name": "Cloud Shift Lightweight Runner Pro Edition",
                "sku": "SD-999-TAN-38",
                "rating": 3.9,
                "price": 99.00,
                "originalPrice": None,
                "discount": None,
                "brand": "Crocs",
                "category": "Sandals"
                }
           
              ]



    # products = [
    #     {
    #         "prod_id": "sohgoisd3453451",
    #         "pic_url": "https://images.unsplash.com/photo-1528310385748-dba09bf1657a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=320&h=320&q=80",
    #         "title": "Google Home",
    #         "cat_name": "Electronics",
    #         "color": "black",
    #         "size" : "2L",
    #         "is_in_stock": 25,
    #         "product_sku": "2384741241",
    #         "list_price": "$65",
    #         "progress_percent": 25,
    #         "channels": ["🛍️ In store", "🌐 Online"],
    #         "actions_data": {
    #             "view_url": "../../pro/ecommerce/product-details.html",
    #             "download_types": ["Excel", "Word"]
    #         }
    #     },
    #     {
    #         "prod_id": "678dgosjs9civhh09222s",
    #         "pic_url": "https://images.unsplash.com/photo-1613852348851-df1739db8201?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=320&h=320&q=80",
    #         "title": "Calvin Klein T-shirts",
    #         "cat_name": "Clothing",
    #         "color": "red",
    #         "size" : "2L",
    #         "is_in_stock": 5,
    #         "product_sku": "4124123847",
    #         "list_price": "$21",
    #         "progress_percent": 50,
    #         "channels": ["🛍️ In store"],
    #         "actions_data": {
    #             "view_url": "../../pro/ecommerce/product-details.html",
    #             "download_types": ["Excel", "Word"]
    #         }
    #     },
    #     {
    #         "prod_id": "sn8ysdvdfgvhhis3339dhj8",
    #         "pic_url": "https://images.unsplash.com/photo-1611911813383-67769b37a149?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=320&h=320&q=80",
    #         "title": "Pattern Winter Sweater",
    #         "cat_name": "Accessories",
    #         "color": "green",
    #         "is_in_stock": 45,
    #         "product_sku": "8472341241",
    #         "list_price": "$37",
    #         "channels": ["🛍️ In store", "🌐 Online"],
    #         "actions_data": {
    #             "view_url": "../../pro/ecommerce/product-details.html",
    #             "download_types": ["Excel", "Word"]
    #         }
    #     },
    #     {
    #         "prod_id": "mbiusndfu89s444d76sdf90u0sd",
    #         "title": "White Blazer by Armani",
    #         "cat_name": "Clothing",
    #         "color": "olive_green",
    #         "status": "Available",
    #         "product_sku": "7184741241",
    #         "list_price": "$17",
    #         "channels": ["🛍️ In store"],
    #         "pic_url": "https://images.unsplash.com/photo-1616969899621-0ea269426a21?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=320&h=320&q=80",
    #         "actions_data": {
    #             "details_url": "../../pro/ecommerce/product-details.html",
    #             "download_types": ["Excel", "Word"]
    #         }
    #     },
    #     {
    #         "prod_id": "sn8ysdvdfgvhhis9d444555hj8",
    #         "pic_url": "https://images.unsplash.com/photo-1611911813383-67769b37a149?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=320&h=320&q=80",
    #         "title": "Pattern Winter Sweater",
    #         "cat_name": "Accessories",
    #         "color": "black",
    #         "size" : "6L",
    #         "is_in_stock": 2,
    #         "product_sku": "8472341241",
    #         "list_price": "$37",
    #         "channels": ["🛍️ In store", "🌐 Online"],
    #         "actions_data": {
    #             "view_url": "../../pro/ecommerce/product-details.html",
    #             "download_types": ["Excel", "Word"]
    #         }
    #     },
    #     {
    #         "prod_id": "mbiusndf66677u89sd76sdf90u0sd",
    #         "title": "White Blazer by Armani",
    #         "cat_name": "Clothing",
    #         "color": "red",
    #         "status": "Available",
    #         "product_sku": "7184741241",
    #         "list_price": "$17",
    #         "channels": ["🛍️ In store"],
    #         "pic_url": "https://images.unsplash.com/photo-1616969899621-0ea269426a21?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=320&h=320&q=80",
    #         "actions_data": {
    #             "details_url": "../../pro/ecommerce/product-details.html",
    #             "download_types": ["Excel", "Word"]
    #         }
    #     },
    #     {
    #         "prod_id": "sn8ys777dvdfgvhhis9dhj8",
    #         "pic_url": "https://images.unsplash.com/photo-1611911813383-67769b37a149?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=320&h=320&q=80",
    #         "title": "Pattern Winter Sweater",
    #         "cat_name": "Accessories",
    #         "color": "blue",
    #         "size" : "2L",
    #         "is_in_stock": 5,
    #         "product_sku": "8472341241",
    #         "list_price": "$37",
    #         "channels": ["🛍️ In store", "🌐 Online"],
    #         "actions_data": {
    #             "view_url": "../../pro/ecommerce/product-details.html",
    #             "download_types": ["Excel", "Word"]
    #         }
    #     },
    #     {
    #         "prod_id": "mbiusndfu8754569sd76sdf90u0sd",
    #         "title": "White Blazer by Armani",
    #         "cat_name": "Clothing",
    #         "color": "red",
    #         "size" : "2L",
    #         "status": "Available",
    #         "product_sku": "7184741241",
    #         "list_price": "$17",
    #         "channels": ["🛍️ In store"],
    #         "pic_url": "https://images.unsplash.com/photo-1616969899621-0ea269426a21?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=320&h=320&q=80",
    #         "actions_data": {
    #             "details_url": "../../pro/ecommerce/product-details.html",
    #             "download_types": ["Excel", "Word"]
    #         }
    #     },
    #     {
    #         "prod_id": "sn8ysdvdf76456gvhhis9dhj8",
    #         "pic_url": "https://images.unsplash.com/photo-1611911813383-67769b37a149?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=320&h=320&q=80",
    #         "title": "Pattern Winter Sweater",
    #         "cat_name": "Accessories",
    #         "color": "black",
    #         "size" : "2L",
    #         "is_in_stock": 6,
    #         "product_sku": "8472341241",
    #         "list_price": "$37",
    #         "channels": ["🛍️ In store", "🌐 Online"],
    #         "actions_data": {
    #             "view_url": "../../pro/ecommerce/product-details.html",
    #             "download_types": ["Excel", "Word"]
    #         }
    #     },
    #     {
    #         "prod_id": "mbiusndfu89sd76sdf90u0sd",
    #         "title": "White Blazer by Armani",
    #         "cat_name": "Clothing",
    #         "color": "pink",
    #         "status": "Available",
    #         "product_sku": "7184741241",
    #         "list_price": "$17",
    #         "channels": ["🛍️ In store"],
    #         "pic_url": "https://images.unsplash.com/photo-1616969899621-0ea269426a21?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=320&h=320&q=80",
    #         "actions_data": {
    #             "details_url": "../../pro/ecommerce/product-details.html",
    #             "download_types": ["Excel", "Word"]
    #         }
    #     },
    #     {
    #         "prod_id": "sohg4576456isd345345",
    #         "pic_url": "https://images.unsplash.com/photo-1528310385748-dba09bf1657a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=320&h=320&q=80",
    #         "title": "Google Home",
    #         "cat_name": "Electronics",
    #         "color": "black",
    #         "is_in_stock": 8,
    #         "product_sku": "2384741241",
    #         "list_price": "$65",
    #         "progress_percent": 25,
    #         "channels": ["🛍️ In store", "🌐 Online"],
    #         "actions_data": {
    #             "view_url": "../../pro/ecommerce/product-details.html",
    #             "download_types": ["Excel", "Word"]
    #         }
    #     },
    #     {
    #         "prod_id": "678dgos345346js9civhh09s",
    #         "pic_url": "https://images.unsplash.com/photo-1613852348851-df1739db8201?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=320&h=320&q=80",
    #         "title": "Calvin Klein T-shirts",
    #         "cat_name": "Clothing",
    #         "color": "black",
    #         "size" : "XL",
    #         "is_in_stock": 5,
    #         "product_sku": "4124123847",
    #         "list_price": "$21",
    #         "progress_percent": 50,
    #         "channels": ["🛍️ In store"],
    #         "actions_data": {
    #             "view_url": "../../pro/ecommerce/product-details.html",
    #             "download_types": ["Excel", "Word"]
    #         }
    #     }
    # ]
    
    
    filtered_products  = filterRepo.filterItems(products, criteria)
    
    
    filtered_sorted_products = filterRepo.sortData(filtered_products, sorting)
    
    data = filtered_sorted_products[start:end]
    
    return {
        "page": page,
        "page_size": page_size,
        "total_items": len(filtered_products),
        "total_pages": math.ceil(len(filtered_products) / page_size),
        "data": data,
    }
    
@router.get("/products2")
async def get_products2(
    page: int = Query(1, ge=1),  # Default page = 1
    page_size: int = Query(10, ge=1, le=100),  # Default page_size = 10
    q: Optional[str] = Query(None),  
    color:  Optional[List[str]] = Query(None),
    size: Optional[List[str]] = Query(None),
    sortBy: Optional[str] = Query(None)
):
    """
    API for fetching paginated data.
    """
    start = (page - 1) * page_size
    end = start + page_size
    

    # สร้าง dictionary สำหรับเก็บ criteria จาก query parameters
    criteria = {}
    textSearch = ""
    sorting = ""
    
    # if categoryId:
    #     criteria["categoryId"] = categoryId
    if color:
        criteria["color"] = color
    if size:
        criteria["size"] = size
    if q:
        criteria["textSearch"] = q
    
    print(f"criteria >>>>>>  {criteria}")
    
    if sortBy:
        sorting = sortBy
    # print(f"sorting >>>>>>  {sorting}")
    
    

    
    
    # ตัวอย่างข้อมูล
    products = [
      {
          "prod_id": "phoenix-saas",
          "sku" : "PHX-001",
          "pic_url": "/media/brand-logos/office.svg",
          "title": "Phoenix SaaS",
          "sub_title": "Cloud storage and file sharing",
          "duration": "1-3 months",
          "location": "Flexible",
          "list_price": "$65",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-4.png",
            "/media/avatars/300-1.png",
            "/media/avatars/300-2.png",
            "S"
          ]
        },
        {
          "prod_id": "golden-gate-analytics",
          "sku" : "GGA-002",
          "pic_url": "/media/brand-logos/btcchina.svg",
          "title": "Golden Gate Analytics",
          "sub_title": "Team communication and collaboration tool",
          "duration": "2-4 months",
          "location": "Global",
          "list_price": "$25",
          "status": "Completed",
          "avatars": [
            "/media/avatars/300-5.png",
            "/media/avatars/300-17.png",
            "/media/avatars/300-16.png"
          ]
        },
        {
          "prod_id": "sparkletech",
          "sku" : "SPK-003",
          "pic_url": "/media/brand-logos/jira.svg",
          "title": "SparkleTech",
          "sub_title": "Short-term accommodation marketplace",
          "duration": "3-5 months",
          "location": "Remote",
          "list_price": "$16",
          "status": "Upcoming",
          "avatars": [
            "/media/avatars/300-19.png",
            "/media/avatars/300-9.png"
          ]
        },
        {
          "prod_id": "nexus-design-system",
          "pic_url": "/media/brand-logos/equacoin.svg",
          "title": "Nexus Design System",
          "sub_title": "Visual discovery and inspiration",
          "duration": "2-6 months",
          "location": "Onsite",
          "list_price": "$45",
          "status": "Completed",
          "avatars": [
            "/media/avatars/300-5.png",
            "/media/avatars/300-11.png",
            "W"
          ]
        },
        {
          "prod_id": "neptune-app",
          "pic_url": "/media/brand-logos/slack.svg",
          "title": "Neptune App",
          "sub_title": "Peer-to-peer mobile payment service",
          "duration": "3-8 months",
          "location": "Flexible",
          "list_price": "$34",
          "status": "Completed",
          "avatars": [
            "/media/avatars/300-17.png",
            "/media/avatars/300-1.png",
            "/media/avatars/300-19.png",
            "P"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "golden-gate-analytics",
          "pic_url": "/media/brand-logos/btcchina.svg",
          "title": "Golden Gate Analytics",
          "sub_title": "Team communication and collaboration tool",
          "duration": "2-4 months",
          "location": "Global",
          "list_price": "$25",
          "status": "Upcoming",
          "avatars": [
            "/media/avatars/300-5.png",
            "/media/avatars/300-17.png",
            "/media/avatars/300-16.png"
          ]
        },
        {
          "prod_id": "golden-gate-analytics",
          "pic_url": "/media/brand-logos/btcchina.svg",
          "title": "Golden Gate Analytics",
          "sub_title": "Team communication and collaboration tool",
          "duration": "2-4 months",
          "location": "Global",
          "list_price": "$25",
          "status": "Upcoming",
          "avatars": [
            "/media/avatars/300-5.png",
            "/media/avatars/300-17.png",
            "/media/avatars/300-16.png"
          ]
        },
    ]
    
    
    filtered_products  = filterRepo.filterItems(products, criteria)
    
    
    filtered_sorted_products = filterRepo.sortData(filtered_products, sorting)
    
    data = filtered_sorted_products[start:end]
    
    return {
        "page": page,
        "page_size": page_size,
        "total_items": len(filtered_products),
        "total_pages": math.ceil(len(filtered_products) / page_size),
        "data": data,
    }

@router.get("/products2-offset")
async def get_products2_offset(
    offset: int = Query(0, ge=0),  # เริ่มจากตำแหน่งที่ 0
    limit: int = Query(5, ge=1, le=20),  # โหลดครั้งละ 5 records
    q: Optional[str] = Query(None),  
    color: Optional[List[str]] = Query(None),
    size: Optional[List[str]] = Query(None),
    sortBy: Optional[str] = Query(None)
):
    """
    API for infinite scroll pagination.
    """
    # สร้าง criteria จาก query parameters
    criteria = {}
    
    if color:
        criteria["color"] = color
    if size:
        criteria["size"] = size
    if q:
        criteria["textSearch"] = q
    
    print(f"criteria >>>>>>  {criteria}")
    
    sorting = sortBy if sortBy else ""

    # สร้าง dictionary สำหรับเก็บ criteria จาก query parameters
    criteria = {}
    textSearch = ""
    sorting = ""
    
    # if categoryId:
    #     criteria["categoryId"] = categoryId
    if color:
        criteria["color"] = color
    if size:
        criteria["size"] = size
    if q:
        criteria["textSearch"] = q
    
    print(f"criteria >>>>>>  {criteria}")
    
    if sortBy:
        sorting = sortBy
    # print(f"sorting >>>>>>  {sorting}")
    
    

    
    
    # ตัวอย่างข้อมูล
    products = [
      {
          "prod_id": "phoenix-saas",
          "sku" : "PHX-001",
          "pic_url": "/media/brand-logos/office.svg",
          "title": "Phoenix SaaS",
          "sub_title": "Cloud storage and file sharing",
          "duration": "1-3 months",
          "location": "Flexible",
          "list_price": "$65",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-4.png",
            "/media/avatars/300-1.png",
            "/media/avatars/300-2.png",
            "S"
          ]
        },
        {
          "prod_id": "golden-gate-analytics",
          "sku" : "GGA-002",
          "pic_url": "/media/brand-logos/btcchina.svg",
          "title": "Golden Gate Analytics",
          "sub_title": "Team communication and collaboration tool",
          "duration": "2-4 months",
          "location": "Global",
          "list_price": "$25",
          "status": "Upcoming",
          "avatars": [
            "/media/avatars/300-5.png",
            "/media/avatars/300-17.png",
            "/media/avatars/300-16.png"
          ]
        },
        {
          "prod_id": "sparkletech",
          "sku" : "SPK-003",
          "pic_url": "/media/brand-logos/jira.svg",
          "title": "SparkleTech",
          "sub_title": "Short-term accommodation marketplace",
          "duration": "3-5 months",
          "location": "Remote",
          "list_price": "$16",
          "status": "Upcoming",
          "avatars": [
            "/media/avatars/300-19.png",
            "/media/avatars/300-9.png"
          ]
        },
        {
          "prod_id": "nexus-design-system",
          "pic_url": "/media/brand-logos/equacoin.svg",
          "title": "Nexus Design System",
          "sub_title": "Visual discovery and inspiration",
          "duration": "2-6 months",
          "location": "Onsite",
          "list_price": "$45",
          "status": "Completed",
          "avatars": [
            "/media/avatars/300-5.png",
            "/media/avatars/300-11.png",
            "W"
          ]
        },
        {
          "prod_id": "neptune-app",
          "pic_url": "/media/brand-logos/slack.svg",
          "title": "Neptune App",
          "sub_title": "Peer-to-peer mobile payment service",
          "duration": "3-8 months",
          "location": "Flexible",
          "list_price": "$34",
          "status": "Completed",
          "avatars": [
            "/media/avatars/300-17.png",
            "/media/avatars/300-1.png",
            "/media/avatars/300-19.png",
            "P"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "radiant-wave",
          "pic_url": "/media/brand-logos/grab.svg",
          "title": "Radiant Wave",
          "sub_title": "Team communication and collaboration",
          "duration": "2-5 months",
          "location": "Remote",
          "list_price": "$33",
          "status": "In Progress",
          "avatars": [
            "/media/avatars/300-24.png",
            "/media/avatars/300-7.png",
            "/media/avatars/300-9.png",
            "S"
          ]
        },
        {
          "prod_id": "golden-gate-analytics",
          "pic_url": "/media/brand-logos/btcchina.svg",
          "title": "Golden Gate Analytics",
          "sub_title": "Team communication and collaboration tool",
          "duration": "2-4 months",
          "location": "Global",
          "list_price": "$25",
          "status": "Upcoming",
          "avatars": [
            "/media/avatars/300-5.png",
            "/media/avatars/300-17.png",
            "/media/avatars/300-16.png"
          ]
        },
        {
          "prod_id": "golden-gate-analytics",
          "pic_url": "/media/brand-logos/btcchina.svg",
          "title": "Golden Gate Analytics",
          "sub_title": "Team communication and collaboration tool",
          "duration": "2-4 months",
          "location": "Global",
          "list_price": "$25",
          "status": "Upcoming",
          "avatars": [
            "/media/avatars/300-5.png",
            "/media/avatars/300-17.png",
            "/media/avatars/300-16.png"
          ]
        },
    ]
    
    
    # Filter และ Sort
    filtered_products = filterRepo.filterItems(products, criteria)
    filtered_sorted_products = filterRepo.sortData(filtered_products, sorting)
    
    # คำนวณข้อมูลที่จะส่งกลับ
    total_items = len(filtered_sorted_products)
    data = filtered_sorted_products[offset:offset + limit]
    has_more = offset + limit < total_items  # มีข้อมูลเพิ่มหรือไม่
    
    return {
        "offset": offset,
        "limit": limit,
        "total_items": total_items,
        "has_more": has_more,
        "next_offset": offset + limit if has_more else None,
        "data": data,
    }
    
@router.get("/users/")
async def get_users(
    db: AsyncIOMotorClient =  Depends(get_database),
    page: int = Query(1, ge=1),  # Default page = 1
    page_size: int = Query(10, ge=1, le=100),  # Default page_size = 10
    q: Optional[str] = Query(None),
    itemStatus: Optional[str] = Query(None),
    sortBy: Optional[str] = Query(None)
): 
    
    """
    API for fetching paginated Users.
    """
    
    criteria = {}
    textSearch = ""
    sorting = ""
    
    start = (page - 1) * page_size
    end = start + page_size
    
    
    if q:
        criteria["textSearch"] = q
    else:
        criteria["textSearch"] = ""
        
    if itemStatus:
        criteria["itemStatus"] = itemStatus
    
    print(f"criteria >>>>>>  {criteria}")
    
    if sortBy:
        sorting = sortBy
    
    # ตัวอย่างข้อมูล
    rows = []
    rows =   db["salepiev1"]["user"].find( 
                                            { "$or" :   [
                                                          { "username" :  {'$regex': criteria["textSearch"], '$options' : 'i' }},
                                                          { "firstName" :  {'$regex': criteria["textSearch"], '$options' : 'i' }},
                                                          { "lastName" :  {'$regex': criteria["textSearch"], '$options' : 'i' }},
                                                          { "description" :  {'$regex': criteria["textSearch"], '$options' : 'i' }}  
                                                        
                                                        ] 
                                              }
                                                        
                                             ).sort("createDateTime",-1)
#     users = [
#   {
#     "id": 1,
#     "name": "Tyler Hero",
#     "email": "tyler.hero@gmail.com",
#     "image": "/media/avatars/300-3.png",
#     "products": [
#       "NFT",
#       "Artwork",
#       "Widget"
#     ],
#     "license": {
#       "type": "Premium",
#       "duration": "4 months left"
#     },
#     "lastPayment": "6 Aug, 2024",
#     "active": True,
#     "invoiceLink": "",
#     "lastLogin" : "2025-07-21T10:20:30Z"
#   },
#   {
#     "id": 2,
#     "name": "Esther Howard",
#     "email": "esther.howard@gmail.com",
#     "image": "/media/avatars/300-1.png",
#     "products": [
#       "Design",
#       "Template"
#     ],
#     "license": {
#       "type": "Trial",
#       "duration": "16 days left"
#     },
#     "lastPayment": "21 Apr, 2024",
#     "active": True,
#     "invoiceLink": "",
#     "lastLogin" : "2025-07-21T10:20:30Z"
#   },
#   {
#     "id": 3,
#     "name": "Jacob Jones",
#     "email": "jacob.jones@gmail.com",
#     "image": "/media/avatars/300-11.png",
#     "products": [
#       "App",
#       "Plugin"
#     ],
#     "license": {
#       "type": "Premium",
#       "duration": "2 months left"
#     },
#     "lastPayment": "14 Mar, 2024",
#     "active": True,
#     "invoiceLink": "",
#     "lastLogin" : "2025-07-21T10:20:30Z"
#   },
#   {
#     "id": 4,
#     "name": "User 4",
#     "email": "user4@example.com",
#     "image": "/media/avatars/300-4.png",
#     "products": [
#       "App",
#       "Widget"
#     ],
#     "license": {
#       "type": "Trial",
#       "duration": "4 days left"
#     },
#     "lastPayment": "4 Jul, 2024",
#     "active": True,
#     "invoiceLink": "",
#     "lastLogin" : "2025-07-21T10:20:30Z"
#   },
#   {
#     "id": 5,
#     "name": "User 5",
#     "email": "user5@example.com",
#     "image": "/media/avatars/300-5.png",
#     "products": [
#       "Template",
#       "NFT"
#     ],
#     "license": {
#       "type": "Standard",
#       "duration": "5 days left"
#     },
#     "lastPayment": "5 Jul, 2024",
#     "active": False,
#     "invoiceLink": "",
#     "lastLogin" : "2025-07-21T10:20:30Z"
#   },
#   {
#     "id": 6,
#     "name": "User 6",
#     "email": "user6@example.com",
#     "image": "/media/avatars/300-6.png",
#     "products": [
#       "App",
#       "Widget"
#     ],
#     "license": {
#       "type": "Premium",
#       "duration": "6 months left"
#     },
#     "lastPayment": "6 Jul, 2024",
#     "active": True,
#     "invoiceLink": "",
#     "lastLogin" : "2025-07-21T10:20:30Z"
#   },
#   {
#     "id": 7,
#     "name": "User 7",
#     "email": "user7@example.com",
#     "image": "/media/avatars/300-7.png",
#     "products": [
#       "Template",
#       "NFT"
#     ],
#     "license": {
#       "type": "Trial",
#       "duration": "7 days left"
#     },
#     "lastPayment": "7 Jul, 2024",
#     "active": False,
#     "invoiceLink": "",
#     "lastLogin" : "2025-07-21T10:20:30Z"
#   },
#   {
#     "id": 8,
#     "name": "User 8",
#     "email": "user8@example.com",
#     "image": "/media/avatars/300-8.png",
#     "products": [
#       "App",
#       "Widget"
#     ],
#     "license": {
#       "type": "Standard",
#       "duration": "8 days left"
#     },
#     "lastPayment": "8 Jul, 2024",
#     "active": True,
#     "invoiceLink": "",
#     "lastLogin" : "2025-07-21T10:20:30Z"
#   },
#   {
#     "id": 9,
#     "name": "User 9",
#     "email": "user9@example.com",
#     "image": "/media/avatars/300-9.png",
#     "products": [
#       "Template",
#       "NFT"
#     ],
#     "license": {
#       "type": "Premium",
#       "duration": "9 months left"
#     },
#     "lastPayment": "9 Jul, 2024",
#     "active": False,
#     "invoiceLink": "",
#     "lastLogin" : "2025-07-21T10:20:30Z"
#   },
#   {
#     "id": 10,
#     "name": "User 10",
#     "email": "user10@example.com",
#     "image": "/media/avatars/300-10.png",
#     "products": [
#       "App",
#       "Widget"
#     ],
#     "license": {
#       "type": "Trial",
#       "duration": "10 days left"
#     },
#     "lastPayment": "10 Jul, 2024",
#     "active": True,
#     "invoiceLink": "",
#     "lastLogin" : "2025-07-21T10:20:30Z"
#   },
#   {
#     "id": 11,
#     "name": "User 11",
#     "email": "user11@example.com",
#     "image": "/media/avatars/300-11.png",
#     "products": [
#       "Template",
#       "NFT"
#     ],
#     "license": {
#       "type": "Standard",
#       "duration": "11 days left"
#     },
#     "lastPayment": "11 Jul, 2024",
#     "active": False,
#     "invoiceLink": "",
#     "lastLogin" : "2025-12-21T10:20:30Z"
#   },
#   {
#     "id": 12,
#     "name": "User 12",
#     "email": "user12@example.com",
#     "image": "/media/avatars/300-12.png",
#     "products": [
#       "App",
#       "Widget"
#     ],
#     "license": {
#       "type": "Premium",
#       "duration": "12 months left"
#     },
#     "lastPayment": "12 Jul, 2024",
#     "active": True,
#     "invoiceLink": "",
#     "lastLogin" : "2025-12-05T10:20:30Z"
#   },
#   {
#     "id": 13,
#     "name": "User 13",
#     "email": "user13@example.com",
#     "image": "/media/avatars/300-13.png",
#     "products": [
#       "Template",
#       "NFT"
#     ],
#     "license": {
#       "type": "Trial",
#       "duration": "13 days left"
#     },
#     "lastPayment": "13 Jul, 2024",
#     "active": False,
#     "invoiceLink": ""
#   },
#   {
#     "id": 14,
#     "name": "User 14",
#     "email": "user14@example.com",
#     "image": "/media/avatars/300-14.png",
#     "products": [
#       "App",
#       "Widget"
#     ],
#     "license": {
#       "type": "Standard",
#       "duration": "14 days left"
#     },
#     "lastPayment": "14 Jul, 2024",
#     "active": True,
#     "invoiceLink": ""
#   },
#   {
#     "id": 15,
#     "name": "User 15",
#     "email": "user15@example.com",
#     "image": "/media/avatars/300-15.png",
#     "products": [
#       "Template",
#       "NFT"
#     ],
#     "license": {
#       "type": "Premium",
#       "duration": "15 months left"
#     },
#     "lastPayment": "15 Jul, 2024",
#     "active": False,
#     "invoiceLink": ""
#   },
#   {
#     "id": 16,
#     "name": "User 16",
#     "email": "user16@example.com",
#     "image": "/media/avatars/300-16.png",
#     "products": [
#       "App",
#       "Widget"
#     ],
#     "license": {
#       "type": "Trial",
#       "duration": "16 days left"
#     },
#     "lastPayment": "16 Jul, 2024",
#     "active": True,
#     "invoiceLink": ""
#   },
#   {
#     "id": 17,
#     "name": "User 17",
#     "email": "user17@example.com",
#     "image": "/media/avatars/300-17.png",
#     "products": [
#       "Template",
#       "NFT"
#     ],
#     "license": {
#       "type": "Standard",
#       "duration": "17 days left"
#     },
#     "lastPayment": "17 Jul, 2024",
#     "active": False,
#     "invoiceLink": ""
#   },
#   {
#     "id": 18,
#     "name": "User 18",
#     "email": "user18@example.com",
#     "image": "/media/avatars/300-18.png",
#     "products": [
#       "App",
#       "Widget"
#     ],
#     "license": {
#       "type": "Premium",
#       "duration": "18 months left"
#     },
#     "lastPayment": "18 Jul, 2024",
#     "active": True,
#     "invoiceLink": ""
#   },
#   {
#     "id": 19,
#     "name": "User 19",
#     "email": "user19@example.com",
#     "image": "/media/avatars/300-19.png",
#     "products": [
#       "Template",
#       "NFT"
#     ],
#     "license": {
#       "type": "Trial",
#       "duration": "19 days left"
#     },
#     "lastPayment": "19 Jul, 2024",
#     "active": False,
#     "invoiceLink": ""
#   },
#   {
#     "id": 20,
#     "name": "User 20",
#     "email": "user20@example.com",
#     "image": "/media/avatars/300-20.png",
#     "products": [
#       "App",
#       "Widget"
#     ],
#     "license": {
#       "type": "Standard",
#       "duration": "20 days left"
#     },
#     "lastPayment": "20 Jul, 2024",
#     "active": True,
#     "invoiceLink": ""
#   },
#   {
#     "id": 21,
#     "name": "User 21",
#     "email": "user21@example.com",
#     "image": "/media/avatars/300-21.png",
#     "products": [
#       "Template",
#       "NFT"
#     ],
#     "license": {
#       "type": "Premium",
#       "duration": "21 months left"
#     },
#     "lastPayment": "21 Jul, 2024",
#     "active": False,
#     "invoiceLink": ""
#   },
#   {
#     "id": 22,
#     "name": "User 22",
#     "email": "user22@example.com",
#     "image": "/media/avatars/300-22.png",
#     "products": [
#       "App",
#       "Widget"
#     ],
#     "license": {
#       "type": "Trial",
#       "duration": "22 days left"
#     },
#     "lastPayment": "22 Jul, 2024",
#     "active": True,
#     "invoiceLink": ""
#   },
#   {
#     "id": 23,
#     "name": "User 23",
#     "email": "user23@example.com",
#     "image": "/media/avatars/300-23.png",
#     "products": [
#       "Template",
#       "NFT"
#     ],
#     "license": {
#       "type": "Standard",
#       "duration": "23 days left"
#     },
#     "lastPayment": "23 Jul, 2024",
#     "active": False,
#     "invoiceLink": ""
#   },
#   {
#     "id": 24,
#     "name": "User 24",
#     "email": "user24@example.com",
#     "image": "/media/avatars/300-24.png",
#     "products": [
#       "App",
#       "Widget"
#     ],
#     "license": {
#       "type": "Premium",
#       "duration": "24 months left"
#     },
#     "lastPayment": "24 Jul, 2024",
#     "active": True,
#     "invoiceLink": ""
#   },
#   {
#     "id": 25,
#     "name": "User 25",
#     "email": "user25@example.com",
#     "image": "/media/avatars/300-25.png",
#     "products": [
#       "Template",
#       "NFT"
#     ],
#     "license": {
#       "type": "Trial",
#       "duration": "25 days left"
#     },
#     "lastPayment": "25 Jul, 2024",
#     "active": False,
#     "invoiceLink": ""
#   },
#   {
#     "id": 26,
#     "name": "User 26",
#     "email": "user26@example.com",
#     "image": "/media/avatars/300-26.png",
#     "products": [
#       "App",
#       "Widget"
#     ],
#     "license": {
#       "type": "Standard",
#       "duration": "26 days left"
#     },
#     "lastPayment": "26 Jul, 2024",
#     "active": True,
#     "invoiceLink": ""
#   },
#   {
#     "id": 27,
#     "name": "User 27",
#     "email": "user27@example.com",
#     "image": "/media/avatars/300-27.png",
#     "products": [
#       "Template",
#       "NFT"
#     ],
#     "license": {
#       "type": "Premium",
#       "duration": "27 months left"
#     },
#     "lastPayment": "27 Jul, 2024",
#     "active": False,
#     "invoiceLink": ""
#   },
#   {
#     "id": 28,
#     "name": "User 28",
#     "email": "user28@example.com",
#     "image": "/media/avatars/300-28.png",
#     "products": [
#       "App",
#       "Widget"
#     ],
#     "license": {
#       "type": "Trial",
#       "duration": "28 days left"
#     },
#     "lastPayment": "28 Jul, 2024",
#     "active": True,
#     "invoiceLink": ""
#   },
#   {
#     "id": 29,
#     "name": "User 29",
#     "email": "user29@example.com",
#     "image": "/media/avatars/300-29.png",
#     "products": [
#       "Template",
#       "NFT"
#     ],
#     "license": {
#       "type": "Standard",
#       "duration": "29 days left"
#     },
#     "lastPayment": "29 Jul, 2024",
#     "active": False,
#     "invoiceLink": ""
#   },
#   {
#     "id": 30,
#     "name": "User 30",
#     "email": "user30@example.com",
#     "image": "/media/avatars/300-30.png",
#     "products": [
#       "App",
#       "Widget"
#     ],
#     "license": {
#       "type": "Premium",
#       "duration": "30 months left"
#     },
#     "lastPayment": "30 Jul, 2024",
#     "active": True,
#     "invoiceLink": ""
#   },
#   {
#     "id": 31,
#     "name": "User 31",
#     "email": "user31@example.com",
#     "image": "/media/avatars/300-31.png",
#     "products": [
#       "Template",
#       "NFT"
#     ],
#     "license": {
#       "type": "Trial",
#       "duration": "31 days left"
#     },
#     "lastPayment": "31 Jul, 2024",
#     "active": False,
#     "invoiceLink": ""
#   }
# ]



    # filtered_users  = filterRepo.filterItems(users, criteria)
    
    # filtered_sorted_users = filterRepo.sortData(filtered_users, sorting)

    # data = rows[start:end]
    
    if not rows:
        raise HTTPException(
                  status_code=400, detail="Bad request: Not found"
          )

    resp = [user.UserOut(**row) async for row in rows  ]

    data = resp[start:end]

    
    
    return {
        "page": page,
        "page_size": page_size,
        "total_items": len(resp),
        "total_pages": math.ceil(len(resp) / page_size),
        "data": data,
    }   
      
@router.post("/create-user",  tags=["user"])
async def createUser( userCreate: user.UserCreate,  db: AsyncIOMotorClient =  Depends(get_database)):
    # students = await retrieve_students()
    # students = StudentSchema()
    # students = await conn["alex_office_admin"]["movie"].find({})
    userdb = await userRepo.getUserByEmail(db, userCreate.username)


    if userdb:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    newuser = await userRepo.createUser(db=db, create=userCreate)
   
    # if row:
    #     return Movie(**row)


@router.get("/orders/")
async def get_orders(
    page: int = Query(1, ge=1),  # Default page = 1
    page_size: int = Query(10, ge=1, le=100)  # Default page_size = 10
): 
    
    """
    API for fetching paginated Order.
    """
    
    start = (page - 1) * page_size
    end = start + page_size
    
    # ตัวอย่างข้อมูล
    orders = [
        {
            "Order": "#235325",
            "Purchased": "Calvin Klein T-shirts",
            "status": "Ready for pickup",
            "Customer": "Jase Marley",
            "Payment method": "Credit Card **** 1898",
            "Payment status": "Paid",
            "Items": 2
        },
        {
            "Order": "#646344",
            "Purchased": "Maroon Wedges",
            "status": "Fulfilled",
            "Customer": "Mathew Gustaffson",
            "Payment method": "Bank Transfer **** 5238",
            "Payment status": "Paid",
            "Items": 1
        },
        {
            "Order": "#547432",
            "Purchased": "Maroon Wedges",
            "status": "Fulfilled",
            "Customer": "Mathew Gustaffson",
            "Payment method": "Bank Transfer **** 8542",
            "Payment status": "Pending",
            "Items": 5
        },
        {
            "Order": "#624363",
            "Purchased": "Pattern Winter Sweater",
            "status": "Fulfilled",
            "Customer": "Nicky Olvsson",
            "Payment method": "PayPal ****@site.so",
            "Payment status": "Paid",
            "Items": 2
        },
        {
            "Order": "#989011",
            "Purchased": "White Blazer by Armani",
            "status": "Unfulfilled",
            "Customer": "David Nunez",
            "Payment method": "Credit Card **** 1284",
            "Payment status": "Pending",
            "Items": 1
        },
        {
            "Order": "#783109",
            "Purchased": "Watch",
            "status": "Fulfilled",
            "Customer": "Brian Jackson",
            "Payment method": "Credit Card **** 5522",
            "Payment status": "Partially refunded",
            "Items": 1
        },
        {
            "Order": "#823904",
            "Purchased": "Keyboard Matt",
            "status": "Ready for pickup",
            "Customer": "Jacky Ferguson",
            "Payment method": "Bank Transfer **** 9832",
            "Payment status": "Pending",
            "Items": 9
        },
        {
            "Order": "#490454",
            "Purchased": "Keyboard Matt",
            "status": "Ready for pickup",
            "Customer": "Karla Verdy",
            "Payment method": "PayPal ****@site.so",
            "Payment status": "Refunded",
            "Items": 5
        },
        {
            "Order": "#190931",
            "Purchased": "Nike Air Jordan 1 Yellow",
            "status": "Fulfilled",
            "Customer": "Karla Verdy",
            "Payment method": "PayPal ****@site.so",
            "Payment status": "Paid",
            "Items": 7
        }
    ]

    data = orders[start:end]
    
    return {
        "page": page,
        "page_size": page_size,
        "total_items": len(products),
        "total_pages": math.ceil(len(products) / page_size),
        "data": data,
    }
    
    
    