from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.routers import auth, orders, admin, plaza, photos
from app.routers import settings as settings_router
from app.routers.plans import router as plans_router
from app.routers.sensor import router as sensor_router
from app.routers.logs import router as logs_router
from app.database import engine, Base, SessionLocal
from app.core.config import settings
from app.core.limiter import limiter

# 初始化数据库（仅用于开发，生产用 Alembic）
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shannan Ji API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 允许跨域；备案完成后在 ALLOWED_ORIGINS 环境变量中替换 IP 为域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# 挂载路由
app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(plaza.router, prefix="/plaza", tags=["plaza"])
app.include_router(sensor_router)
app.include_router(logs_router)
app.include_router(photos.router)
app.include_router(settings_router.router)
app.include_router(plans_router)

@app.get("/", summary="Root")
def root():
    return {"status": "ok", "service": "farm-adopt"}

@app.get("/health", summary="Health Check")
def health():
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    finally:
        db.close()
    if db_status != "ok":
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ok", "db": db_status}