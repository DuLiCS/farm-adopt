from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import enum

class TargetType(str, enum.Enum):
    tea = "tea"
    hydroponic = "hydroponic"

class TargetStatus(str, enum.Enum):
    active = "active"
    maintenance = "maintenance"
    harvested = "harvested"
    unavailable = "unavailable"

class AdoptTargetBase(BaseModel):
    type: TargetType
    code: str
    name: str
    description: Optional[str] = None
    price_basic: Optional[int] = None
    price_standard: Optional[int] = None
    cover_image: Optional[str] = None
    location_desc: Optional[str] = None
    camera_id: Optional[str] = None
    current_status: TargetStatus = TargetStatus.active

class AdoptTargetCreate(AdoptTargetBase):
    pass

class AdoptTargetOut(AdoptTargetBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True