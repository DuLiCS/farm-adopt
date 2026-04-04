from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
import enum

class OrderStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    cancelled = "cancelled"

class PlanType(str, enum.Enum):
    season = "season"
    annual = "annual"
    trial = "trial"
    tea_basic = "tea_basic"
    tea_standard = "tea_standard"
    plant_basic = "plant_basic"

class AdoptOrderBase(BaseModel):
    target_id: int
    plan_type: PlanType
    price: float
    expire_date: Optional[date] = None  # 由后端根据 plan_type 自动计算，可选

class AdoptOrderCreate(AdoptOrderBase):
    receiver_name: Optional[str] = None
    receiver_phone: Optional[str] = None
    receiver_address: Optional[str] = None
    receiver_note: Optional[str] = None
    dedication: Optional[str] = None

class AdoptOrderOut(BaseModel):
    id: int
    user_id: int
    target_id: int
    start_date: date
    expire_date: date
    plan_type: PlanType
    price: float
    status: OrderStatus
    created_at: datetime
    dedication: Optional[str] = None

    class Config:
        from_attributes = True