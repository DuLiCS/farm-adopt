from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class LogType(str, enum.Enum):
    DAILY = "daily"
    SOLAR_TERM = "solar_term"
    HARVEST = "harvest"
    DELIVERY = "delivery"

class UpdateLog(Base):
    __tablename__ = "update_logs"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("adopt_targets.id"), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    image_urls = Column(JSON, nullable=True)  # 图片 URL 数组
    description = Column(String(500), nullable=False)
    log_type = Column(SQLEnum(LogType), nullable=False)

    target = relationship("AdoptTarget", back_populates="updates")