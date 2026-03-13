from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from app.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class SensorData(BaseModel):
    device_id: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    soil_moisture: Optional[float] = None

@router.post("/api/sensor")
def upload_sensor_data(data: SensorData, db: Session = Depends(get_db)):
    db.execute(text("""
        INSERT INTO sensor_logs (device_id, temperature, humidity, soil_moisture)
        VALUES (:device_id, :temperature, :humidity, :soil_moisture)
    """), {
        "device_id": data.device_id,
        "temperature": data.temperature,
        "humidity": data.humidity,
        "soil_moisture": data.soil_moisture
    })
    db.commit()
    return {"status": "ok"}

@router.get("/api/sensor/latest")
def get_latest_sensor(device_id: str, db: Session = Depends(get_db)):
    result = db.execute(text("""
        SELECT temperature, humidity, soil_moisture, recorded_at
        FROM sensor_logs
        WHERE device_id = :device_id
        ORDER BY recorded_at DESC
        LIMIT 1
    """), {"device_id": device_id}).fetchone()

    if not result:
        return {"status": "no_data"}

    return {
        "temperature": result.temperature,
        "humidity": result.humidity,
        "soil_moisture": result.soil_moisture,
        "recorded_at": result.recorded_at
    }
