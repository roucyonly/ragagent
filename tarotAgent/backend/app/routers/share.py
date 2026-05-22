from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
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

    # Skip if already generated
    if reading.share_image_url:
        return {"image_url": reading.share_image_url}

    reading_data = {
        "topic_name": TOPICS.get(reading.topic, reading.topic),
        "cards_drawn": reading.cards_drawn,
        "brief_reading": reading.brief_reading,
        "detailed_reading": reading.detailed_reading,
        "created_at": str(reading.created_at),
    }
    user_data = {"name": user.name, "nickname": user.nickname}

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
    import httpx

    result = await db.execute(select(Reading).where(Reading.id == reading_id))
    reading = result.scalar_one_or_none()

    if not reading or reading.user_id != user.id or not reading.share_image_url:
        raise HTTPException(status_code=404, detail="Image not found")

    # Proxy from OSS to avoid default domain forced download
    async with httpx.AsyncClient() as client:
        resp = await client.get(reading.share_image_url)
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to fetch image")

    return Response(
        content=resp.content,
        media_type="image/jpeg",
        headers={"Content-Disposition": f"inline; filename=tarot_{reading_id}.jpg"},
    )
