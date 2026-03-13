from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserOut
from app.models.adopt_target import AdoptTarget, TargetType, TargetStatus
from app.models.adopt_order import AdoptOrder, OrderStatus, PlanType
from app.models.update_log import UpdateLog, LogType
from app.schemas.update_log import UpdateLogOut
from app.models.delivery_log import DeliveryLog, DeliveryStatus
from app.schemas.adopt_target import AdoptTargetOut, AdoptTargetCreate
from app.schemas.adopt_order import AdoptOrderOut
from app.schemas.admin_order import AdminOrderCreate
from app.routers.auth import get_admin_user

router = APIRouter(tags=["admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/users", response_model=List[UserOut])
def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取所有用户列表（管理员）"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# ============ 认养对象管理 ============

@router.get("/targets", response_model=List[AdoptTargetOut])
def list_targets(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取认养对象列表"""
    targets = db.query(AdoptTarget).offset(skip).limit(limit).all()
    return targets

@router.post("/targets", response_model=AdoptTargetOut, status_code=status.HTTP_201_CREATED)
def create_target(
    target_in: AdoptTargetCreate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """新增认养对象"""
    # 检查编号是否已存在
    existing = db.query(AdoptTarget).filter(AdoptTarget.code == target_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Target code already exists")
    
    target = AdoptTarget(
        type=target_in.type,
        code=target_in.code,
        name=target_in.name,
        description=target_in.description,
        price_basic=target_in.price_basic,
        price_standard=target_in.price_standard,
        cover_image=target_in.cover_image,
        location_desc=target_in.location_desc,
        camera_id=target_in.camera_id,
        current_status=target_in.current_status
    )
    db.add(target)
    db.commit()
    db.refresh(target)
    return target

# ============ 订单管理 ============

@router.get("/orders")
def list_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取所有订单列表（管理员视角）"""
    orders = db.query(AdoptOrder).offset(skip).limit(limit).all()
    # 手动构建包含 user 和 target 信息的响应
    result = []
    for order in orders:
        order_data = {
            "id": order.id,
            "user_id": order.user_id,
            "target_id": order.target_id,
            "start_date": order.start_date,
            "expire_date": order.expire_date,
            "plan_type": order.plan_type.value if hasattr(order.plan_type, 'value') else order.plan_type,
            "price": order.price,
            "status": order.status.value if hasattr(order.status, 'value') else order.status,
            "created_at": order.created_at,
            "receiver_name": order.receiver_name,
            "receiver_phone": order.receiver_phone,
            "receiver_address": order.receiver_address,
            "receiver_note": order.receiver_note,
            "user": {
                "id": order.user.id,
                "phone": order.user.phone,
                "nickname": order.user.nickname
            } if order.user else None,
            "target": {
                "id": order.target.id,
                "code": order.target.code,
                "type": order.target.type.value if hasattr(order.target.type, 'value') else order.target.type,
                "location_desc": order.target.location_desc
            } if order.target else None
        }
        result.append(order_data)
    return result

@router.post("/orders", response_model=AdoptOrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: AdminOrderCreate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """手动创建订单（管理员）"""
    # 根据手机号查找用户
    user = db.query(User).filter(User.phone == order_in.user_phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 检查认养对象是否存在
    target = db.query(AdoptTarget).filter(AdoptTarget.id == order_in.target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    # 检查认养对象是否可用
    if target.current_status != TargetStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Target is not available for adoption")
    
    # 计算到期日：如果未提供则根据套餐类型计算
    expire_date = order_in.expire_date
    if not expire_date:
        today = date.today()
        if order_in.plan_type == PlanType.TRIAL:
            if today.month < 12:
                expire_date = date(today.year, today.month + 1, today.day)
            else:
                expire_date = date(today.year + 1, 1, today.day)
        elif order_in.plan_type == PlanType.SEASON:
            if today.month <= 9:
                expire_date = date(today.year, today.month + 3, today.day)
            else:
                expire_date = date(today.year + 1, (today.month % 12) + 3, today.day)
        else:  # ANNUAL
            expire_date = date(today.year + 1, today.month, today.day)
    
    order = AdoptOrder(
        user_id=user.id,
        target_id=order_in.target_id,
        start_date=date.today(),
        expire_date=expire_date,
        plan_type=order_in.plan_type,
        price=order_in.price,
        status=OrderStatus.ACTIVE
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

# ============ 发布更新 ============

@router.post("/updates", status_code=status.HTTP_201_CREATED)
def create_update(
    request: dict,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """为认养对象发布更新（图片、描述、类型）"""
    target_id = request.get("target_id")
    description = request.get("description")
    log_type = request.get("log_type")
    image_urls = request.get("image_urls", [])
    
    if not all([target_id, description, log_type]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # 验证认养对象
    target = db.query(AdoptTarget).filter(AdoptTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    # 验证更新类型
    try:
        log_type_enum = LogType(log_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid log_type. Must be one of: {[e.value for e in LogType]}")
    
    update = UpdateLog(
        target_id=target_id,
        description=description,
        log_type=log_type_enum,
        image_urls=image_urls if image_urls else None
    )
    db.add(update)
    db.commit()
    db.refresh(update)
    return update

@router.get("/updates", response_model=List[UpdateLogOut])
def list_updates(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取所有更新记录（管理员）"""
    updates = db.query(UpdateLog).offset(skip).limit(limit).all()
    return updates

# ============ 物流/配送管理 ============

@router.post("/deliveries", status_code=status.HTTP_201_CREATED)
def create_delivery(
    request: dict,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """创建配送记录"""
    order_id = request.get("order_id")
    content_desc = request.get("content_desc")
    tracking_number = request.get("tracking_number")
    
    if not all([order_id, content_desc]):
        raise HTTPException(status_code=400, detail="Missing required fields: order_id, content_desc")
    
    # 验证订单是否存在
    order = db.query(AdoptOrder).filter(AdoptOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    delivery = DeliveryLog(
        order_id=order_id,
        content_desc=content_desc,
        tracking_number=tracking_number,
        status=DeliveryStatus.PENDING
    )
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return {"id": delivery.id, "message": "Delivery created successfully"}


import os, uuid
from fastapi import UploadFile, File

UPLOAD_DIR = "/opt/farm-adopt/static/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_image(file: UploadFile = File(...), current_user: User = Depends(get_admin_user)):
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = uuid.uuid4().hex + ext
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())
    return {"url": f"/static/images/{filename}"}

@router.patch("/targets/{target_id}/cover")
def update_target_cover(target_id: int, data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    target = db.query(AdoptTarget).filter(AdoptTarget.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    target.cover_image = data.get("cover_image")
    db.commit()
    return {"ok": True}
