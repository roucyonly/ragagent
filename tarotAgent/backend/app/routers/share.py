from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.reading import Reading
from app.models.user import User
from app.services.reading_service import TOPICS
from app.services.image_service import generate_share_image

router = APIRouter(prefix="/api/share", tags=["share"])


@router.post("/generate-image/{reading_id}")
async def gen_image(
    reading_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Reading).where(Reading.id == reading_id))
    reading = result.scalar_one_or_none()

    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    if reading.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your reading")
    if reading.status != "completed":
        raise HTTPException(status_code=400, detail="Detailed reading not generated yet")

    reading_data = {
        "topic_name": TOPICS.get(reading.topic, reading.topic),
        "cards_drawn": reading.cards_drawn,
        "brief_reading": reading.brief_reading,
        "detailed_reading": reading.detailed_reading,
        "created_at": str(reading.created_at),
    }
    user_data = {"name": user.name}

    image_url = await generate_share_image(reading_id, reading_data, user_data)

    reading.share_image_url = image_url
    db.add(reading)
    await db.commit()

    return {"image_url": image_url}


@router.get("/image/{reading_id}")
async def get_image(
    reading_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    import os
    from app.config import settings

    result = await db.execute(select(Reading).where(Reading.id == reading_id))
    reading = result.scalar_one_or_none()

    if not reading or reading.user_id != user.id or not reading.share_image_url:
        raise HTTPException(status_code=404, detail="Image not found")

    file_path = os.path.join(settings.STATIC_DIR, "generated", f"{reading_id}.png")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image file not found")

    return FileResponse(file_path, media_type="image/png", filename=f"tarot_{reading_id}.png")
