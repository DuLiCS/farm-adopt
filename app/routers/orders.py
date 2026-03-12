from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta, date

from app.database import SessionLocal
from app.models.user import User
from app.models.adopt_order import AdoptOrder, PlanType, OrderStatus
from app.models.adopt_target import AdoptTarget
from app.models.update_log import UpdateLog
from app.models.delivery_log import DeliveryLog
from app.schemas.adopt_order import AdoptOrderOut, AdoptOrderCreate
from app.schemas.update_log import UpdateLogOut
from app.schemas.delivery_log import DeliveryLogOut
from app.core.security import decode_token

router = APIRouter(prefix="/orders", tags=["orders"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    print(f"DEBUG: get_current_user called, auth header: {authorization[:20] if authorization else None}...")  # 调试
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    token = authorization.split(" ")[1]
    try:
        payload = decode_token(token)
        phone = payload.get("sub")
        if phone is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"DEBUG: Token decode error: {e}")  # 调试日志
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=AdoptOrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: AdoptOrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    用户创建订单
    """
    # 验证目标是否存在且可认养
    target = db.query(AdoptTarget).filter(AdoptTarget.id == order_data.target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="认养对象不存在")

    # 将前端传来的 plan_type 映射到数据库支持的类型
    plan_type_map = {
        'tea_basic': PlanType.TRIAL,
        'tea_standard': PlanType.SEASON,
        'plant_basic': PlanType.TRIAL,
        'season': PlanType.SEASON,
        'annual': PlanType.ANNUAL,
        'trial': PlanType.TRIAL,
    }
    plan_type = plan_type_map.get(order_data.plan_type)
    if not plan_type:
        raise HTTPException(status_code=400, detail=f"不支持的套餐类型: {order_data.plan_type}")

    # 计算过期时间
    start_date = date.today()
    if plan_type == PlanType.SEASON:
        expire_date = start_date + timedelta(days=90)
    elif plan_type == PlanType.ANNUAL:
        expire_date = start_date + timedelta(days=365)
    elif plan_type == PlanType.TRIAL:
        expire_date = start_date + timedelta(days=30)

    # 创建订单
    order = AdoptOrder(
        user_id=current_user.id,
        target_id=order_data.target_id,
        start_date=start_date,
        expire_date=expire_date,
        plan_type=plan_type,
        price=order_data.price,
        status=OrderStatus.ACTIVE
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

@router.get("/me", response_model=List[AdoptOrderOut])
def get_my_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    orders = db.query(AdoptOrder).filter(AdoptOrder.user_id == current_user.id).all()
    return orders

@router.get("/{order_id}/updates", response_model=List[UpdateLogOut])
def get_order_updates(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(AdoptOrder).filter(AdoptOrder.id == order_id, AdoptOrder.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    updates = db.query(UpdateLog).filter(UpdateLog.target_id == order.target_id).all()
    return updates

@router.get("/{order_id}/deliveries", response_model=List[DeliveryLogOut])
def get_order_deliveries(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(AdoptOrder).filter(AdoptOrder.id == order_id, AdoptOrder.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    deliveries = db.query(DeliveryLog).filter(DeliveryLog.order_id == order_id).all()
    return deliveries