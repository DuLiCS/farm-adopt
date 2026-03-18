from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, orders, admin, plaza, photos, settings
from app.routers.plans import router as plans_router
from app.routers.sensor import router as sensor_router
from app.routers.logs import router as logs_router
from app.database import engine, Base

# 初始化数据库（仅用于开发，生产用 Alembic）
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shannan Ji API", version="1.0.0")

# 允许跨域（根据需求调整）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(plaza.router, prefix="/plaza", tags=["plaza"])
app.include_router(sensor_router)
app.include_router(logs_router)
app.include_router(photos.router)
app.include_router(settings.router)
app.include_router(plans_router)

@app.get("/", summary="Health Check")
def root():
    return {"status": "ok", "service": "farm-adopt"}