import json
import os

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.config import settings

router = APIRouter(prefix="/api/tarot", tags=["tarot"])

TOPICS = [
    {"key": "love", "name": "桃花/爱情", "icon": "💕", "desc": "探索你的感情运势，寻找爱情的答案"},
    {"key": "career", "name": "事业", "icon": "💼", "desc": "揭示职场方向，助力事业腾飞"},
    {"key": "destiny", "name": "正缘", "icon": "💍", "desc": "寻觅命中注定的那个人"},
    {"key": "family", "name": "家庭", "icon": "🏠", "desc": "洞察家庭关系，增进亲情温暖"},
    {"key": "general", "name": "综合运势", "icon": "✨", "desc": "全面解读近期运势走向"},
]


def _load_cards():
    path = os.path.join(settings.DATA_DIR, "tarot_cards.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/cards")
async def list_cards():
    data = _load_cards()
    cards = []
    for card in data["cards"]:
        cards.append({
            "card_id": card["card_id"],
            "name_en": card["name_en"],
            "name_cn": card["name_cn"],
            "arcana": card["arcana"],
            "suit": card.get("suit"),
            "number": card["number"],
            "keywords_cn": card["keywords"].get("upright_cn", []),
        })
    return cards


@router.get("/cards/{card_id}")
async def get_card(card_id: int):
    data = _load_cards()
    for card in data["cards"]:
        if card["card_id"] == card_id:
            return card
    return JSONResponse(status_code=404, content={"detail": "Card not found"})


@router.get("/topics")
async def list_topics():
    return TOPICS
