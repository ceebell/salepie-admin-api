from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.orderItem import *

class Order(BaseModel):
    uid: str
    shopInfoId: Optional[str] = None
    branchId: Optional[str] = None
    orderRef: Optional[str] = None
    orderNumber: Optional[str] = None
    orderNumberRef: Optional[str] = None
   
    orderStatus: Optional[str] = None   # => {"draft", "waiting_for_payment", "confirm", "preparing", "delivery_out", "customer_received", "complete", "cancel", "on_hold"}
                                        # draft คือ สร้างใบสั่งซื้อใหม่ ยังไม่ได้ชำระเงิน
                                        # waiting_for_payment คือ รอการชำระเงิน
                                        # confirm คือ ยืนยันการสั่งซื้อ
                                        # preparing คือ เตรียมสินค้า
                                        # delivery_out คือ ส่งสินค้าออกจากร้านค้า
                                        # customer_received คือ ลูกค้าได้รับสินค้าแล้ว
                                        # complete คือ ลูกค้า Rating สินค้าแล้ว
                                        # cancel คือ ยกเลิกการสั่งซื้อ
                                        # on_hold คือ ระงับชั่วคราว
                                        # request_to_return คือ คืนสินค้า
                                        # returned_money คือ คืนสินค้าแล้ว
    
    state: bool
    remark1: Optional[str] = None
    remark2: Optional[str] = None
    remark3: Optional[str] = None
    customerId: Optional[str] = None
    customerName: Optional[str] = None
    customerAddress: Optional[str] = None
    customerPhone: Optional[str] = None
    customerEmail: Optional[str] = None
    accountNumber: Optional[str] = None
    accountName: Optional[str] = None
    accountPhone: Optional[str] = None
    receiveChannel: Optional[str] = None
    receiveChannelInfo: Optional[str] = None
    receiveAddress: Optional[str] = None
    receiveNote: Optional[str] = None
    receiveBy: Optional[str] = None
    receiveDate: Optional[datetime] = None
    bringBackBy: Optional[str] = None
    bringBackDate: Optional[datetime] = None
    prepareStatus: Optional[str] = None
    prepareBy: Optional[str] = None
    prepareDate: Optional[datetime] = None
    deliveryOutDate: Optional[datetime] = None
    deliveryOutRemark  : Optional[str] = None
    priceTotal: float = 0.0
    priceDiscount: float = 0.0
    priceNet: float = 0.0
    vatRate: float = 0.0
    vatNet: float = 0.0
    bailRate: float = 0.0
    bailNet: float = 0.0
    pointDiscount: float = 0.0
    taxRate: float = 0.0
    taxStyle: bool = False
    voucherDiscount: float = 0.0
    returnStatus: Optional[str] = None
    returnBy: Optional[str] = None
    returnDate: Optional[datetime] = None
    returnRemark: Optional[str] = None
    returnFee: float = 0.0
    returnCompensate: float = 0.0
    rentalDiscount: float = 0.0
    rentalDiscountNote: Optional[str] = None
    deductionFee: float = 0.0
    deductionNote: Optional[str] = None
    bailReturningDate: Optional[datetime] = None
    bailReturningStatus: Optional[str] = None
    note: Optional[str] = None
    description: Optional[str] = None
    createBy: Optional[str] = None
    createDateTime: datetime
    updateBy: Optional[str] = None
    updateDateTime: datetime
    totalPaymentAmount: float = 0.0
    rentalPaymentMethod: Optional[str] = None
    bailPaymentMethod: Optional[str] = None
    rentalPaymentDate: Optional[datetime] = None
    bailPaymentDate: Optional[datetime] = None
    orderItems: Optional[List[OrderItemInOrder]] = None
    

    
class OrderDB(BaseModel):
    uid: str
    shopInfoId: Optional[str] = None
    branchId: Optional[str] = None
    orderRef: Optional[str] = None
    orderNumber: Optional[str] = None
    orderNumberRef: Optional[str] = None
    orderStatus: Optional[str] = None
    state: bool
    remark1: Optional[str] = None
    remark2: Optional[str] = None
    remark3: Optional[str] = None
    customerId: Optional[str] = None
    customerName: Optional[str] = None
    customerAddress: Optional[str] = None
    customerPhone: Optional[str] = None
    customerEmail: Optional[str] = None
    accountNumber: Optional[str] = None
    accountName: Optional[str] = None
    accountPhone: Optional[str] = None
    receiveChannel: Optional[str] = None
    receiveChannelInfo: Optional[str] = None
    receiveAddress: Optional[str] = None
    receiveNote: Optional[str] = None
    receiveBy: Optional[str] = None
    receiveDate: Optional[datetime] = None
    bringBackBy: Optional[str] = None
    bringBackDate: Optional[datetime] = None
    prepareStatus: Optional[str] = None
    prepareBy: Optional[str] = None
    prepareDate: Optional[datetime] = None
    deliveryOutDate: Optional[datetime] = None
    deliveryOutRemark  : Optional[str] = None
    priceTotal: float = 0.0
    priceDiscount: float = 0.0
    priceNet: float = 0.0
    vatRate: float = 0.0
    vatNet: float = 0.0
    bailRate: float = 0.0
    bailNet: float = 0.0
    pointDiscount: float = 0.0
    taxRate: float = 0.0
    taxStyle: bool = False
    voucherDiscount: float = 0.0
    returnStatus: Optional[str] = None
    returnBy: Optional[str] = None
    returnDate: Optional[datetime] = None
    returnRemark: Optional[str] = None
    returnFee: float = 0.0
    returnCompensate: float = 0.0
    rentalDiscount: float = 0.0
    rentalDiscountNote: Optional[str] = None
    deductionFee: float = 0.0
    deductionNote: Optional[str] = None
    bailReturningDate: Optional[datetime] = None
    bailReturningStatus: Optional[str] = None
    note: Optional[str] = None
    description: Optional[str] = None
    createBy: Optional[str] = None
    createDateTime: datetime
    updateBy: Optional[str] = None
    updateDateTime: datetime
    totalPaymentAmount: float = 0.0
    rentalPaymentMethod: Optional[str] = None
    bailPaymentMethod: Optional[str] = None
    rentalPaymentDate: Optional[datetime] = None
    bailPaymentDate: Optional[datetime] = None
    orderItems: Optional[List[OrderItemInOrder]] = None