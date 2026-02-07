from pydantic import BaseModel, Field, conint, validator
from typing import Optional, List
from datetime import datetime



class Pricelist(BaseModel):
    # uid: str
    # shopInfoId: Optional[str] = Field(None, alias="shopInfold")
    # productItemId: Optional[str] = None  # FK -> ProductItem.uid
    regualrPrice: Optional[float] = None
    salePrice: Optional[float] = None
    memberPrice: Optional[float] = None
    discountPrice: Optional[float] = None
    # createDateTime: datetime
    # createBy: Optional[str] = None
    # updateDateTime: datetime
    # updateBy: Optional[str] = None

    class Config:
        populate_by_name = True


class ProductCost(BaseModel):
    uid: str
    shopInfoId: Optional[str] = Field(None, alias="shopInfold")
    productItemId: Optional[str] = None  # FK -> ProductItem.uid

    sec: Optional[int] = None
    code: Optional[str] = None
    description: Optional[str] = None
    qty: Optional[int] = Field(None, alias="qty")
    unitPrice: Optional[float] = None
    total: Optional[float] = None
    state: bool

    purchasingDate: datetime
    arrivalDate: datetime
    createDateTime: datetime
    createBy: Optional[str] = None
    updateDateTime: datetime
    updateBy: Optional[str] = None

    class Config:
        populate_by_name = True


class VariantInItem(BaseModel):
    uid: str
    productItemId: Optional[str] = None  # FK -> ProductItem.uid

    sec: Optional[int] = None
    code: Optional[str] = None
    value: Optional[str] = None
    state: bool
    description: Optional[str] = None

    variantKey: Optional[str] = None      # e.g., size/color/model
    variantValue: Optional[str] = None

    class Config:
        populate_by_name = True


# class ProductItemDB(BaseModel):
#     uid: str
#     shopInfoId: Optional[str] = None
#     productGroupId: Optional[str] = None
#     name: Optional[str] = None
#     code: Optional[str] = None
#     # added fields
#     barcode: Optional[str] = None
#     sku: Optional[str] = None
#     # added fields
#     category: Optional[str] = None
#     subCategory: Optional[str] = None
#     brand: Optional[str] = None
#     size: Optional[str] = None
#     color: Optional[str] = None
#     texture: Optional[str] = None
#     size: Optional[str] = None
#     yearth: int
#     gender: Optional[str] = None
#     inStock: int = Field(default=0, ge=0)
#     rentalPrice: float = 0
#     bail: float = 0
#     itemStatus: Optional[str] = None
#     webCategory: Optional[str] = None
#     webHotItem: Optional[str] = None
#     webItem: Optional[str] = None
#     mainImage: Optional[str] = None
#     itemCode3Digit: Optional[str] = None
#     description: Optional[str] = None
#     color: Optional[str] = None
#     state: bool
#     createDateTime: datetime
#     createBy: Optional[str] = None
#     updateDateTime: datetime
#     updateBy: Optional[str] = None
#     newRecord: bool
#     temporary: Optional[bool] = None
#     rentalStat: int
#     intendToChange: bool
#     webDescription: Optional[str] = None
#     group: Optional[str] = None
#     groupId: Optional[str] = None
#     hashTags: Optional[List[str]] = []
#     deleted: bool = False

#     # Derived/summary fields in note box
#     productCost: float = 0.0
#     latestDateIncoming: datetime

#     # Relations (embedded lists when needed)
#     pricelist: Optional[List[Pricelist]] =  []
#     variants: Optional[List[VariantInItem]] =  []
#     costs: Optional[List[ProductCost]] =  []
    

# class ProductIn(BaseModel):
#     # uid: str
#     # shopInfoId: Optional[str] = None
#     productGroupId: Optional[str] = None
#     name: Optional[str] = None
#     code: Optional[str] = None
#     # added fields
#     barcode: Optional[str] = None
#     sku: Optional[str] = None
#     # added fields
#     category: Optional[str] = None
#     subCategory: Optional[str] = None
#     brand: Optional[str] = None
#     size: Optional[str] = None
#     color: Optional[str] = None
#     texture: Optional[str] = None
#     size: Optional[str] = None
#     yearth: int
#     gender: Optional[str] = None
#     inStock: int = Field(default=0, ge=0)# ✅
#     rentalPrice: float = 0
#     bail: float = 0
#     itemStatus: Optional[str] = None
#     webCategory: Optional[str] = None
#     webHotItem: Optional[str] = None
#     webItem: Optional[str] = None
#     mainImage: Optional[str] = None
#     itemCode3Digit: Optional[str] = None
#     description: Optional[str] = None
#     color: Optional[str] = None
#     state: bool
#     # createDateTime: datetime
#     # createBy: Optional[str] = None
#     # updateDateTime: datetime
#     # updateBy: Optional[str] = None
#     newRecord: bool
#     temporary: Optional[bool] = None
#     rentalStat: int
#     intendToChange: bool
#     webDescription: Optional[str] = None
#     group: Optional[str] = None
#     groupId: Optional[str] = None
#     hashTags: Optional[List[str]] = []
#     deleted: bool = False

#     # Derived/summary fields in note box
#     productCost: float = 0.0
#     latestDateIncoming: datetime

#     # Relations (embedded lists when needed)
#     pricelist: Optional[List[Pricelist]] =  []
#     variants: Optional[List[VariantInItem]] =  []
#     costs: Optional[List[ProductCost]] =  []

   
  
# class ProductOut(BaseModel):
#     uid: str
#     shopInfoId: Optional[str] = None
#     productGroupId: Optional[str] = None
#     name: Optional[str] = None
#     code: Optional[str] = None
#     # added fields
#     barcode: Optional[str] = None
#     sku: Optional[str] = None
#     # added fields
#     category: Optional[str] = None
#     subCategory: Optional[str] = None
#     brand: Optional[str] = None
#     size: Optional[str] = None
#     color: Optional[str] = None
#     texture: Optional[str] = None
#     size: Optional[str] = None
#     yearth: int
#     gender: Optional[str] = None
#     inStock: int = Field(default=0, ge=0)
#     rentalPrice: float = 0
#     bail: float = 0
#     itemStatus: Optional[str] = None
#     webCategory: Optional[str] = None
#     webHotItem: Optional[str] = None
#     webItem: Optional[str] = None
#     mainImage: Optional[str] = None
#     itemCode3Digit: Optional[str] = None
#     description: Optional[str] = None
#     color: Optional[str] = None
#     state: bool
#     createDateTime: datetime
#     createBy: Optional[str] = None
#     updateDateTime: datetime
#     updateBy: Optional[str] = None
#     newRecord: bool
#     temporary: Optional[bool] = None
#     rentalStat: int
#     intendToChange: bool
#     webDescription: Optional[str] = None
#     group: Optional[str] = None
#     groupId: Optional[str] = None
#     hashTags: Optional[List[str]] = []
#     deleted: bool = False

#     # Derived/summary fields in note box
#     productCost: float = 0.0
#     latestDateIncoming: datetime

#     # Relations (embedded lists when needed)
#     pricelist: Optional[List[Pricelist]] =  []
#     variants: Optional[List[VariantInItem]] =  []
#     costs: Optional[List[ProductCost]] =  []

