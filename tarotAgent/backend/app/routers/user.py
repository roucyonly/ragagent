from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.reading import Reading
from app.models.user import User
from app.schemas.reading import ReadingListItem
from app.schemas.user import UserOut, UserUpdate

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user)


@router.put("/profile")
async def update_profile(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    if data.name is not None:
        user.name = data.name
    if data.gender is not None:
        user.gender = data.gender
    if data.birth_date is not None:
        user.birth_date = data.birth_date
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserOut.model_validate(user)


@router.get("/readings")
async def list_readings(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
) -> list[ReadingListItem]:
    result = await db.execute(
        select(Reading)
        .where(Reading.user_id == user.id)
        .order_by(Reading.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    readings = result.scalars().all()
    return [ReadingListItem.model_validate(r) for r in readings]
