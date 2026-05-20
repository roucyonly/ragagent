from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.reading import Reading
from app.models.user import User
from app.schemas.reading import ReadingCreate, BriefReadingOut, DetailedReadingOut
from app.services.reading_service import generate_brief_reading, generate_detailed_reading

router = APIRouter(prefix="/api/readings", tags=["readings"])


@router.post("")
async def create_reading(
    data: ReadingCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BriefReadingOut:
    if len(data.cards) != 3:
        raise HTTPException(status_code=400, detail="Must select exactly 3 cards")

    positions = {c.position for c in data.cards}
    if positions != {"past", "present", "future"}:
        raise HTTPException(status_code=400, detail="Cards must have positions: past, present, future")

    cards_data = [c.model_dump() for c in data.cards]

    reading = Reading(
        user_id=user.id,
        topic=data.topic,
        question_text=data.question_text,
        cards_drawn=cards_data,
        card_count=3,
        status="brief",
    )
    db.add(reading)
    await db.commit()
    await db.refresh(reading)

    await generate_brief_reading(db, reading, user)
    await db.refresh(reading)

    return BriefReadingOut.model_validate(reading)


@router.get("/{reading_id}")
async def get_reading(
    reading_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DetailedReadingOut:
    result = await db.execute(select(Reading).where(Reading.id == reading_id))
    reading = result.scalar_one_or_none()

    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    if reading.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your reading")

    response = DetailedReadingOut.model_validate(reading)
    if reading.status != "completed":
        response.detailed_reading = None

    return response


@router.post("/{reading_id}/detail")
async def generate_detail(
    reading_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DetailedReadingOut:
    result = await db.execute(select(Reading).where(Reading.id == reading_id))
    reading = result.scalar_one_or_none()

    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    if reading.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your reading")
    if reading.status not in ("paid", "completed"):
        raise HTTPException(status_code=400, detail="Reading not paid yet")
    if reading.status == "completed":
        return DetailedReadingOut.model_validate(reading)

    await generate_detailed_reading(db, reading, user)
    await db.refresh(reading)

    return DetailedReadingOut.model_validate(reading)
