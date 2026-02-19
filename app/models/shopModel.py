from typing import List, Optional, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from pydantic import BaseModel, Field, model_validator,ConfigDict
from utils.datetime_util import now  # สมมติว่ามี util นี้ตามไฟล์ตัวอย่าง

# =========================================================
# Base Validator Mixin (เพื่อลด code ซ้ำ)
# =========================================================
# class AuditMixin(BaseModel):
#     createDateTime: datetime = Field(default_factory=now)
#     createBy: Optional[str] = None
#     updateDateTime: datetime = Field(default_factory=now)
#     updateBy: Optional[str] = None

#     @field_validator("createDateTime", "updateDateTime", mode="before")
#     @classmethod
#     def set_dt(cls, v):
#         return v or now()

class BaseDBModel(BaseModel):
    """
    คลาสแม่สำหรับ DB Model ทุกตัว
    - มี audit fields พื้นฐาน (create/update)
    - มี logic model_validator ที่จะ scan หา field ที่ลงท้ายด้วย 'DateTime'
      ถ้าค่าที่ส่งมาเป็น None จะแทนที่ด้วย now() ทันที
    """

    # 2. เพิ่ม Config ตรงนี้เพื่อให้รองรับ Alias และ Field Name
    model_config = ConfigDict(populate_by_name=True)

    createDateTime: datetime = Field(default_factory=now)
    createBy: Optional[str] = None
    updateDateTime: datetime = Field(default_factory=now)
    updateBy: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def set_datetime_fields(cls, data: Any) -> Any:
        # ตรวจสอบว่าเป็น Dictionary หรือไม่
        if isinstance(data, dict):
            for key, value in data.items():
                # Logic: ถ้าชื่อ field ลงท้ายด้วย DateTime และค่าเป็น None
                if key.endswith("DateTime") and value is None:
                    data[key] = now()
        return data


# =========================================================
# 1. Shop Info
# =========================================================
class ShopInfoReq(BaseModel):
    name: str
    code: Optional[str] = None
    phone: Optional[str] = None
    line: Optional[str] = None
    description: Optional[str] = None
    termAndCondition: Optional[str] = None
    shopCategory: Optional[str] = None
    logo: Optional[str] = None
    industry: Optional[str] = Field(None, alias="Industry")
    group: Optional[str] = None
    subgroup: Optional[str] = None

class ShopInfoDB(BaseDBModel): # สืบทอดจาก BaseDBModel
    uid: str
    name: Optional[str] = None
    code: Optional[str] = None
    phone: Optional[str] = None
    line: Optional[str] = None
    runningNumber: Optional[str] = None
    newSeason: Optional[str] = None
    dateOfNewSeason: Optional[str] = None
    monthOfNewSeason: Optional[str] = None
    firstYear: Optional[str] = None
    yearth: Optional[str] = None
    description: Optional[str] = None
    termAndCondition: Optional[str] = None
    shopCategory: Optional[str] = None
    age: Optional[int] = None
    branchNumber: Optional[str] = None
    logo: Optional[str] = None
    package: Optional[str] = None
    branchRunning: Optional[str] = None
    saleOrderRunningNumber: int = 0
    wknRunningNumber: int = 0
    statusInfo: Optional[str] = Field(None, alias="StatusInfo")
    industry: Optional[str] = Field(None, alias="Industry")
    group: Optional[str] = None
    subgroup: Optional[str] = None

class ShopInfoOut(ShopInfoDB):
    pass

# =========================================================
# 2. Branch
# =========================================================
class BranchReq(BaseModel):
    branchName: str
    code: Optional[str] = None
    image: Optional[str] = None
    bannerImage: Optional[str] = None
    address: Optional[str] = None
    workingTime: Optional[str] = Field(None, alias="WorkingTime")
    phone: Optional[str] = Field(None, alias="Phone")
    description: Optional[str] = Field(None, alias="Description")
    state: bool = Field(True, alias="State")
    
class BranchDB(BaseDBModel): # สืบทอดจาก BaseDBModel
    uid: str
    shopInfoId: str = Field(..., alias="ShopInfoId")
    branchName: Optional[str] = None
    code: Optional[str] = None
    image: Optional[str] = None
    bannerImage: Optional[str] = None
    address: Optional[str] = None
    workingTime: Optional[str] = Field(None, alias="WorkingTime")
    phone: Optional[str] = Field(None, alias="Phone")
    description: Optional[str] = Field(None, alias="Description")
    runningOrder: int = Field(0, alias="RunningOrder")
    runningBorrow: int = Field(0, alias="RunningBorrow")
    sticker: Optional[int] = Field(None, alias="Sticker")
    state: bool = Field(True, alias="State")
    flag1: Optional[str] = Field(None, alias="Flag1")
    flag2: Optional[str] = Field(None, alias="Flag2")
    
    # ตัวนี้ก็จะถูก auto set ถ้าเป็น None เพราะลงท้ายด้วย DateTime
    borrowUpdateDateTime: Optional[datetime] = Field(None, alias="BorrowUpdateDateTime") 
    
    qrToken: Optional[str] = Field(None, alias="QrToken")
    deleted: bool = False

class BranchOut(BranchDB):
    pass

# =========================================================
# 3. Shop Setting
# =========================================================
class ShopSettingReq(BaseModel):
    inVat: bool = False
    taxRate: float = 7.0
    vatSystem: bool = False

class ShopSettingDB(BaseDBModel): # สืบทอดจาก BaseDBModel
    uid: str
    shopInfoId: str = Field(..., alias="ShopInfoId")
    inVat: bool = False
    taxRate: float = 0.0
    vatSystem: bool = False

class ShopSettingOut(ShopSettingDB):
    pass

# =========================================================
# 4. Shop Package
# =========================================================
class ShopPackageReq(BaseModel):
    package: str
    startDateTime: datetime
    endDateTime: datetime
    description: Optional[str] = None
    paid: bool = False
    numberOfUse: int = 0
    current: bool = False

class ShopPackageDB(BaseDBModel): # สืบทอดจาก BaseDBModel
    uid: str
    shopInfoId: str = Field(..., alias="ShopInfoId")
    package: Optional[str] = None
    
    # startDateTime/endDateTime จะถูก set เป็น now() ถ้าค่าที่ส่งมาเป็น None 
    # (จาก Logic ใน BaseDBModel)
    startDateTime: datetime 
    endDateTime: datetime
    
    description: Optional[str] = None
    state: bool = True
    paid: bool = False
    numberOfUse: int = 0
    current: bool = False

class ShopPackageOut(ShopPackageDB):
    pass

# # =========================================================
# # 1. Shop Info
# # =========================================================
# class ShopInfoReq(BaseModel):
#     name: str
#     code: Optional[str] = None
#     phone: Optional[str] = None
#     line: Optional[str] = None
#     description: Optional[str] = None
#     termAndCondition: Optional[str] = None
#     shopCategory: Optional[str] = None
#     logo: Optional[str] = None
#     industry: Optional[str] = Field(None, alias="Industry") # Map จาก Diagram
#     group: Optional[str] = None
#     subgroup: Optional[str] = None
#     # Fields อื่นๆ ตาม Diagram ใส่เพิ่มได้ตามต้องการ

# class ShopInfoDB(AuditMixin):
#     uid: str
#     name: Optional[str] = None
#     code: Optional[str] = None
#     phone: Optional[str] = None
#     line: Optional[str] = None
#     runningNumber: Optional[str] = None
#     newSeason: Optional[str] = None
#     dateOfNewSeason: Optional[str] = None
#     monthOfNewSeason: Optional[str] = None
#     firstYear: Optional[str] = None
#     yearth: Optional[str] = None
#     description: Optional[str] = None
#     termAndCondition: Optional[str] = None
#     shopCategory: Optional[str] = None
#     age: Optional[int] = None
#     branchNumber: Optional[str] = None
#     logo: Optional[str] = None
#     package: Optional[str] = None
#     branchRunning: Optional[str] = None
#     saleOrderRunningNumber: int = 0
#     wknRunningNumber: int = 0
#     statusInfo: Optional[str] = Field(None, alias="StatusInfo")
#     industry: Optional[str] = Field(None, alias="Industry")
#     group: Optional[str] = None
#     subgroup: Optional[str] = None

# class ShopInfoOut(ShopInfoDB):
#     pass

# # =========================================================
# # 2. Branch
# # =========================================================
# class BranchReq(BaseModel):
#     branchName: str
#     code: Optional[str] = None
#     image: Optional[str] = None
#     bannerImage: Optional[str] = None
#     address: Optional[str] = None
#     workingTime: Optional[str] = Field(None, alias="WorkingTime")
#     phone: Optional[str] = Field(None, alias="Phone")
#     description: Optional[str] = Field(None, alias="Description")
#     state: bool = Field(True, alias="State")
    
# class BranchDB(AuditMixin):
#     uid: str
#     shopInfoId: str = Field(..., alias="ShopInfoId") # FK
#     branchName: Optional[str] = None
#     code: Optional[str] = None
#     image: Optional[str] = None
#     bannerImage: Optional[str] = None
#     address: Optional[str] = None
#     workingTime: Optional[str] = Field(None, alias="WorkingTime")
#     phone: Optional[str] = Field(None, alias="Phone")
#     description: Optional[str] = Field(None, alias="Description")
#     runningOrder: int = Field(0, alias="RunningOrder")
#     runningBorrow: int = Field(0, alias="RunningBorrow")
#     sticker: Optional[int] = Field(None, alias="Sticker")
#     state: bool = Field(True, alias="State")
#     flag1: Optional[str] = Field(None, alias="Flag1")
#     flag2: Optional[str] = Field(None, alias="Flag2")
#     borrowUpdateDateTime: Optional[datetime] = Field(None, alias="BorrowUpdateDateTime")
#     qrToken: Optional[str] = Field(None, alias="QrToken")
    
#     # status
#     deleted: bool = False

# class BranchOut(BranchDB):
#     pass

# # =========================================================
# # 3. Shop Setting
# # =========================================================
# class ShopSettingReq(BaseModel):
#     inVat: bool = False
#     taxRate: float = 7.0
#     vatSystem: bool = False

# class ShopSettingDB(AuditMixin):
#     uid: str
#     shopInfoId: str = Field(..., alias="ShopInfoId")
#     inVat: bool = False
#     taxRate: float = 0.0
#     vatSystem: bool = False

# class ShopSettingOut(ShopSettingDB):
#     pass

# # =========================================================
# # 4. Shop Package
# # =========================================================
# class ShopPackageReq(BaseModel):
#     package: str
#     startDateTime: datetime
#     endDateTime: datetime
#     description: Optional[str] = None
#     paid: bool = False
#     numberOfUse: int = 0
#     current: bool = False

# class ShopPackageDB(AuditMixin):
#     uid: str
#     shopInfoId: str = Field(..., alias="ShopInfoId")
#     package: Optional[str] = None
#     startDateTime: datetime
#     endDateTime: datetime
#     description: Optional[str] = None
#     state: bool = True
#     paid: bool = False
#     numberOfUse: int = 0
#     current: bool = False

# class ShopPackageOut(ShopPackageDB):
#     pass