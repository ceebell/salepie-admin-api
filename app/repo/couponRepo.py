from typing import List, Optional
from pydantic import BaseModel, Json ,ValidationError, validator, Field, EmailStr

# from loguru import logger
from models import user, schemas
from database.mongodb  import AsyncIOMotorClient, get_database
from utils import util

from datetime import datetime, date
from dateutil.parser import parse

from . import authRepo, utilRepo

from fastapi import APIRouter, Depends, HTTPException, UploadFile

import json
import uuid

