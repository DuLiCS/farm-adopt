from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class DeliveryStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"

class DeliveryLog(Base):
    __tablename__ = "delivery_logs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("adopt_orders.id"), nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    tracking_number = Column(String(100), nullable=True)
    content_desc = Column(String(500), nullable=False)
    status = Column(SQLEnum(DeliveryStatus), default=DeliveryStatus.PENDING)

    order = relationship("AdoptOrder", back_populates="deliveries")