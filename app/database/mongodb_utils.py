import logging

from motor.motor_asyncio import AsyncIOMotorClient
from core.config import MONGODB_URL, MAX_CONNECTIONS_COUNT, MIN_CONNECTIONS_COUNT
from .mongodb import db


async def connect_to_mongo():
    db.client = AsyncIOMotorClient(str(MONGODB_URL)
                                 )


async def close_mongo_connection():
    db.client.close()
