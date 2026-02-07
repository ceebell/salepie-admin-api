from pydantic import BaseModel, field_validator, Field
from typing import Optional, List
from datetime import datetime
from models.customValidation import alpNumStr, alpNumSpeStr, emojiAlnumStr
from utils.datetime_util  import now

from core.config import SALEPIE_URL

# class ImageCommon(BaseModel):
#     uid: Optional[str] = None
#     domainId: Optional[str] = None
#     name: Optional[str] = None
#     description: Optional[str] = None
#     bannerImage: Optional[str] = None
#     branchImage: Optional[str] = None
#     variantId: Optional[str] = None
#     seq: Optional[int] = 0 
#     getUrl: Optional[str] = None
#     path: Optional[str] = None
#     filename: Optional[str] = None
#     uploadedFilename: Optional[str] = None
#     deleted: Optional[bool] = False
    

#     createDateTime: datetime = Field(default_factory=now)
#     createBy: Optional[str] = None
#     updateDateTime: datetime = Field(default_factory=now) 
#     updateBy: Optional[str] = None

#     @field_validator("createDateTime", "updateDateTime", mode="before")
#     @classmethod
#     def set_dt(cls, v):
#         return v or now()


#=============================================
# Product Stock Data Model
# =============================================

class StockDB(BaseModel):
    uid: Optional[str] = None
    domainId: Optional[str] = None
    productId: Optional[str] = None
    variantId: Optional[str] = None
    description: Optional[str] = None
    branchId: Optional[str] = None
    inStock: float = Field(default=0, ge=0)

    # audit
    createDateTime: datetime = Field(default_factory=now)
    createBy: Optional[str] = None
    updateDateTime: datetime = Field(default_factory=now)
    updateBy: Optional[str] = None

    

    # status
    isActive: bool = True
    deleted: bool = False
    

    @field_validator("createDateTime", "updateDateTime", mode="before")
    @classmethod
    def set_dt(cls, v):
        return v or now()

class StockIn(BaseModel):
    uid: Optional[str] = None
    domainId: Optional[str] = None
    productId: Optional[str] = None
    variantId: Optional[str] = None
    description: Optional[str] = None
    branchId: Optional[str] = None
    inStock: float = Field(default=0, ge=0)


class StockOut(BaseModel):
    uid: Optional[str] = None
    domainId: Optional[str] = None
    productId: Optional[str] = None
    variantId: Optional[str] = None
    description: Optional[str] = None
    branchId: Optional[str] = None
    inStock: float = Field(default=0, ge=0)

    # audit
    createDateTime: datetime = Field(default_factory=now)
    createBy: Optional[str] = None
    updateDateTime: datetime = Field(default_factory=now)
    updateBy: Optional[str] = None

    # status
    isActive: bool = True
    deleted: bool = False
  


#=============================================
# Produc tGroup
# =============================================

class ProductGroup(BaseModel):
    uid: str
    domainId: Optional[str] = None
    name: Optional[str] = None
    code: Optional[str] = None
    barcode: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    subCategory: Optional[str] = None
    brand: Optional[str] = None
    gender: Optional[str] = None
    inStock: Optional[int] = Field(default=0, ge=0)
    rentalPrice: Optional[float]=0
    bail: Optional[float]=0
    itemStatus: Optional[str] = None
    
class PriceList(BaseModel):
    uid: Optional[str] = None
    domainId: Optional[str] = None
    standardPrice:Optional[float]=0
    sellingPrice:Optional[float]=0
    memberPrice:Optional[float]=0
    discountPrice:Optional[float]=0
    createDateTime: datetime = None
    createBy: Optional[str] = None
    updateDateTime: Optional[datetime] = None
    updateBy: Optional[str] = None

    @field_validator("createDateTime", "updateDateTime", mode="before")
    @classmethod
    def set_dt(cls, v):
        return v or now()

#=============================================
# Product Image Model
# =============================================    
class ProductImage(BaseModel):
    uid: Optional[str] = None
    domainId: Optional[str] = None
    productId: Optional[str] = None
    variantId: Optional[str] = None
    seq: Optional[int] = 0 
    getUrl: Optional[str] = None
    description: Optional[str] = None
    isMain: Optional[bool] = False
    path: Optional[str] = None
    filename: Optional[str] = None
    uploadedFilename: Optional[str] = None
    deleted: Optional[bool] = False
    variantKey: Optional[str] = None
    variantValue: Optional[str] = None
    
    createDateTime: datetime = Field(default_factory=now)
    createBy: Optional[str] = None
    updateDateTime: datetime = Field(default_factory=now) 
    updateBy: Optional[str] = None
    
    @field_validator("createDateTime", "updateDateTime", mode="before")
    @classmethod
    def set_dt(cls, v):
        return v or now()


class ProductImageForm(BaseModel):
    # uid: Optional[str] = None
    # domainId: Optional[str] = None
    # productId: Optional[str] = None
    # variantId: Optional[str] = None
    seq: Optional[int] = 0 
    getUrl: Optional[str] = None
    description: Optional[str] = None
    isMain: Optional[bool] = False
    path: Optional[str] = None
    filename: Optional[str] = None
    uploadedFilename: Optional[str] = None
    deleted: Optional[bool] = False
    variantKey: Optional[str] = None
    variantValue: Optional[str] = None
    
    # createDateTime: Optional[datetime] = None
    # createBy: Optional[str] = None
    # updateDateTime: Optional[datetime] = None
    # updateBy: Optional[str] = None

class ProductImageOut(BaseModel):
    uid: Optional[str] = None
    domainId: Optional[str] = None
    productId: Optional[str] = None
    variantId: Optional[str] = None
    seq: Optional[int] = 0 
    getUrl: Optional[str] = None
    # description: Optional[str] = None
    isMain: Optional[bool] = False
    # path: Optional[str] = None
    filename: Optional[str] = None
    # uploadedFilename: Optional[str] = None
    # deleted: Optional[bool] = False
    variantKey: Optional[str] = None
    variantValue: Optional[str] = None
    createDateTime: Optional[datetime] = None
    createBy: Optional[str] = None
    updateDateTime: Optional[datetime] = None
    updateBy: Optional[str] = None

class ProductImageMinOut(BaseModel):
    # uid: Optional[str] = None
    # domainId: Optional[str] = None
    # productId: Optional[str] = None
    # variantId: Optional[str] = None
    seq: Optional[int] = 0 
    getUrl: Optional[str] = None
    # description: Optional[str] = None
    isMain: Optional[bool] = False
    # path: Optional[str] = None
    # filename: Optional[str] = None
    # uploadedFilename: Optional[str] = None
    # deleted: Optional[bool] = False
    # variantKey: Optional[str] = None
    # variantValue: Optional[str] = None
    # createDateTime: Optional[datetime] = None
    # createBy: Optional[str] = None
    # updateDateTime: Optional[datetime] = None
    # updateBy: Optional[str] = None

    # ✅ เพิ่มส่วนนี้เข้าไปครับ
    @field_validator('getUrl')
    @classmethod
    def add_base_url_prefix(cls, v: Optional[str]) -> Optional[str]:
        # 1. ถ้าเป็น None หรือ Empty string ให้คืนค่าเดิมกลับไป
        if not v:
            return v
        
        # 2. ป้องกันการเติมซ้ำ (เผื่อใน DB เก็บแบบมี http มาแล้ว)
        if v.startswith("http"):
            return v
            
        # 3. เติม Prefix (จัดการเรื่อง / เพื่อไม่ให้ซ้ำกันเช่น .com//image)
        # .lstrip('/') คือลบ / ตัวหน้าสุดของ path ออกถ้ามี
        clean_path = v.lstrip('/')
        clean_prefix = SALEPIE_URL.rstrip('/')
        
        return f"{clean_prefix}/{clean_path}"
    



class ProductImageInItemIn(BaseModel):
    # uid: str
    # seq: Optional[int] = 0
    # dataUrl: Optional[str] = None
    # getUrl: Optional[str] = None    
    productId: Optional[str] = None
    variantId: Optional[str] = None
    description: Optional[str] = None
    isMain: bool               
    filename: Optional[str] = None
    uploadedFilename: Optional[str] = None
    isDeleted: Optional[bool] = False
    variantKey: Optional[str] = None # {color, size, model}
    variantValue: Optional[str] = None
   
class ProductImageInItemDB(BaseModel):
    # uid: str
    productId: Optional[str] = None
    variantId: Optional[str] = None
    seq: Optional[int] = 0
    # dataUrl: Optional[str] = None
    getUrl: Optional[str] = None
    description: Optional[str] = None
    isMain: bool             
    filename: Optional[str] = None
    uploadedFilename: Optional[str] = None
    isDeleted: Optional[bool] = False
    variantKey: Optional[str] = None # {color, size, model}
    variantValue: Optional[str] = None
    # @field_validator("createDateTime", "updateDateTime", mode="before")
    # @classmethod
    # def set_dt(cls, v):
    #     return v or now()
    
class ProductImageInItemOut(BaseModel):
    # uid: str
    productId: Optional[str] = None
    variantId: Optional[str] = None
    seq: Optional[int] = 0
    # dataUrl: Optional[str] = None
    getUrl: Optional[str] = None
    description: Optional[str] = None
    isMain: bool             
    filename: Optional[str] = None
    uploadedFilename: Optional[str] = None
    isDeleted: Optional[bool] = False
    variantKey: Optional[str] = None # {color, size, model}
    variantValue: Optional[str] = None
    
#=============================================
# Product Model
# =============================================

class ProductDB(BaseModel):
    # identity
    uid: Optional[str] = None
    domainId: str

    # core display
    name: str
    code: Optional[str] = None            # รหัสสินค้าแม่ (เช่น DRS-001)
    category: Optional[str] = None
    subCategory: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    gender: Optional[str] = None

    # web/display flags
    itemStatus: Optional[str] = None
    webCategory: Optional[str] = None
    webHotItem: Optional[str] = None
    webItem: Optional[str] = None
    isActive: bool = True

    # content
    description: Optional[str] = None
    webDescription: Optional[str] = None

    # grouping / tags
    group: Optional[str] = None
    groupId: Optional[str] = None
    hashTags: Optional[List[str]] = Field(default_factory=list)

    # images ระดับสินค้าแม่ (เช่น รูป hero/cover)
    # mainImage: Optional[ProductImageInItemDB] = None
    images: List[ProductImageInItemDB] = Field(default_factory=list)

    # audit
    createDateTime: datetime = Field(default_factory=now)
    createBy: Optional[str] = None
    updateDateTime: datetime = Field(default_factory=now)
    updateBy: Optional[str] = None

    # system flags
    deleted: bool = False
    stat: int = 0
    newRecord: bool = False
    temporary: bool = False
    endToChange: bool = False

    @field_validator("createDateTime", "updateDateTime", mode="before")
    @classmethod
    def set_root_dt(cls, v):
        return v or now()


class ProductOut(BaseModel):
    # identity
    uid: Optional[str] = None
    domainId: str

    # core display
    name: str
    code: Optional[str] = None            # รหัสสินค้าแม่ (เช่น DRS-001)
    category: Optional[str] = None
    subCategory: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    gender: Optional[str] = None

    # web/display flags
    itemStatus: Optional[str] = None
    webCategory: Optional[str] = None
    webHotItem: Optional[str] = None
    webItem: Optional[str] = None
    isActive: bool = True

    # content
    description: Optional[str] = None
    webDescription: Optional[str] = None

    # grouping / tags
    group: Optional[str] = None
    groupId: Optional[str] = None
    hashTags: Optional[List[str]] = Field(default_factory=list)

    # images ระดับสินค้าแม่ (เช่น รูป hero/cover)
    # mainImage: Optional[ProductImageInItemDB] = None
    images: Optional[List[ProductImageMinOut]] = Field(default_factory=list)

    # audit
    createDateTime: datetime 
    createBy: Optional[str] = None
    updateDateTime: datetime 
    updateBy: Optional[str] = None

    # system flags
    deleted: bool = False
    stat: int = 0
    newRecord: bool = False
    temporary: bool = False
    endToChange: bool = False



class ProductCreateForm(BaseModel):
    # identity
    domainId: str

    # core display
    name: str
    code: Optional[str] = None            # รหัสสินค้าแม่ (เช่น DRS-001)
    category: Optional[str] = None
    subCategory: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None


class ProductIn(BaseModel):
    # identity
    uid: Optional[str] = None
    # domainId: str

    # core display
    name: str
    code: Optional[str] = None            # รหัสสินค้าแม่ (เช่น DRS-001)
    category: Optional[str] = None
    subCategory: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    gender: Optional[str] = None

    # web/display flags
    itemStatus: Optional[str] = None
    webCategory: Optional[str] = None
    webHotItem: Optional[str] = None
    webItem: Optional[str] = None
    isActive: bool = True

    # content
    description: Optional[str] = None
    webDescription: Optional[str] = None

    # grouping / tags
    group: Optional[str] = None
    groupId: Optional[str] = None
    hashTags: List[str] = Field(default_factory=list)

    # images ระดับสินค้าแม่ (เช่น รูป hero/cover)
    mainImage: Optional[ProductImageInItemDB] = None
    images: List[ProductImageInItemDB] = Field(default_factory=list)

    # audit
    # createDateTime: datetime = Field(default_factory=now)
    # createBy: Optional[str] = None
    # updateDateTime: datetime = Field(default_factory=now)
    # updateBy: Optional[str] = None

    # system flags
    deleted: bool = False
    # stat: int = 0
    # newRecord: bool = False
    # temporary: bool = False
    # endToChange: bool = False



class ProductVariantOut(BaseModel):
    # *** identity
    uid: Optional[str] = None
    # ***
    domainId: str

    # *** productId
    productId: str   # FK -> ProductDB.uid

    # *** variantKey, variantValue
    variantKey: str
    variantValue: str

    # *** SKU core
    sku: str
    barcode: Optional[str] = None

    # attributes (ตัวเลือกที่ทำให้ต้องแยก SKU)
    # FIXME: cololr need 3 chidren elements (name, code, description) 
    color: Optional[str] = None
    # FIXME: cololr need 3 chidren elements (name, code, description) 
    size: Optional[str] = None

    # inventory (สำคัญสำหรับ order)
    inStock: int = Field(default=0, ge=0)
    latestDateIncoming: Optional[datetime] = None

    # stock
    stock: Optional[List[StockOut]] = None


    # pricing (ควรอยู่ที่ SKU)
    standardPrice: float = 0
    sellingPrice: float = 0
    productCost: float = 0
    pricelist: List[PriceList] = Field(default_factory=list)
    

    # images ระดับ variant (เช่น สีแดงมีรูปเฉพาะ)
    # mainImage: Optional[ProductImageInItemDB] = None
    images: List[ProductImageMinOut] = Field(default_factory=list)

    # status
    isActive: bool = True
    deleted: bool = False

    # audit
    createDateTime: Optional[datetime] = None
    createBy: Optional[str] = None
    updateDateTime: Optional[datetime] = None
    updateBy: Optional[str] = None


class ProductVariantOutList(BaseModel):
    # *** identity
    # uid: Optional[str] = None
    # ***
    # domainId: str

    # *** productId
    # productId: str   # FK -> ProductDB.uid

    # *** variantKey, variantValue
    # variantKey: str
    # variantValue: str

    # *** SKU core
    sku: Optional[str] = None
    # barcode: Optional[str] = None

    # attributes (ตัวเลือกที่ทำให้ต้องแยก SKU)
    # FIXME: cololr need 3 chidren elements (name, code, description) 
    color: Optional[str] = None
    # FIXME: cololr need 3 chidren elements (name, code, description) 
    size: Optional[str] = None

    # inventory (สำคัญสำหรับ order)
    inStock: int = Field(default=0, ge=0)
    # latestDateIncoming: Optional[datetime] = None

    # pricing (ควรอยู่ที่ SKU)
    standardPrice: float = 0
    sellingPrice: float = 0
    productCost: float = 0
    pricelist: List[PriceList] = Field(default_factory=list)
    

    # images ระดับ variant (เช่น สีแดงมีรูปเฉพาะ)
    # mainImage: Optional[ProductImageInItemDB] = None
    # images: List[ProductImageMinOut] = Field(default_factory=list)

    # status
    # isActive: bool = True
    # deleted: bool = False

    # # audit
    # createDateTime: Optional[datetime] = None
    # createBy: Optional[str] = None
    # updateDateTime: Optional[datetime] = None
    # updateBy: Optional[str] = None

 


class ProductOutDetail(BaseModel):
    # identity
    uid: Optional[str] = None
    domainId: str

    # core display
    name: str
    code: Optional[str] = None            # รหัสสินค้าแม่ (เช่น DRS-001)
    category: Optional[str] = None
    subCategory: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    gender: Optional[str] = None

    # web/display flags
    itemStatus: Optional[str] = None
    webCategory: Optional[str] = None
    webHotItem: Optional[str] = None
    webItem: Optional[str] = None
    isActive: bool = True

    # content
    description: Optional[str] = None
    webDescription: Optional[str] = None

    # grouping / tags
    group: Optional[str] = None
    groupId: Optional[str] = None
    hashTags: List[str] = Field(default_factory=list)

    # images ระดับสินค้าแม่ (เช่น รูป hero/cover)
    mainImage: Optional[ProductImageMinOut] = None
    images: List[ProductImageMinOut] = Field(default_factory=list)

    # audit
    createDateTime: datetime = Field(default_factory=now)
    createBy: Optional[str] = None
    updateDateTime: datetime = Field(default_factory=now)
    updateBy: Optional[str] = None

    # system flags
    deleted: bool = False
    # stat: int = 0
    # newRecord: bool = False
    # temporary: bool = False
    # endToChange: bool = False

  
class ProductOutList(BaseModel):
    # identity
    uid: Optional[str] = None
    domainId: str

    # core display
    name: str
    code: Optional[str] = None            # รหัสสินค้าแม่ (เช่น DRS-001)
    category: Optional[str] = None
    subCategory: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    gender: Optional[str] = None

    # web/display flags
    itemStatus: Optional[str] = None
    # webCategory: Optional[str] = None
    # webHotItem: Optional[str] = None
    # webItem: Optional[str] = None
    isActive: bool = True

    # content
    # description: Optional[str] = None
    # webDescription: Optional[str] = None

    # grouping / tags
    # group: Optional[str] = None
    # groupId: Optional[str] = None
    hashTags: List[str] = Field(default_factory=list)

    # images ระดับสินค้าแม่ (เช่น รูป hero/cover)
    # mainImage: Optional[ProductImageOut] = None
    # images: List[ProductImageOut] = Field(default_factory=list)

    # audit
    createDateTime: datetime = Field(default_factory=now)
    createBy: Optional[str] = None
    updateDateTime: datetime = Field(default_factory=now)
    updateBy: Optional[str] = None

    # system flags
    # deleted: bool = False
    # stat: int = 0
    # newRecord: bool = False
    # temporary: bool = False
    # endToChange: bool = False

#=============================================
# Product Variant Model
# =============================================
class ProductVariantDB(BaseModel):
    # *** identity
    uid: Optional[str] = None
    # ***
    domainId: str

    # *** productId
    productId: str   # FK -> ProductDB.uid

    # *** variantKey, variantValue
    variantKey: str
    variantValue: str

    # *** SKU core
    sku: str
    barcode: Optional[str] = None

    # attributes (ตัวเลือกที่ทำให้ต้องแยก SKU)
    # FIXME: cololr need 3 chidren elements (name, code, description) 
    color: Optional[str] = None
    # FIXME: cololr need 3 chidren elements (name, code, description) 
    size: Optional[str] = None

    # inventory (สำคัญสำหรับ order)
    inStock: int = Field(default=0, ge=0)
    latestDateIncoming: Optional[datetime] = None

    # pricing (ควรอยู่ที่ SKU)
    standardPrice: float = 0
    sellingPrice: float = 0
    productCost: float = 0
    pricelist: List[PriceList] = Field(default_factory=list)
    

    # images ระดับ variant (เช่น สีแดงมีรูปเฉพาะ)
    # mainImage: Optional[ProductImageInItemDB] = None
    # images: List[ProductImageInItemDB] = Field(default_factory=list)

    # stock
    stock: Optional[List[StockDB]] = None


    # status
    isActive: bool = True
    deleted: bool = False

    # audit
    createDateTime: datetime = Field(default_factory=now)
    createBy: Optional[str] = None
    updateDateTime: datetime = Field(default_factory=now)
    updateBy: Optional[str] = None

    @field_validator("createDateTime", "updateDateTime", mode="before")
    @classmethod
    def set_root_dt(cls, v):
        return v or now()
    

class ProductVariantAdd(BaseModel):
    # identity
    # uid: Optional[str] = None
    # domainId: Optional[str] = None

    # relation
    # productId: str   # FK -> ProductDB.uid # from product header

    # SKU core
    sku: str
    barcode: Optional[str] = None

    # *** variantKey, variantValue
    variantKey: str
    variantValue: str

    # attributes (ตัวเลือกที่ทำให้ต้องแยก SKU)
    color: Optional[str] = None
    size: Optional[str] = None

    # inventory (สำคัญสำหรับ order)
    inStock: float = Field(default=0, ge=0)
    latestDateIncoming: Optional[datetime] = None

    # pricing (ควรอยู่ที่ SKU)
    standardPrice: float = 0
    sellingPrice: float = 0
    productCost: float = 0
    pricelist: List[PriceList] = Field(default_factory=list)

    # images ระดับ variant (เช่น สีแดงมีรูปเฉพาะ)
    # mainImage: Optional[ProductImageInItemDB] = None
    images: List[ProductImageInItemDB] = Field(default_factory=list)

    # status
    isActive: bool = True
    deleted: bool = False

    # audit
    # createDateTime: datetime = Field(default_factory=now)
    # createBy: Optional[str] = None
    # updateDateTime: datetime = Field(default_factory=now)
    # updateBy: Optional[str] = None


  


#=============================================
# Image Meta Data Model
# =============================================

class ProductVariantImageGroup(BaseModel):
    variantKey: Optional[str] = None
    variantValue: Optional[str] = None
    # ใช้ ProductImageMinOut เพื่อให้ได้ URL ที่มี https และ field น้อยๆ
    images: List[ProductImageMinOut] = Field(default_factory=list)


class ProductFormCreate(BaseModel):
    product: ProductIn
    variants: List[ProductVariantAdd] = Field(default_factory=list)
    images: List[ProductImageForm] = Field(default_factory=list)

class ProductFormUpdate(BaseModel):
    product: ProductIn
    variants: List[ProductVariantAdd] = Field(default_factory=list)
    images: List[ProductImageForm] = Field(default_factory=list)



class ProductItemOutDetail(BaseModel):
    product: ProductOutDetail
    variants: List[ProductVariantOut] = Field(default_factory=list)
    images: List[ProductVariantImageGroup] = Field(default_factory=list)

class colorOut(BaseModel):
    color: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None

class sizeOut(BaseModel):
    size: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None

class ProductItemOutList(BaseModel):
    uid:  Optional[str] = None
    domainId: Optional[str] = None
    name: Optional[str] = None
    code: Optional[str] = None
    barcode: Optional[str] = None
    category: Optional[str] = None
    subCategory: Optional[str] = None
    brand: Optional[str] = None
    # ✅ แก้เป็น List[str] ครับ
    availableColors: List[str] = Field(default_factory=list)
    availableSizes: List[str] = Field(default_factory=list)
    # gender: Optional[str] = None
    inStock: Optional[int] = Field(default=0, ge=0)
    itemStatus: Optional[str] = None
    # webCategory: Optional[str] = None
    # webHotItem: Optional[str] = None
    # webItem: Optional[str] = None
    mainImage: Optional[ProductImageInItemOut] = None
    description: Optional[str] = None
    isActive: Optional[bool] = True
    createDateTime: datetime = None
    createBy: Optional[str] = None
    updateDateTime: datetime = None
    updateBy: Optional[str] = None
    # newRecord: Optional[bool] = False
    # temporary: Optional[bool] = False
    stat: Optional[int] = 0
    # endToChange: Optional[bool] = False
    # webDescription: Optional[str] = None
    # group: Optional[str] = None
    # groupId: Optional[str] = None
    # hashTags: Optional[List[str]] = []
    standardPrice:Optional[float]=0
    sellingPrice:Optional[float]=0
    productCost: Optional[float]=0 
    latestDateIncoming: Optional[datetime] = None
    # deleted: Optional[bool] = False

    variants: Optional[List[ProductVariantOutList]] = None

    # pricelist: Optional[List[PriceList]] = []
    # mainImageDataUrl: Optional[ProductImage] = None   # ✅ เพิ่มตัวนี้
    # images: Optional[List[ProductImage]] = []


class ProductItemOutListNoVariants(BaseModel):
    uid:  Optional[str] = None
    domainId: Optional[str] = None
    name: Optional[str] = None
    code: Optional[str] = None
    barcode: Optional[str] = None
    category: Optional[str] = None
    subCategory: Optional[str] = None
    brand: Optional[str] = None
    # ✅ แก้เป็น List[str] ครับ
    availableColors: List[str] = Field(default_factory=list)
    availableSizes: List[str] = Field(default_factory=list)
    # gender: Optional[str] = None
    inStock: Optional[int] = Field(default=0, ge=0)
    itemStatus: Optional[str] = None
    # webCategory: Optional[str] = None
    # webHotItem: Optional[str] = None
    # webItem: Optional[str] = None
    mainImage: Optional[ProductImageInItemOut] = None
    description: Optional[str] = None
    isActive: Optional[bool] = True
    createDateTime: datetime = None
    createBy: Optional[str] = None
    updateDateTime: datetime = None
    updateBy: Optional[str] = None
    # newRecord: Optional[bool] = False
    # temporary: Optional[bool] = False
    stat: Optional[int] = 0
    # endToChange: Optional[bool] = False
    # webDescription: Optional[str] = None
    # group: Optional[str] = None
    # groupId: Optional[str] = None
    # hashTags: Optional[List[str]] = []
    standardPrice:Optional[float]=0
    sellingPrice:Optional[float]=0
    productCost: Optional[float]=0 
    latestDateIncoming: Optional[datetime] = None
    # deleted: Optional[bool] = False

    # *** 
    # variants: Optional[List[ProductVariantOutList]] = None

    # pricelist: Optional[List[PriceList]] = []
    # mainImageDataUrl: Optional[ProductImage] = None   # ✅ เพิ่มตัวนี้
    # images: Optional[List[ProductImage]] = []


#=============================================
# Branch Image in model
# =============================================

class BranchImageDB(BaseModel):
    uid: Optional[str] = None
    domainId: Optional[str] = None
    branchId: Optional[str] = None

    name: Optional[str] = None
    description: Optional[str] = None
    seq: Optional[int] = 0 
    getUrl: Optional[str] = None
    path: Optional[str] = None
    filename: Optional[str] = None
    uploadedFilename: Optional[str] = None
    deleted: Optional[bool] = False
    

    createDateTime: datetime = Field(default_factory=now)
    createBy: Optional[str] = None
    updateDateTime: datetime = Field(default_factory=now) 
    updateBy: Optional[str] = None

    @field_validator("createDateTime", "updateDateTime", mode="before")
    @classmethod
    def set_dt(cls, v):
        return v or now()
   



#=============================================
# Branch in model
# =============================================

class BranchDB(BaseModel):
    uid: Optional[str] = None
    domainId: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    seq: Optional[int] = 0
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    contactPerson: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    status: Optional[str] = None
    isActive: Optional[bool] = True
    deleted: Optional[bool] = False
    bannerImage: Optional[BranchImageDB] = None
    branchImage: Optional[BranchImageDB] = None
    createDateTime: datetime = Field(default_factory=now)
    createBy: Optional[str] = None
    updateDateTime: datetime = Field(default_factory=now) 
    updateBy: Optional[str] = None
    
    @field_validator("createDateTime", "updateDateTime", mode="before")
    @classmethod
    def set_dt(cls, v):
        return v or now()






