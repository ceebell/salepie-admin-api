# app/api/api_v1/endpoints/items.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Json

router = APIRouter()

class Item(BaseModel):
    foobar: str = "foobar"
    foo: str
    bar: str = None

@router.post("/theitem")
async def thepost( newpost: Item):
    ALL_ITEMS = [Item(foo="foo0"), Item(foo="foo1"), Item(foo="foo2")]
    return ALL_ITEMS



@router.post("/item1")
async def thepost(ap : list):
    # ALL_ITEMS = [Item(foo="foo0"), Item(foo="foo1"), Item(foo="foo2")]
    return ap