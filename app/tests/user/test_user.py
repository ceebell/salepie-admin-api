import pytest
from httpx import AsyncClient, ASGITransport

from main import app
from database.mongodb import get_database
from api.v1.endpoints.authApi import pwd_context,SECRET_KEY, ALGORITHM
from jose import jwt
import pydantic
print(pydantic.VERSION)
import json


NEW_USER_ID = ""

@pytest.mark.asyncio
async def test_createUser_success(client):
    
    # [1. create user]
    user_data = {
        # "uid": "8b16f0cb-3ac2-4cc6-94e8-89ac120fb9b0",
        "email": "emily5@salepie.com",
        "firstName": "Emily5",
        "lastName": "Johnson",
        "address": "123 Main St, Cityville",
        "phone": "123-456-7890",
        "roles": ["customer"], 
        "isActive": True,
        "deleted": False,
        "domainId": "domain123"
    }

    json_text = json.dumps(user_data)

    print("\nCreating user with data:", type(json_text))

    response = await client.post(
        "/user/create-staff",
        json=user_data

    )

    # # 3. ตรวจสอบผล
    assert response.status_code == 200
    # res_json = response.json()
    # assert "access_token" in res_json
    
    # print("\nLogin สำเร็จ! และเดี๋ยวข้อมูลจะถูกลบเองอัตโนมัติ")


# [2. create duplicated user]
@pytest.mark.asyncio
async def test_createUser_duplicated(auth_client):
    
    theTrue = True
    theFalse = False
    # 2. ยิง API (ใช้ client ที่ conftest เตรียมมาให้)json=
    user_data = {
        "email": "Arbigale@salepie.com",
        "password": "Arbigale#2026",
        "firstName": "Arbigale",
        "lastName": "Johnson",
        "address": "123 Main St, Cityville",
        "phone": "081-878-5645",
        "status": "active",
        "roles": ["customer"], 
        "isActive": theTrue,
        "deleted": theFalse,
        "domainId": "domain123"
    }

    json_text = json.dumps(user_data)

    print("\nCreating user with data:", type(json_text))

    response = await auth_client.post(
        "/user/create-staff",
        json=user_data

    )

    # # 3. ตรวจสอบผล
    assert response.status_code == 400
    # res_json = response.json()
    # assert "access_token" in res_json
    
    # print("\nLogin สำเร็จ! และเดี๋ยวข้อมูลจะถูกลบเองอัตโนมัติ")

# [u-2] /soft-delete/{uid}
@pytest.mark.asyncio
async def test_user_softDelete(auth_client):
    
    userId = "92a12df2-abe2-4994-b813-eaf5fa283f41"
    response = await auth_client.post(
        f"/user/soft-delete/{userId}",
        json={}

    )

    # # 3. User must not be found after soft deleted
    assert response.status_code == 200
    

    resp_getUser = await auth_client.get(
        f"/user/get-user-by-id/{userId}"
    )

    # print("\nGet User after soft delete:", resp_getUser.status_code, resp_getUser.text)

    # # 3. User must not be found after soft deleted
    assert resp_getUser.status_code == 404
    
    # print("\nLogin สำเร็จ! และเดี๋ยวข้อมูลจะถูกลบเองอัตโนมัติ")

# --- คนละ Domain คนละร้านกัน
# [u-4] /get-user-by-id/{uid}
@pytest.mark.asyncio
async def test_user_by_user_id_after_softDelete(auth_client):
    
    userId = "f02911ff-e3a9-40d8-a90a-6776e236c4cb"
    response = await auth_client.get(
        f"/user/get-user-by-id/{userId}"
    )

    # # 3. ตรวจสอบผล
    assert response.status_code == 404

# --- get user ร้านเดียวกัน
# [u-5] /get-user-by-id
@pytest.mark.asyncio
async def test_user_by_user_id_sameDomain(auth_client):
    

    # jennifer5@salepie.com
    userId = "92a12df2-abe2-4994-b813-eaf5fa283f41"
    act = True
    response = await auth_client.post(
        f"/user/change-user-active",
        json={
            "uid": userId,
            "isActive": act
        }
    )

    # # 3. ตรวจสอบผล
    assert response.status_code == 200

    # assert "email" in response.json()
    # assert "email" in response.json()


# --- change user active
# [u-6] /edit-my-profile
@pytest.mark.asyncio
async def test_edit_my_profile(auth_client):
    


    userId = "12614fe6-6def-445c-aef6-689d1d7a80a2"
    response = await auth_client.post(
        f"/user/edit-my-profile",
        json = {
            "firstName": "Airna_Michael",
            "lastName": "Smith",
            "address": "456 Oak St, Townsville",
            "phone": "987-654-3210",
            "roles": ["owner", "staff"],
            "isActive": True,
            "deleted": False,
        }
    )

    # # 3. ตรวจสอบผล
    assert response.status_code == 200

    # assert "email" in response.json()


    # --- change user active
# [u-6] /edit-my-profile
# @pytest.mark.asyncio
# async def test_edit_my_profile(auth_client):
    


#     userId = "4290049e-460d-40d5-9322-4e91d575f2c8"
#     response = await auth_client.post(
#         f"/user/edit-my-profile"
#     )

#     # # 3. ตรวจสอบผล
#     assert response.status_code == 200

#     assert "email" in response.json()