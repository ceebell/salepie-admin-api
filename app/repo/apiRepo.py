from passlib.context import CryptContext
from typing import List, Optional

# from loguru import logger
from models import user, schemas
from database.mongodb  import AsyncIOMotorClient, get_database
from utils import util
from datetime import datetime
from . import authRepo

from fastapi import APIRouter, Depends, HTTPException

import orjson



    
async def checkUnique( db: AsyncIOMotorClient, table : str, filed: str , value: str) -> bool:
    res = await db["genapi"][table].find_one({ filed :  { '$regex': f"^{value}$" , '$options': 'i' } })

    if res:
        return False #***  ถูกใช้แล้ว 
    else:
        return True #*** ยังไม่ถูกใช้งาน OK 
   

