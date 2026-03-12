from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import SessionLocal
from app.models.adopt_target import AdoptTarget
from app.models.update_log import UpdateLog, LogType
from app.schemas.adopt_target import AdoptTargetOut
from app.schemas.update_log import UpdateLogOut

router = APIRouter(tags=["plaza"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/targets", response_model=List[AdoptTargetOut])
def list_targets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取所有认养对象（公开）"""
    targets = db.query(AdoptTarget).offset(skip).limit(limit).all()
    # 调试：打印第一个 target 的属性
    if targets:
        t = targets[0]
        print(f"DEBUG: id={t.id}, name={t.name}, price_basic={t.price_basic}")
        from app.schemas.adopt_target import AdoptTargetOut
        schema = AdoptTargetOut.model_validate(t)
        print("Schema dict:", schema.model_dump())
    return targets

@router.get("/targets/{target_id}")
def get_target_detail(
    target_id: int,
    db: Session = Depends(get_db)
):
    """获取单个认养对象详情（公开，带最新3条更新）"""
    target = db.query(AdoptTarget).filter(AdoptTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    # 获取最新3条更新
    updates = db.query(UpdateLog).filter(UpdateLog.target_id == target_id).order_by(UpdateLog.updated_at.desc()).limit(3).all()
    
    return {
        "target": target,
        "updates": updates
    }
