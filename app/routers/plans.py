from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal
from app.routers.auth import get_admin_user
from pydantic import BaseModel
from typing import Optional, List
import json

router = APIRouter(prefix="/api/plans", tags=["plans"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class PlanCreate(BaseModel):
    plan_key: str
    name: str
    category: str
    price: int
    description: Optional[str] = None
    details: Optional[str] = None
    benefits: Optional[List[str]] = []
    sort_order: int = 0
    stock: int = -1
    is_active: bool = True


class PlanUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[int] = None
    description: Optional[str] = None
    details: Optional[str] = None
    benefits: Optional[List[str]] = None
    sort_order: Optional[int] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None


class SortItem(BaseModel):
    id: int
    sort_order: int


@router.get("")
def get_active_plans(db: Session = Depends(get_db)):
    rows = db.execute(text(
        "SELECT * FROM plans WHERE is_active = TRUE ORDER BY sort_order ASC"
    )).fetchall()
    return [dict(r._mapping) for r in rows]


@router.get("/all")
def get_all_plans(db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    rows = db.execute(text(
        "SELECT * FROM plans ORDER BY sort_order ASC"
    )).fetchall()
    return [dict(r._mapping) for r in rows]


@router.post("")
def create_plan(plan: PlanCreate, db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    db.execute(text("""
        INSERT INTO plans (plan_key, name, category, price, description, details, benefits, sort_order, stock, is_active)
        VALUES (:plan_key, :name, :category, :price, :description, :details, :benefits, :sort_order, :stock, :is_active)
    """), {
        **plan.dict(),
        "benefits": json.dumps(plan.benefits, ensure_ascii=False)
    })
    db.commit()
    return {"ok": True}


@router.put("/sort")
def update_sort(items: List[SortItem], db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    for item in items:
        db.execute(text(
            "UPDATE plans SET sort_order = :sort_order WHERE id = :id"
        ), {"id": item.id, "sort_order": item.sort_order})
    db.commit()
    return {"ok": True}


@router.put("/{plan_id}")
def update_plan(plan_id: int, plan: PlanUpdate, db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    data = {k: v for k, v in plan.dict().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="没有可更新的字段")
    if "benefits" in data:
        data["benefits"] = json.dumps(data["benefits"], ensure_ascii=False)
    sets = ", ".join([f"{k} = :{k}" for k in data])
    data["plan_id"] = plan_id
    db.execute(text(f"UPDATE plans SET {sets}, updated_at = NOW() WHERE id = :plan_id"), data)
    db.commit()
    return {"ok": True}


@router.delete("/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    db.execute(text("DELETE FROM plans WHERE id = :id"), {"id": plan_id})
    db.commit()
    return {"ok": True}
