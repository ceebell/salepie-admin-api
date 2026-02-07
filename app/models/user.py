from typing import List, Optional

from pydantic import field_validator, ConfigDict, BaseModel,EmailStr , Json,Field, ValidationError, validator
from datetime import datetime, timedelta
import uuid
from utils.datetime_util  import now

class UserBase(BaseModel):
    email: EmailStr
    # is_active: Optional[bool]

class UserUpdate(UserBase):
    password: Optional[str]
    isActive: Optional[bool]

class UserImage(BaseModel):
    seq: Optional[int] = None
    dataUrl: Optional[str] = None
    filename: Optional[str] = None
    description: Optional[str] = None
    getUrl: Optional[str] = None
    path: Optional[str] = None
    deleted: Optional[bool] = False

class UserImageIn(BaseModel):
    seq: Optional[int] = None
    dataUrl: Optional[str] = None
    filename: Optional[str] = None
    description: Optional[str] = None
    getUrl: Optional[str] = None
    path: Optional[str] = None
    deleted: Optional[bool] = False
    
class UserForm(BaseModel):
    email: Optional[EmailStr]
    password: Optional[str]
    rememberMe: Optional[bool] = False


class UserCreate(BaseModel):
    email: EmailStr
    # password: Optional[str]
    # uid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    firstName: Optional[str] = ""
    lastName: Optional[str] = ""
    address: Optional[str]= ""
    # email: Optional[EmailStr]
    phone: Optional[str]= ""
    isActive:  Optional[bool] = True
    status:  Optional[str] = "Active"
    # deleted:  Optional[bool] = False
    # userType: Optional[str] = None
    roles: Optional[List[str]] = [] 
    description: Optional[str] = None
    images: Optional[List[UserImage]] = []
    # hashedPassword: Optional[str] = None
    # activeToken: Optional[str] = None 
    # tokenExpiredAt: Optional[datetime] = None
    # googleToken: Optional[str] = None 
    # googleTokenExpiredAt: Optional[datetime] = None
    # createDateTime: Optional[datetime] =  Field(default_factory=datetime.utcnow)
    # updateDateTime: Optional[datetime] =  Field(default_factory=datetime.utcnow)
    # lastLogin: Optional[datetime] = None
    domainId: Optional[str] = None 
    # admin: Optional[bool] = False

    
class SocialRegister(BaseModel):
    email: EmailStr
    userType: Optional[str] = None 
    description: Optional[str] = None




class UserView(UserBase):
    activeToken: Optional[str] = None
    images: Optional[List[UserImage]] = []
    createDateTime: Optional[datetime]
    updateAt: Optional[datetime]
    isActive: Optional[bool]
    domainId: Optional[str] = None 
    # admin: Optional[bool] = False




class UserDb(UserBase):
    ConfigDict(extra="ignore")  
    # password : Optional[str] = None
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    firstName: Optional[str]
    lastName: Optional[str]
    address: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    isActive:  Optional[bool] = True
    status:  Optional[str] = ""
    deleted:  Optional[bool] = False
    userType: Optional[str] = None
    roles: Optional[List[str]] = [] 
    description: Optional[str] = None
    images: Optional[List[UserImage]] = []
    hashedPassword: Optional[str] = None
    activeToken: Optional[str] = None 
    tokenExpiredAt: Optional[datetime] = None
    googleToken: Optional[str] = None 
    googleTokenExpiredAt: Optional[datetime] = None
    createDateTime: Optional[datetime] =  None
    updateDateTime: Optional[datetime] =  None
    lastLogin: Optional[datetime] = None
    domainId: Optional[str] = None 
    # admin: Optional[bool] = False

    @field_validator("createDateTime", "updateDateTime", mode="before")
    @classmethod
    def set_dt(cls, v):
        return v or now()
    # class Config:
    #     orm_mode = True
    
    
class UserLoginResponse(UserBase):
    ConfigDict(extra="ignore") 
    uid: Optional[str]
    isActive:  Optional[bool] = True
    # accessToken: Optional[str] = None 
    tokenExpiredAt: Optional[datetime] = None
    createDateTime: Optional[datetime] =  None
    updateDateTime: Optional[datetime] =  None
    domainId: Optional[str] = None 
    # admin: Optional[bool] = False

class UserOut(UserBase):
    ConfigDict(extra="ignore") 
    email: EmailStr
    # password: str
    uid: Optional[str]
    firstName: Optional[str]
    lastName: Optional[str]
    address: Optional[str]
    # email: Optional[EmailStr]
    phone: Optional[str]
    isActive:  Optional[bool] = True
    status: Optional[str] = None
    # deleted:  Optional[bool] = False
    # userType: Optional[str] = None
    roles: Optional[List[str]] = [] 
    description: Optional[str] = None
    images: Optional[List[UserImage]] = []
    # hashedPassword: Optional[str] = None
    # activeToken: Optional[str] = None 
    # tokenExpiredAt: Optional[datetime] = None
    # googleToken: Optional[str] = None 
    # googleTokenExpiredAt: Optional[datetime] = None
    createDateTime: Optional[datetime] =  Field(default_factory=datetime.utcnow)
    updateDateTime: Optional[datetime] =  Field(default_factory=datetime.utcnow)
    lastLogin: Optional[datetime] = None
    domainId: Optional[str] = None 
    # admin: Optional[bool] = False


class UserProfile(UserBase):
    email: EmailStr
    # password: str
    uid: Optional[str]
    # firstName: Optional[str]
    # lastName: Optional[str]
    # address: Optional[str]
    # email: Optional[EmailStr]
    # phone: Optional[str]
    isActive:  Optional[bool] = True
    status:  Optional[str] 
    # deleted:  Optional[bool] = False
    # userType: Optional[str] = None
    roles: Optional[List[str]] = [] 
    description: Optional[str] = None
    images: Optional[List[UserImage]] = []
    # hashedPassword: Optional[str] = None
    # activeToken: Optional[str] = None 
    # tokenExpiredAt: Optional[datetime] = None
    # googleToken: Optional[str] = None 
    # googleTokenExpiredAt: Optional[datetime] = None
    createDateTime: Optional[datetime] =  Field(default_factory=datetime.utcnow)
    updateDateTime: Optional[datetime] =  Field(default_factory=datetime.utcnow)
    lastLogin: Optional[datetime] = None
    domainId: Optional[str] = None 
    # admin: Optional[bool] = False
    
class UserForView(UserBase):
    uid: Optional[str]
    isActive:  Optional[bool] = True
    tokenExpiredAt: Optional[datetime] = None
    createDateTime: Optional[datetime] =  None
    updateDateTime: Optional[datetime] =  None
    domainId: Optional[str] = None 
    # admin: Optional[bool] = False
    
    
    
class SearchForm(BaseModel):
    uid: Optional[str] = "" 
    page : Optional[int] = 1
    pageSize : Optional[int] = 10
    searchText: Optional[str] = "" 
    domainId: Optional[str] = "" 
    status: Optional[str] = ""
    # admin: Optional[bool] = False

class ActiveForm(BaseModel):
    uid: str
    isActive: bool


class UserEditProfile(BaseModel):
    firstName: Optional[str] = "" 
    lastName : Optional[str] = "" 
    address : Optional[str] = "" 
    phone: Optional[str] = "" 
    isActive:  Optional[bool]
    status: Optional[str] = ""
    roles: Optional[List[str]] = [] 
    images: Optional[List[UserImageIn]] = []
