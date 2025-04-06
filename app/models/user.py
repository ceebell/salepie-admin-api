from typing import List, Optional

from pydantic import BaseModel,EmailStr , Json,Field, ValidationError, validator
from datetime import datetime, timedelta


class UserBase(BaseModel):
    username: EmailStr
    # is_active: Optional[bool]

class UserUpdate(UserBase):
    password: Optional[str]
    isActive: Optional[bool]

class UserCreate(UserBase):
    # username: EmailStr
    password: str
    
class SocialRegister(BaseModel):
    username: EmailStr
    userType: Optional[str] = None 
    description: Optional[str] = None


class UserImage(BaseModel):
    uid: Optional[str] = None
    name: Optional[str] = None
    createAt: Optional[datetime]
    updateAt: Optional[datetime]

class UserView(UserBase):
    activeToken: Optional[str] = None
    images: Optional[List[UserImage]] = []
    createAt: Optional[datetime]
    updateAt: Optional[datetime]
    isActive: Optional[bool]
    domainId: Optional[str] = None 
    admin: Optional[bool] = False




class UserDb(UserBase):
    uid: Optional[str]
    username: Optional[str]
    # password : Optional[str] = None
    isActive:  Optional[bool] = True
    deleted:  Optional[bool] = False
    userType: Optional[str] = None
    description: Optional[str] = None
    images: Optional[List[UserImage]] = []
    hashedPassword: Optional[str] = None
    activeToken: Optional[str] = None 
    tokenExpiredAt: Optional[datetime] = None
    googleToken: Optional[str] = None 
    googleTokenExpiredAt: Optional[datetime] = None
    createAt: Optional[datetime] =  Field(default_factory=datetime.utcnow)
    update_At: Optional[datetime] =  Field(default_factory=datetime.utcnow)
    domainId: Optional[str] = None 
    admin: Optional[bool] = False

    # class Config:
    #     orm_mode = True
    
    
class UserLoginResponse(UserBase):
    uid: Optional[str]
    isActive:  Optional[bool] = True
    # accessToken: Optional[str] = None 
    tokenExpiredAt: Optional[datetime] = None
    createAt: Optional[datetime] =  None
    update_At: Optional[datetime] =  None
    domainId: Optional[str] = None 
    admin: Optional[bool] = False

class UserOut(UserBase):
    uid: Optional[str]
    isActive:  Optional[bool] = True
    accessToken: Optional[str] = None 
    tokenExpiredAt: Optional[datetime] = None
    createAt: Optional[datetime] =  None
    update_At: Optional[datetime] =  None
    domainId: Optional[str] = None 
    admin: Optional[bool] = False
    
class UserForView(UserBase):
    uid: Optional[str]
    isActive:  Optional[bool] = True
    tokenExpiredAt: Optional[datetime] = None
    createAt: Optional[datetime] =  None
    update_At: Optional[datetime] =  None
    domainId: Optional[str] = None 
    admin: Optional[bool] = False
    
    
    
class SearchForm(BaseModel):
    uid: Optional[str] = "" 
    page : Optional[int] = 1
    pageSize : Optional[int] = 10
    searchText: Optional[str] = "" 
    domainId: Optional[str] = "" 
    status: Optional[str] = ""
    admin: Optional[bool] = False
    
