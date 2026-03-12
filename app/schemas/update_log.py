from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import enum

class LogType(str, enum.Enum):
    daily = "daily"
    solar_term = "solar_term"
    harvest = "harvest"
    delivery = "delivery"

class UpdateLogBase(BaseModel):
    target_id: int
    description: str
    log_type: LogType
    image_urls: Optional[List[str]] = None

class UpdateLogCreate(UpdateLogBase):
    pass

class UpdateLogOut(UpdateLogBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True