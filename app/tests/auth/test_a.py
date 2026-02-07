import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from database.mongodb import AsyncIOMotorClient, get_database
from api.v1.endpoints import authApi
from passlib.context import CryptContext

# --- SETUP ---
app = FastAPI()
app.include_router(authApi.router, prefix="/auth")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def override_get_database():
    client = AsyncIOMotorClient("mongodb://admin:password@127.0.0.1:8999")
    try:
        # ต้องส่งค่า database กลับไป !!!
        yield client["salepiev1"] 
    finally:
        client.close()
# Override dependency
async def override_get_database():
    # Connect to real Mongo
    # NOTE: Ensure this connection string is correct for your environment
    client = AsyncIOMotorClient("mongodb://admin:password@127.0.0.1:27017")
    return client 

app.dependency_overrides[get_database] = override_get_database

# Helper function
async def prepare_test_user(db_client):
    user_data = {
        "username": "realuser@test.com",
        "hashedPassword": pwd_context.hash("RealPass#1234"),
        "isActive": True,
        "email": "realuser@test.com",
        "roles": ["user"]
    }
    # Use the same collection as the app: db["salepiev1"]["user"]
    await db_client["salepiev1"]["user"].insert_one(user_data)
    return user_data

async def cleanup_test_user(db_client):
    await db_client["salepiev1"]["user"].delete_one({"username": "realuser@test.com"})

# --- TEST CASE ---
@pytest.mark.asyncio
async def test_login_with_real_db():
    print("\nStarting test...")
    
    # 1. Connect to DB manually for setup/teardown
    db_client = await override_get_database()
    print("DB Client created")
    
    try:
        # 2. Cleanup first just in case
        print("Cleaning up...")
        await cleanup_test_user(db_client)
        print("Cleanup done")
        
        # 3. Prepare data
        print("Preparing user...")
        await prepare_test_user(db_client)
        print("User prepared")

        # 4. Call API using AsyncClient
        print("Starting AsyncClient...")
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            print("Sending POST request...")
            response = await client.post(
                "/auth/login",
                json={"username": "realuser@test.com", "password": "RealPass#1234"}
            )
            print(f"Response received: {response.status_code}")
            if response.status_code != 200:
                print(f"Error detail: {response.text}")

            # 5. Assert
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            print(f"\nLogin success! Token: {data['access_token'][:20]}...")

    finally:
        # 6. Cleanup
        print("Final cleanup...")
        await cleanup_test_user(db_client)
        print("Final cleanup done")