from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class TargetType(str, enum.Enum):
    TEA = "tea"
    HYDROPONIC = "hydroponic"

class TargetStatus(str, enum.Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    HARVESTED = "harvested"
    UNAVAILABLE = "unavailable"

class AdoptTarget(Base):
    __tablename__ = "adopt_targets"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(TargetType), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)  # 例如 "TEA-001"
    name = Column(String(100), nullable=False)  # 对象名称（如"云雾茶树 · 01号"）
    description = Column(Text, nullable=True)  # 详细描述
    price_basic = Column(Integer, nullable=True)  # 基础套餐价格
    price_standard = Column(Integer, nullable=True)  # 标准套餐价格（可为空）
    cover_image = Column(String(500), nullable=True)  # 封面图片URL
    location_desc = Column(String(200), nullable=True)
    camera_id = Column(String(100), nullable=True)  # 摄像头标识
    current_status = Column(SQLEnum(TargetStatus), default=TargetStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("AdoptOrder", back_populates="target")
    updates = relationship("UpdateLog", back_populates="target", cascade="all, delete-orphan")