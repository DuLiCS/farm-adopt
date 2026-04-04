from sqlalchemy import Column, Integer, String, DateTime, Date, Enum as SQLEnum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
from app.database import Base

class OrderStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class PlanType(str, enum.Enum):
    SEASON = "season"
    ANNUAL = "annual"
    TRIAL = "trial"
    TEA_BASIC = "tea_basic"
    TEA_STANDARD = "tea_standard"
    PLANT_BASIC = "plant_basic"

class AdoptOrder(Base):
    __tablename__ = "adopt_orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("adopt_targets.id"), nullable=False)
    start_date = Column(Date, default=date.today, nullable=False)
    expire_date = Column(Date, nullable=False)
    plan_type = Column(SQLEnum(PlanType), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 收货地址信息
    receiver_name = Column(String(50), nullable=True)
    receiver_phone = Column(String(20), nullable=True)
    receiver_address = Column(String(200), nullable=True)
    receiver_note = Column(String(100), nullable=True)

    # 认养寄语
    dedication = Column(String(100), nullable=True)

    user = relationship("User", back_populates="orders")
    target = relationship("AdoptTarget", back_populates="orders")
    deliveries = relationship("DeliveryLog", back_populates="order", cascade="all, delete-orphan")