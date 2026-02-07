from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OrderItem(BaseModel):
    uid: str
    shopInfoId: Optional[str] = None
    sec: int
    productItemId: Optional[str] = None
    productItemName: Optional[str] = None
    productItemCode: Optional[str] = None
    wnfRemark: Optional[str] = None
    flag1: Optional[str] = None
    flag2: Optional[str] = None
    state: bool
    reservedQuantity: int
    rentalPrice: float
    bail: float
    startDate: datetime
    endDate: datetime
    createDateTime: datetime
    createBy: Optional[str] = None
    updateDateTime: datetime
    updateBy: Optional[str] = None
    mainImage: Optional[str] = None
    freeItemDiscount: float = 0.0
    freeItemQuantity: int = 0
    orderDetailStatus: Optional[str] = None
    wnfOrderId: Optional[str] = None
    wnfReceivingDate: Optional[datetime] = None
    wnfRemark: Optional[str] = None
    
    
class OrderItemInOrder(BaseModel):
    # uid: str
    # shopInfoId: Optional[str] = None
    sec: int
    productItemId: Optional[str] = None
    productItemName: Optional[str] = None
    productItemCode: Optional[str] = None
    wnfRemark: Optional[str] = None
    flag1: Optional[str] = None
    flag2: Optional[str] = None
    state: bool
    reservedQuantity: int
    rentalPrice: float
    # bail: float
    startDate: datetime
    endDate: datetime
    # createDateTime: datetime
    # createBy: Optional[str] = None
    # updateDateTime: datetime
    # updateBy: Optional[str] = None
    mainImage: Optional[str] = None
    freeItemDiscount: float = 0.0
    freeItemQuantity: int = 0
    orderDetailStatus: Optional[str] = None
    # wnfOrderId: Optional[str] = None
    # wnfReceivingDate: Optional[datetime] = None
    # wnfRemark: Optional[str] = None

