from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/logs/latest")
def get_latest_log(db: Session = Depends(get_db)):
    """获取最新一条已发布日志（首页用）"""
    result = db.execute(text("""
        SELECT id, title, description, log_type, source, updated_at
        FROM update_logs
        WHERE status = 'published'
        ORDER BY updated_at DESC
        LIMIT 1
    """)).fetchone()
    if not result:
        return {"data": None}
    return {"data": dict(result._mapping)}

@router.get("/api/logs")
def get_logs(page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    """获取已发布日志列表"""
    offset = (page - 1) * page_size
    results = db.execute(text("""
        SELECT id, title, description, log_type, source, updated_at
        FROM update_logs
        WHERE status = 'published'
        ORDER BY updated_at DESC
        LIMIT :limit OFFSET :offset
    """), {"limit": page_size, "offset": offset}).fetchall()

    total = db.execute(text("""
        SELECT COUNT(*) FROM update_logs WHERE status = 'published'
    """)).scalar()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": [dict(r._mapping) for r in results]
    }
