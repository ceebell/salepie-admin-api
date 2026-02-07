from typing import List, Optional

from pydantic import BaseModel,EmailStr , Json,Field, ValidationError, validator
from datetime import datetime, timedelta


class ClientInfoBase(BaseModel):
    id: Optional[str]
    clientId: str
    redirectUrl: str
    
    # is_active: Optional[bool]

class ClientInfoCreate(BaseModel):
    id: Optional[str]
    clientId: str
    redirectUrl: str
    
    # is_active: Optional[bool]




class ClientInfoDb(ClientInfoBase):
    id: Optional[str]
    clientId: str
    redirectUrl: str
    # password : Optional[str] = None
    isActive:  Optional[bool] = True
    # items: Optional[List[Item]] = []
    createDateTime: Optional[datetime] =  Field(default_factory=datetime.utcnow)
    updateDateTime: Optional[datetime] =  Field(default_factory=datetime.utcnow)
