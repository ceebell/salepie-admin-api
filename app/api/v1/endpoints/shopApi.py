from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from database.mongodb import AsyncIOMotorClient, get_database
from repo import authRepo
from models import user
from models import shopModel as shop # Import models ที่สร้างข้างบน
from utils import util
from utils.datetime_util import now
import logging

router = APIRouter()
logger = logging.getLogger("salepie.shop")

# =========================================================
# [Shop] Get / Update Shop Info
# =========================================================

# [Shop-1]
@router.get("/shop-info", response_model=shop.ShopInfoOut, tags=["Shop"])
async def get_shop_info(
    db: AsyncIOMotorClient = Depends(get_database),
    currentUser: user.UserDb = Depends(authRepo.get_current_active_user)
):
    # ใช้ domainId ของ user เป็น uid ของ ShopInfo
    doc = await db["salepiev1"]["shopInfo"].find_one({"uid": currentUser.domainId})
    if not doc:
        raise HTTPException(status_code=404, detail="Shop info not found")
    
    if "_id" in doc: doc.pop("_id")
    return shop.ShopInfoOut(**doc)

# [Shop-2]
@router.post("/shop-info", response_model=shop.ShopInfoOut, tags=["Shop"])
async def upsert_shop_info(
    req: shop.ShopInfoReq,
    db: AsyncIOMotorClient = Depends(get_database),
    currentUser: user.UserDb = Depends(authRepo.get_current_active_user)
):
    current_time = now()
    shop_uid = currentUser.domainId

    # เช็คว่ามีอยู่แล้วไหม
    existing = await db["salepiev1"]["shopInfo"].find_one({"uid": shop_uid})

    if existing:
        # Update
        update_data = req.model_dump(exclude_unset=True)
        update_data.update({
            "updateBy": currentUser.email,
            "updateDateTime": current_time
        })
        
        await db["salepiev1"]["shopInfo"].update_one(
            {"uid": shop_uid},
            {"$set": update_data}
        )
        # Fetch updated
        doc = await db["salepiev1"]["shopInfo"].find_one({"uid": shop_uid})
    else:
        # Create New
        new_shop = shop.ShopInfoDB(
            **req.model_dump(),
            uid=shop_uid,
            createBy=currentUser.email,
            updateBy=currentUser.email
        )
        await db["salepiev1"]["shopInfo"].insert_one(new_shop.model_dump())
        doc = new_shop.model_dump()

    if "_id" in doc: doc.pop("_id")
    return shop.ShopInfoOut(**doc)


# =========================================================
# [Branch] Branch CRUD
# =========================================================

# [Branch-1] 
@router.post("/branch", response_model=shop.BranchOut, tags=["Shop-Branch"])
async def create_branch(
    req: shop.BranchReq,
    db: AsyncIOMotorClient = Depends(get_database),
    currentUser: user.UserDb = Depends(authRepo.get_current_active_user)
):
    new_uid = str(util.getUuid())
    
    branch_db = shop.BranchDB(
        **req.model_dump(),
        uid=new_uid,
        shopInfoId=currentUser.domainId, # Link กับ Shop
        createBy=currentUser.email,
        updateBy=currentUser.email
    )

    
    res = await db["salepiev1"]["branch"].insert_one(branch_db.model_dump())
    if not res.acknowledged:
        raise HTTPException(status_code=500, detail="Failed to create branch")
    logger.info("A new Branch was saved")
        
    return branch_db


# [Branch-2] 
@router.get("/branch", response_model=List[shop.BranchOut], tags=["Shop-Branch"])
async def list_branches(
    db: AsyncIOMotorClient = Depends(get_database),
    currentUser: user.UserDb = Depends(authRepo.get_current_active_user)
):
    cursor = db["salepiev1"]["branch"].find({
        "shopInfoId": currentUser.domainId,
        "deleted": {"$ne": True}
    })
    branches = await cursor.to_list(length=100)

    logger.info("Calling branch list")
    
    results = []
    for b in branches:
        if "_id" in b: b.pop("_id")
        results.append(shop.BranchOut(**b))
        
    return results

    
# [Branch-3] 
@router.put("/branch/{uid}", response_model=shop.BranchOut, tags=["Shop-Branch"])
async def update_branch(
    uid: str,
    req: shop.BranchReq,
    db: AsyncIOMotorClient = Depends(get_database),
    currentUser: user.UserDb = Depends(authRepo.get_current_active_user)
):
    # ตรวจสอบความเป็นเจ้าของ
    existing = await db["salepiev1"]["branch"].find_one({"uid": uid, "shopInfoId": currentUser.domainId})
    if not existing:
        raise HTTPException(status_code=404, detail="Branch not found")

    update_data = req.model_dump(exclude_unset=True)
    update_data.update({
        "updateBy": currentUser.email,
        "updateDateTime": now()
    })

    await db["salepiev1"]["branch"].update_one(
        {"uid": uid},
        {"$set": update_data}
    )
    
    updated_doc = await db["salepiev1"]["branch"].find_one({"uid": uid})
    if "_id" in updated_doc: updated_doc.pop("_id")
    
    return shop.BranchOut(**updated_doc)

# [Branch-4] 
@router.delete("/branch/{uid}", tags=["Shop-Branch"])
async def delete_branch(
    uid: str,
    db: AsyncIOMotorClient = Depends(get_database),
    currentUser: user.UserDb = Depends(authRepo.get_current_active_user)
):
    # Soft Delete
    res = await db["salepiev1"]["branch"].update_one(
        {"uid": uid, "shopInfoId": currentUser.domainId},
        {"$set": {
            "deleted": True,
            "updateBy": currentUser.email,
            "updateDateTime": now()
        }}
    )
    if res.modified_count == 0:
        raise HTTPException(status_code=404, detail="Branch not found or already deleted")
        
    return {"status": "success", "message": "Branch deleted"}


# =========================================================
# [Shop-3] Shop Setting
# =========================================================
@router.post("/shop-setting", response_model=shop.ShopSettingOut, tags=["Shop-Setting"])
async def save_shop_setting(
    req: shop.ShopSettingReq,
    db: AsyncIOMotorClient = Depends(get_database),
    currentUser: user.UserDb = Depends(authRepo.get_current_active_user)
):
    shop_id = currentUser.domainId
    existing = await db["salepiev1"]["shopSetting"].find_one({"shopInfoId": shop_id})
    
    if existing:
        # Update
        await db["salepiev1"]["shopSetting"].update_one(
            {"shopInfoId": shop_id},
            {"$set": {
                **req.model_dump(),
                "updateBy": currentUser.email,
                "updateDateTime": now()
            }}
        )
        doc = await db["salepiev1"]["shopSetting"].find_one({"shopInfoId": shop_id})
    else:
        # Create
        new_setting = shop.ShopSettingDB(
            **req.model_dump(),
            uid=str(util.getUuid()),
            shopInfoId=shop_id,
            createBy=currentUser.email,
            updateBy=currentUser.email
        )
        await db["salepiev1"]["shopSetting"].insert_one(new_setting.model_dump())
        doc = new_setting.model_dump()
        
    if "_id" in doc: doc.pop("_id")
    return shop.ShopSettingOut(**doc)

@router.get("/shop-setting", response_model=shop.ShopSettingOut, tags=["Shop-Setting"])
async def get_shop_setting(
    db: AsyncIOMotorClient = Depends(get_database),
    currentUser: user.UserDb = Depends(authRepo.get_current_active_user)
):
    doc = await db["salepiev1"]["shopSetting"].find_one({"shopInfoId": currentUser.domainId})
    if not doc:
        # Return default or 404 depends on logic, here create default
        return shop.ShopSettingOut(
            uid=str(util.getUuid()),
            shopInfoId=currentUser.domainId,
            createBy="system",
            updateBy="system"
        )
        
    if "_id" in doc: doc.pop("_id")
    return shop.ShopSettingOut(**doc)


# =========================================================
# [Shop-4] Shop Package
# =========================================================
@router.get("/shop-package", response_model=List[shop.ShopPackageOut], tags=["Shop-Package"])
async def get_shop_packages(
    db: AsyncIOMotorClient = Depends(get_database),
    currentUser: user.UserDb = Depends(authRepo.get_current_active_user)
):
    cursor = db["salepiev1"]["shopPackage"].find({"shopInfoId": currentUser.domainId})
    docs = await cursor.to_list(length=100)
    
    results = []
    for d in docs:
        if "_id" in d: d.pop("_id")
        results.append(shop.ShopPackageOut(**d))
    return results

# Example Add Package (Admin or System logic usually, but here is user context)
@router.post("/shop-package", response_model=shop.ShopPackageOut, tags=["Shop-Package"])
async def add_shop_package(
    req: shop.ShopPackageReq,
    db: AsyncIOMotorClient = Depends(get_database),
    currentUser: user.UserDb = Depends(authRepo.get_current_active_user)
):
    new_pkg = shop.ShopPackageDB(
        **req.model_dump(),
        uid=str(util.getUuid()),
        shopInfoId=currentUser.domainId,
        createBy=currentUser.email,
        updateBy=currentUser.email
    )
    
    await db["salepiev1"]["shopPackage"].insert_one(new_pkg.model_dump())
    return new_pkg