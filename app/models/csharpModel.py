from typing import List, Optional

from pydantic import BaseModel,EmailStr , Json,Field, ValidationError, validator
from datetime import datetime, timedelta
from utils import util



# ******************** C# Field ************************

class CsharpFieldBase(BaseModel):
    name: str
    dataType: str
    isList : Optional[str] = None 
    isOption : Optional[str] = None 
    desc: Optional[str]= None
    init : Optional[str]= None
    
    # is_active: Optional[bool]
    
class CsharpFieldForm(CsharpFieldBase):
    pass

class CsharpFieldCreate(CsharpFieldBase):
    id: Optional[str] = util.getUuid()
    createDatetime: Optional[datetime] =  Field(default_factory=datetime.utcnow)
    updateDatetime: Optional[datetime] =  Field(default_factory=datetime.utcnow)
    
class CsharpFieldUpdate(CsharpFieldBase):
    id: Optional[str] = None
    updateDatetime: Optional[datetime] =  Field(default_factory=datetime.utcnow)
    



class CsharpFieldDb(CsharpFieldBase):
    id: Optional[str] = None
    createDatetime: Optional[datetime] 
    createBy:  Optional[str] = None
    updateDatetime: Optional[datetime] 
    updateBy: Optional[str] = None
    
    
class CsharpFieldView(CsharpFieldBase):
    # pass
    id: Optional[str] = None
    createDatetime: Optional[datetime]  = None
    createBy:  Optional[str] = None
    updateDatetime: Optional[datetime]  = None
    updateBy: Optional[str] = None

# ******************** C# Model ************************

class CsharpModelBase(BaseModel):
    name: Optional[str]= None
    baseName: Optional[str]= None
    modelType: Optional[str]= None # in / out / trans
    detail: Optional[str]= None
    
class CsharpModelForm(BaseModel):
    name: Optional[str]= None
    baseName: Optional[str]= None
    modelType: Optional[str]= None # in / out / trans
    detail: Optional[str]= None
    fields: Optional[List[CsharpFieldForm]] 
    
    
    # is_active: Optional[bool]

class CsharpModelCreate(CsharpModelBase):
    id: Optional[str] = util.getUuid()
    fields: Optional[List[CsharpFieldCreate]] = None
    createDatetime: Optional[datetime] =  Field(default_factory=datetime.utcnow)
  

class CsharpModelUpdate(CsharpModelBase):
    id: Optional[str] = None
    updateDatetime: Optional[datetime] =  Field(default_factory=datetime.utcnow)
   


class CsharpModelDb(CsharpModelBase):
    id: Optional[str] = None
    fields: Optional[List[CsharpFieldDb]] 
    createDatetime: Optional[datetime] 
    createBy:  Optional[str] = None
    updateDatetime: Optional[datetime] 
    updateBy: Optional[str] = None
    
class CsharpModelView(CsharpModelBase):
    id: Optional[str] = None
    fields: Optional[List[CsharpFieldView]] = None
    createDatetime: Optional[datetime] 
    createBy:  Optional[str] = None
    updateDatetime: Optional[datetime] 
    updateBy: Optional[str] = None
    


