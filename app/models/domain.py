from typing import List, Optional

from pydantic import BaseModel,EmailStr , Json,Field, ValidationError, validator
from datetime import datetime, timedelta


class DomainBase(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None

class DomainUpdate(DomainBase):
    update_datetime: datetime =  Field(default_factory=datetime.utcnow)


class DomainCreate(DomainBase):
    create_datetime: Optional[datetime]
    update_datetime: Optional[datetime] =  Field(default_factory=datetime.utcnow)

class DomainView(DomainBase):
    create_datetime: Optional[datetime]
    update_datetime: Optional[datetime]
    is_active: Optional[bool]

class DomainDb(DomainBase):
    id: Optional[str]
    title : Optional[str] = None
    is_active: bool
    items: Optional[List[Item]] = []
    create_datetime: Optional[datetime] =  Field(default_factory=datetime.utcnow)
    create_by:  Optional[str] = None
    update_datetime: Optional[datetime] =  Field(default_factory=datetime.utcnow)
    update_by:  Optional[str] = None
    class Config:
        orm_mode = True
