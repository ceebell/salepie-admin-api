import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from database.mongodb import AsyncIOMotorClient, get_database
# *** เปลี่ยน import app ให้ตรงกับไฟล์ที่ประกาศ FastAPI ของคุณ ***
# เช่นถ้า app อยู่ใน main.py ก็ from main import app
# หรือถ้าอยู่ใน authApi.py ก็ from authApi import app
from database.mongodb import get_database

from httpx import AsyncClient
from httpx import ASGITransport

from main import app   
from database.mongodb import get_database

# @pytest.fixture
# async def auth_client(client):
#     # ยิง login เพื่อให้ได้ cookie
#     login_res = await client.post(
#         "/auth/login",
#         json={
#             "email": "arina@example.com",
#             "password": "Arina#2025"
#         }
#     )

#     # ดึง cookie ที่ server set มา
#     auth_cookie = login_res.cookies.get("Authorization")
#     assert auth_cookie is not None, "Login failed: no cookie received"

#     print("Auth Cookie:", auth_cookie)

#     # **เก็บ cookie ใส่ client เอาไว้ (สำคัญ!)**
#     client.cookies.set("Authorization", auth_cookie)

#     return client


# tests/conftest.py

# ✅ Fixture สำหรับส่ง Database Object ให้ Test Function









@pytest.fixture
async def db():
    return await get_database()

@pytest.fixture
async def auth_client(client):
    # 1. ลอง Login
    login_data = {
        "email": "arina@example.com",
        "password": "Arina#2025"
    }
    
    login_res = await client.post("/auth/login", json=login_data)

    # --- เพิ่มส่วนนี้เพื่อ Debug ---
    # print(f"\n[DEBUG] S
    # tatus Code: {login_res.status_code}")
    # print(f"[DEBUG] Response Body: {login_res.text}")
    # print(f"[DEBUG] Cookies received: {login_res.cookies}") 
    # ---------------------------

    # เช็คว่า Login ผ่านจริงไหม (สำคัญ!)
    if login_res.status_code != 200:
        pytest.fail(f"Login Failed! Status: {login_res.status_code}, Body: {login_res.text}")

    # ลองดึง Cookie (ถ้าชื่อไม่ใช่ Authorization ให้ดูจาก Log [DEBUG] Cookies received ข้างบน)
    # สมมติว่าใน Log เห็นชื่อ 'access_token' ก็ต้องแก้ตรงนี้เป็น 'access_token'
    auth_cookie = login_res.cookies.get("Authorization") 
    
    # ถ้ายังหาไม่เจอ ให้ลองดูว่า Token อยู่ใน Body หรือเปล่า
    if not auth_cookie:
        # ลองแกะจาก JSON เผื่อ server ส่งมาเป็น Body
        try:
            data = login_res.json()
            # สมมติถ้าอยู่ใน body ให้เอามา set ใส่ cookie เอง (เพื่อให้ client จำ)
            if "access_token" in data:
                 token = data["access_token"]
                 client.cookies.set("Authorization", f"Bearer {token}")
                 return client
        except:
            pass

    assert auth_cookie is not None, f"No cookie found! Client cookies: {client.cookies}"
    
    # ถ้า Client ฉลาดพอ มันอาจจะ set cookie ให้แล้ว เราแค่ return client
    return client


@pytest_asyncio.fixture(scope="function")
async def client():
    # -------------------------------
    # 1) บังคับให้ FastAPI รัน startup()
    # -------------------------------
    await app.router.startup()
    # -------------------------------
    # 2) Override get_database → ใช้ DB จริง
    # -------------------------------
    async def override_get_database():
        return await get_database()  # เรียก DB จริง

    app.dependency_overrides[get_database] = override_get_database

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    await app.router.shutdown()  # ← shutdown event