from typing import List, Optional , Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from repo import  userRepo, authRepo

##### BEGIN : DATABSE #####

from models import  schemas, user, csharpModel
# from loguru import logger
from pydantic import BaseModel, Json ,ValidationError, validator, Field, EmailStr
from database.mongodb import AsyncIOMotorClient, get_database

from utils import util

from time import time
import httpx
import asyncio
import stripe

router = APIRouter()

from sqlmodel import Field, Session, SQLModel, create_engine


class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None


#******************************************
#*** [1.0] product item [admin , shop]
#******************************************
# @router.post("/productitems",  tags=["ecoupon"] )
# async def update_campaign( use : CouponUse ,  db: AsyncIOMotorClient =  Depends(get_database) ):



stripe.api_key = 'sk_test_51N4PWFFUW9r0xAOxMO0PjQTpC6mVPhklk0JqMTLdOWKnWkhjSS5nwwhVmRTyC27pXGmkZzeyJivodyirykMcO9xE00q73RiBV6'



#******************************************
#*** [90.1.1] stripe payment [admin , shop]
#******************************************
@router.post("/create-checkout-session",  tags=["arisa"] )
async def create_checkout_session():
    intent = stripe.PaymentIntent.create(
        payment_method_types=["card","promptpay"],
        amount=1000,
        currency="thb",
        )

    return intent


#******************************************
#*** [90.2.1] stripe create customer [admin , shop]
#******************************************
@router.post("/stripe-create-customer",  tags=["arisa"] )
async def stripe_create_customers():
    stripe.Customer.create(
        name="Sandy Charon",
        email="sandycharon@example.com",
        )

    return "OK"


#******************************************
#*** [90.2.2] stripe retrieve customers [admin , shop]
#******************************************
@router.post("/stripe-retrieve-customers",  tags=["arisa"] )
async def stripe_create_customers():

    return stripe.Customer.list(limit=10)