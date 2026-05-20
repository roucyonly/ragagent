import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.user import TokenOut, UserOut, RegisterIn, LoginIn, UserUpdate

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _create_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    return jwt.encode({"sub": user_id, "exp": expire}, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


@router.post("/register")
async def register(data: RegisterIn, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.nickname == data.nickname))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该昵称已被使用")

    user = User(
        id=str(uuid.uuid4()),
        nickname=data.nickname,
        password_hash=bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode(),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = _create_token(user.id)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/login")
async def login(data: LoginIn, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.nickname == data.nickname))
    user = result.scalar_one_or_none()

    if not user or not user.password_hash or not bcrypt.checkpw(data.password.encode(), user.password_hash.encode()):
        raise HTTPException(status_code=401, detail="昵称或密码错误")

    token = _create_token(user.id)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/refresh")
async def refresh_token(user: User = Depends(get_current_user)):
    token = _create_token(user.id)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))
