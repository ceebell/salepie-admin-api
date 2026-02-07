import pytest
from httpx import AsyncClient, ASGITransport

from main import app
from database.mongodb import get_database
from api.v1.endpoints.authApi import pwd_context,SECRET_KEY, ALGORITHM
from jose import jwt
# import jwt

# @pytest.mark.asyncio
# async def test_login_without_conftest():

#     # -------------------------------
#     # 1) บังคับให้ FastAPI รัน startup()
#     # -------------------------------
#     await app.router.startup()

#     # -------------------------------
#     # 2) Override get_database → ใช้ DB จริง
#     # -------------------------------
#     async def override_get_database():
#         return await get_database()  # เรียก DB จริง

#     app.dependency_overrides[get_database] = override_get_database

#     # -------------------------------
#     # 3) สร้าง HTTPX AsyncClient
#     # -------------------------------
#     async with AsyncClient(
#         transport=ASGITransport(app=app),
#         base_url="http://test"
#     ) as client:

#         # -------------------------------
#         # 4) ยิง API login
#         # -------------------------------
#         response = await client.post(
#             "/auth/login",
#             json={"email": "arina@example.com", "password": "Arina#2025"}
#         )

#         # -------------------------------
#         # 5) ตรวจสอบผล
#         # -------------------------------
#         assert response.status_code == 200
#         assert "access_token" in response.json()

#     # -------------------------------
#     # 6) shutdown + clear overrides
#     # -------------------------------
#     await app.router.shutdown()
#     app.dependency_overrides.clear()



@pytest.mark.asyncio
async def test_login_success(client):
    
  
    # 2. ยิง API (ใช้ client ที่ conftest เตรียมมาให้)
    response = await client.post(
        "/auth/login",
        json={"email": "arina@example.com", "password": "Arina#2025"}
    )

    # 3. ตรวจสอบผล
    assert response.status_code == 200
    res_json = response.json()
    assert "access_token" in res_json
    
    print("\nLogin สำเร็จ! และเดี๋ยวข้อมูลจะถูกลบเองอัตโนมัติ")

@pytest.mark.asyncio
async def test_login_email_notfound(client):
    
   
    # 2. ยิง API (ใช้ client ที่ conftest เตรียมมาให้)
    response = await client.post(
        "/auth/login",
        json={"email": "arin@example.com", "password": "Arina#2025"}
    )

    # 3. ตรวจสอบผล
    assert response.status_code == 401
    res_json = response.json()
    assert "detail" in res_json
    assert res_json["detail"] == "Incorrect email or password"
    
    print("\nLogin Failed!")


@pytest.mark.asyncio
async def test_login_with_wrong_password(client):
    
   
    # 2. ยิง API (ใช้ client ที่ conftest เตรียมมาให้)
    response = await client.post(
        "/auth/login",
        json={"email": "arina@example.com", "password": "2025"}
    )

    # 3. ตรวจสอบผล
    assert response.status_code == 401
    res_json = response.json()
    assert "detail" in res_json
    assert res_json["detail"] == "Incorrect email or password"
    

@pytest.mark.asyncio
async def test_login_email_not_match_email_pattern(client):
    
   
    # 2. ยิง API (ใช้ client ที่ conftest เตรียมมาให้)
    response = await client.post(
        "/auth/login",
        json={"email": "arina@example", "password": "2025"}
    )

    # 3. ตรวจสอบผล
    assert response.status_code == 422
    res_json = response.json()
    print("res_json ",res_json)
    # assert "detail" in res_json
    # assert res_json["detail"] == "Incorrect email or password"
    


@pytest.mark.asyncio
async def test_login_user_inactivate(client):
    
   
    # 2. ยิง API (ใช้ client ที่ conftest เตรียมมาให้)
    response = await client.post(
        "/auth/login",
        json={"email": "arina@example", "password": "2025"}
    )

    # 3. ตรวจสอบผล
    assert response.status_code == 422
    res_json = response.json()
    print("res_json ",res_json)
    # assert "detail" in res_json
    # assert res_json["detail"] == "Incorrect email or password"
    



@pytest.mark.asyncio
async def test_login_token_decode_able(client):
    
   
    # 2. ยิง API (ใช้ client ที่ conftest เตรียมมาให้)
    response = await client.post(
        "/auth/login",
        json={"email": "arina@example.com", "password": "Arina#2025"}
    )

    email = "arina@example.com"

    assert response.status_code == 200

    # -----------------------------
    # 5) ตรวจสอบ cookie
    # -----------------------------
    cookies = response.cookies

    print("\ncookies:", cookies)

    # Cookie ชื่อ Authorization ต้องมี
    # assert "Authorization" in cookies

    raw_cookie = cookies.get("Authorization")

    print("\nraw_cookie:", raw_cookie)
    print("\nraw_cookie type:", type(raw_cookie))

    # --- ค่า cookie ต้องขึ้นต้นด้วย Bearer
    # assert raw_cookie.startswith("Bearer ")

    # --- แยก token ออกมา
    token = raw_cookie.replace("Bearer ", "").strip(    )
    # แก้จุดสำคัญ — ลบ double quotes
    raw_cookie = raw_cookie.replace('\"','')
    token = raw_cookie.replace("Bearer ", "")
    print("\token:", token)
    # assert token != ""

    print("\n SECRET_KEY:", SECRET_KEY)
    print("\n ALGORITHM:", ALGORITHM)
  
    header = jwt.get_unverified_header(token)
    print(header)
    # -----------------------------
    # 6) Decode Token ตรวจสอบค่า
    # -----------------------------
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print("\payload:", payload)
    assert payload["email"] == email
    assert "exp" in payload
    # assert "iat" in payload

    # print("Cookie:", raw_cookie)
    # print("Decoded token:", payload)
    

