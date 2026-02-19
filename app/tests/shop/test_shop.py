import pytest
import logging
import json
from models import shopModel as shop

# ตั้งค่า Logger ให้เหมือนตัวอย่าง
logger = logging.getLogger("test.shop")

# =================================================================================
# 🏪 TEST CASE 1: Shop Info (Upsert & Get)
# =================================================================================
# [ShopInfo-1]
@pytest.mark.asyncio
async def test_shop_info_lifecycle(auth_client, db):
    """
    [Shop-1] & [Shop-2]
    Flow:
    1. POST /shop-info : เพื่อสร้างหรืออัปเดตข้อมูลร้านค้า
    2. เช็ค Response ว่าถูกต้อง
    3. เช็ค Database ว่าข้อมูลลงจริง
    4. GET /shop-info : เพื่อดึงข้อมูลมาตรวจสอบว่าตรงกับที่ Save ไหม
    """
    
    # ---------------------------------------------------------
    # 1. Prepare Data for POST (Upsert)
    # ---------------------------------------------------------
    payload = {
        "name": "Salepie Test Shop",
        "code": "TEST-SHOP-002",
        "phone": "0812345678",
        "line": "@salepietest",
        "description": "ร้านค้าสำหรับทดสอบระบบ Integration Test",
        "industry": "Fashion",  # Map กับ field 'Industry'
        "statusInfo": "Active"  # Map กับ field 'StatusInfo'
    }

    logger.info(f"\n🚀 [Step 1] Sending POST /shop-info with payload: {json.dumps(payload, ensure_ascii=False)}")

    # ---------------------------------------------------------
    # 2. Call API: POST /shop-info
    # ---------------------------------------------------------
    res_post = await auth_client.post("/shop/shop-info", json=payload)
    
    # Debug Error ถ้ามี
    if res_post.status_code != 200:
        logger.error(f"💥 Error POST Shop Info: {res_post.text}")

    assert res_post.status_code == 200, f"Expected 200 but got {res_post.status_code}"
    
    data_post = res_post.json()
    logger.info(f"✅ POST Response: {json.dumps(data_post, ensure_ascii=False)}")

    # Check Response Values
    assert data_post["name"] == payload["name"]
    assert data_post["code"] == payload["code"]
    shop_uid = data_post["uid"] # เก็บ uid ไว้เช็ค

    # ---------------------------------------------------------
    # 3. Verify in Database
    # ---------------------------------------------------------
    db_shop = await db["salepiev1"]["shopInfo"].find_one({"uid": shop_uid})
    assert db_shop is not None, "Data not found in MongoDB 'shopInfo' collection"
    assert db_shop["name"] == payload["name"]
    logger.info("\n🕵️‍♂️ Database Check: Found Shop Info correctly.")

    # ---------------------------------------------------------
    # 4. Call API: GET /shop-info
    # ---------------------------------------------------------
    logger.info("\n🚀 [Step 2] Sending GET /shop-info")
    res_get = await auth_client.get("/shop/shop-info")
    
    assert res_get.status_code == 200
    data_get = res_get.json()
    
    # Assert ว่าข้อมูลที่ Get ได้ ต้องตรงกับที่ Post ไป
    assert data_get["uid"] == shop_uid
    assert data_get["phone"] == payload["phone"]
    assert data_get["line"] == payload["line"]
    
    logger.info(f"✅ GET Response matches POST data.")


# =================================================================================
# 🏢 TEST CASE 2: ShopInfo Branch CRUD (Create -> List -> Update -> Delete)
# =================================================================================

# [Shop-2]
# ShopInfo Branch CRUD Flow (Create -> List -> Update -> Delete)
@pytest.mark.asyncio
async def test_branch_crud_flow(auth_client, db ):
    """
    [Branch-1] to [Branch-4]
    Flow:
    1. POST /branch     : สร้างสาขาใหม่
    2. GET /branch      : ดึง List มาดูว่าเจอสาขาที่สร้างไหม
    3. PUT /branch/{id} : แก้ไขชื่อสาขา
    4. DELETE /branch/{id} : ลบสาขา (Soft Delete)
    5. Check DB         : ตรวจสอบว่า field 'deleted' เป็น True
    """

    # ==========================================
    # 1. CREATE (POST)
    # ==========================================
    branch_payload = {
        "branchName": "Branch Central World",
        "code": "B-CTW",
        "address": "Bangkok, Pathum Wan",
        "phone": "02-999-9999",
        "State": True,
        "WorkingTime": "10:00 - 22:00"
    }

    logger.info(f"\n🚀 [Step 1] Creating Branch...")
    res_create = await auth_client.post("/shop/branch", json=branch_payload)
    
    assert res_create.status_code == 200
    new_branch = res_create.json()
    
    branch_uid = new_branch["uid"]
    logger.info(f"✅ Branch Created! UID: {branch_uid}")
    assert new_branch["branchName"] == branch_payload["branchName"]

    # ==========================================
    # 2. LIST (GET)
    # ==========================================
    logger.info(f"\n🚀 [Step 2] Listing Branches...")
    res_list = await auth_client.get("/shop/branch")


    # Debug Error ถ้าไม่ผ่าน 200
    if res_list.status_code != 200:
        logger.error(f"\n💥 Error Response: {res_list.text}")
    
    assert res_list.status_code == 200
    branches = res_list.json()

    
    # หาว่ามี branch_uid ที่เพิ่งสร้างอยู่ใน list ไหม
    found_branch = next((b for b in branches if b["uid"] == branch_uid), None)

    
    assert found_branch is not None, f"Branch {branch_uid} not found in list API"
    assert found_branch["code"] == "B-CTW"
    logger.info(f"✅ Found created branch in list.")

    # ==========================================
    # 3. UPDATE (PUT)
    # ==========================================
    update_payload = {
        "branchName": "Branch CTW (Renamed)", # เปลี่ยนชื่อ
        "code": "B-CTW-V2",                   # เปลี่ยน code
        "State": False                        # ปิดสาขา
    }
    
    logger.info(f"\n🚀 [Step 3] Updating Branch {branch_uid}...")
    res_update = await auth_client.put(f"/shop/branch/{branch_uid}", json=update_payload)
    
    assert res_update.status_code == 200
    updated_data = res_update.json()
    
    assert updated_data["branchName"] == "Branch CTW (Renamed)"
    assert updated_data["State"] is False
    
    # Double Check DB
    db_branch_updated = await db["salepiev1"]["branch"].find_one({"uid": branch_uid})
    assert db_branch_updated["branchName"] == "Branch CTW (Renamed)"
    logger.info(f"✅ Update successful and verified in DB.")

    # ==========================================
    # 4. DELETE (DELETE)
    # ==========================================
    logger.info(f"\n🚀 [Step 4] Deleting Branch {branch_uid}...")
    res_delete = await auth_client.delete(f"/shop/branch/{branch_uid}")
    
    assert res_delete.status_code == 200
    assert res_delete.json()["status"] == "success"
    
    # ==========================================
    # 5. VERIFY SOFT DELETE IN DB
    # ==========================================
    logger.info(f"\n🕵️‍♂️ [Step 5] Verifying Soft Delete in DB...")
    db_branch_final = await db["salepiev1"]["branch"].find_one({"uid": branch_uid})
    
    # ตรวจสอบว่า record ยังอยู่ แต่ deleted = True
    assert db_branch_final is not None, "Record should not be hard deleted"
    assert db_branch_final.get("deleted") is True, "Field 'deleted' must be True"
    
    logger.info("✅ Branch soft deleted successfully.")