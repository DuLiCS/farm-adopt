from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import enum

class DeliveryStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    delivered = "delivered"

class DeliveryLogBase(BaseModel):
    order_id: int
    content_desc: str
    tracking_number: Optional[str] = None
    status: DeliveryStatus = DeliveryStatus.pending

class DeliveryLogCreate(DeliveryLogBase):
    pass

class DeliveryLogOut(BaseModel):
    id: int
    order_id: int
    sent_at: datetime
    tracking_number: Optional[str]
    content_desc: str
    status: DeliveryStatus

    class Config:
        from_attributes = True