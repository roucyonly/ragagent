import json
import os
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.models.reading import Reading
from app.models.user import User
from app.schemas.reading import ReadingCreate, BriefReadingOut, DetailedReadingOut
from app.services.reading_service import generate_brief_reading, generate_detailed_reading

router = APIRouter(prefix="/api/readings", tags=["readings"])


def _pick_random_cards() -> list[dict]:
    path = os.path.join(settings.DATA_DIR, "tarot_cards.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    picked = random.sample(data["cards"], 3)
    positions = ["past", "present", "future"]
    cards = []
    for i, card in enumerate(picked):
        cards.append({
            "card_id": card["card_id"],
            "name_en": card["name_en"],
            "name_cn": card["name_cn"],
            "position": positions[i],
            "is_reversed": random.random() > 0.65,
        })
    return cards


@router.post("")
async def create_reading(
    data: ReadingCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BriefReadingOut:
    cards_data = _pick_random_cards()

    reading = Reading(
        user_id=user.id,
        topic="general",
        question_text=data.question_text,
        cards_drawn=cards_data,
        card_count=3,
        status="brief",
    )
    db.add(reading)
    await db.commit()
    await db.refresh(reading)

    if data.mock:
        reading.brief_reading = (
            "三张牌的画面在我眼前徐徐展开。过去的能量显示你曾经历过一段犹豫不决的时期，"
            "那时你总是试图在理智和感性之间寻找平衡。而现在，一股全新的力量正在涌入你的生活，"
            "它带着改变的气息，暗示你正站在一个重要的十字路口。"
            "未来的牌面透露出希望的光芒，如果你能勇敢地跟随内心的指引，"
            "一段意想不到的美好旅程正在前方等待着你。命运的丝线已经悄然编织，只等你去揭开它神秘的面纱……"
        )
        reading.llm_provider = "mock"
        db.add(reading)
        await db.commit()
        await db.refresh(reading)
    else:
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
    mock: bool = False,
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

    if mock:
        reading.detailed_reading = (
            "【整体能量概览】\n"
            "你的牌阵散发着强烈的转变能量。三张牌共同勾勒出一条从迷茫走向清晰的路径，"
            "暗示你正处于命运的关键转折点。\n\n"
            "【逐牌详解】\n"
            "第一张牌——过去的你，经历过一段深刻的内心挣扎。那段时间里你不断地问自己："
            "「这条路真的是我想要的吗？」这种质疑虽然痛苦，但它赋予了你更深层的自我认知。\n\n"
            "第二张牌——此刻的你，正站在一扇崭新的大门前。你手中握着改变的力量，"
            "只需要迈出那一步。周围的能量在催促你：不要再等待那个「完美时机」了。\n\n"
            "第三张牌——未来的方向，呈现出令人欣喜的画面。一张象征希望与丰收的牌出现在这里，"
            "预示着你的勇气将会得到命运的馈赠。\n\n"
            "【牌间关联】\n"
            "过去牌的挣扎为现在牌的觉醒铺平了道路，而未来牌的美好正是对这一旅程的最佳回报。"
            "三张牌之间形成了流畅的能量流动，没有阻碍与逆流。\n\n"
            "【专属建议】\n"
            "信任自己的直觉。你内心深处其实早已知道答案，只是害怕做出那个决定。"
            "塔罗牌提醒你：勇敢不是没有恐惧，而是在恐惧面前依然选择前行。\n\n"
            "【近期展望】\n"
            "未来两周内，你可能会收到一个意想不到的消息或机会。保持开放的心态，"
            "不要因为习惯性的谨慎而错过命运递来的橄榄枝。\n\n"
            "【寄语】\n"
            "星星不会为犹豫的人闪耀。勇敢地走出舒适区，命运之轮已经开始为你转动。"
        )
        reading.status = "completed"
        reading.llm_provider = "mock"
        db.add(reading)
        await db.commit()
        await db.refresh(reading)
    else:
        await generate_detailed_reading(db, reading, user)
        await db.refresh(reading)

    return DetailedReadingOut.model_validate(reading)
