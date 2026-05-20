import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.user import TokenOut, UserOut, UserCreate

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _create_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    return jwt.encode({"sub": user_id, "exp": expire}, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


@router.get("/wechat/callback")
async def wechat_callback(code: str, db: AsyncSession = Depends(get_db)):
    """V1 mock: auto-create user from code. Production: exchange code for openid via WeChat API."""
    mock_openid = f"wx_mock_{code[:16]}" if len(code) >= 16 else f"wx_mock_{code}"

    result = await db.execute(select(User).where(User.openid == mock_openid))
    user = result.scalar_one_or_none()

    if not user:
        user = User(openid=mock_openid, nickname="微信用户")
        db.add(user)
        await db.commit()
        await db.refresh(user)

    token = _create_token(user.id)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/guest")
async def guest_login(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a user with profile info directly."""
    user = User(
        openid=f"guest_{uuid.uuid4().hex[:8]}",
        nickname=data.name,
        name=data.name,
        gender=data.gender,
        birth_date=data.birth_date,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = _create_token(user.id)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/refresh")
async def refresh_token(user: User = Depends(get_current_user)):
    token = _create_token(user.id)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))
