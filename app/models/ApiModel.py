from typing import List, Optional

from pydantic import BaseModel,EmailStr , Json,Field, ValidationError, validator
from datetime import datetime, timedelta


class FieldDb(BaseModel):
    uid: Optional[str] = ""
    name: str
    dataType: str
    sec : Optional[int] = None 
    isList : Optional[bool] = False 
    isRequired : Optional[bool] = False
    description: Optional[str]= None

class FieldInput(BaseModel):
    name: str
    dataType: str
    sec : Optional[int] = None 
    isList : Optional[bool] = False 
    isRequired : Optional[bool] = False
    description: Optional[str]= None

class FieldView(BaseModel):
    name: str
    dataType: str
    sec : Optional[int] = None 
    isList : Optional[bool] = False 
    isRequired : Optional[bool] = False
    description: Optional[str]= None
    

class ApiModelInput(BaseModel):
    modelName : Optional[str] = "" 
    modelType: Optional[str]= None # in / out / trans
    description: Optional[str]= None
    fields: Optional[List[FieldInput]] 

class ApiModelDb(BaseModel):
    uid: Optional[str] = "" 
    modelName : Optional[str] = "" 
    domainName: Optional[str] = ""
    modelType: Optional[str]= None # in / out / trans
    description: Optional[str]= None
    fields: Optional[List[FieldDb]] 
    createDateTime: Optional[datetime] =  Field(default_factory=datetime.utcnow)
    updateDateTime: Optional[datetime] =  Field(default_factory=datetime.utcnow)
    createBy: Optional[str] = ""
    updateBy: Optional[str] = ""


class ApiModelView(BaseModel):
    modelName : Optional[str] = "" 
    modelType: Optional[str]= None # in / out / trans
    description: Optional[str]= None
    fields: Optional[List[FieldView]] 