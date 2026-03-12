from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token
from app.core.security import verify_password, get_password_hash, create_access_token, decode_token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    token = authorization.split(" ")[1]
    try:
        payload = decode_token(token)
        phone = payload.get("sub")
        if phone is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_admin_user(current_user: User = Depends(get_current_user)):
    """验证用户是否为管理员"""
    # 管理员账号在config中硬编码：admin/farm2026
    if current_user.phone != settings.ADMIN_USERNAME:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # 检查手机号是否已注册
    existing = db.query(User).filter(User.phone == user_in.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone already registered")
    user = User(
        phone=user_in.phone,
        password_hash=get_password_hash(user_in.password),
        nickname=user_in.nickname
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends()):
    # 注意：OAuth2PasswordRequestForm 的 username 字段用作 phone
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.phone == form.username).first()
        if not user or not verify_password(form.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # 检查是否为管理员账号
        is_admin = (user.phone == settings.ADMIN_USERNAME)
        access_token = create_access_token(data={"sub": user.phone, "role": "admin" if is_admin else "user"})
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        db.close()
