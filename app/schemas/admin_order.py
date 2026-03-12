from pydantic import BaseModel
from datetime import date
from typing import Optional
from app.schemas.adopt_order import PlanType

class AdminOrderCreate(BaseModel):
    user_phone: str  # 用户手机号，用于查询用户
    target_id: int
    plan_type: PlanType
    price: float
    expire_date: Optional[date] = None  # 可选，如果不提供则根据套餐自动计算
