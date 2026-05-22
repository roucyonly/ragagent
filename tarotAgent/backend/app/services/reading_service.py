import json
import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.llm.base import get_provider
from app.models.reading import Reading
from app.prompts.brief_reading import build_brief_prompt
from app.prompts.detailed_reading import build_detailed_prompt
from app.prompts.follow_up import build_follow_up_prompt

TOPICS = {
    "love": "桃花/爱情",
    "career": "事业",
    "destiny": "正缘",
    "family": "家庭",
    "general": "综合运势",
}


def _load_cards_data() -> dict:
    path = os.path.join(settings.DATA_DIR, "tarot_cards.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_card_by_id(card_id: int) -> dict | None:
    data = _load_cards_data()
    for card in data["cards"]:
        if card["card_id"] == card_id:
            return card
    return None


def format_cards_text(cards_drawn: list[dict]) -> str:
    position_names = {"past": "过去", "present": "现在", "future": "未来"}
    lines = []
    for card_data in cards_drawn:
        card_info = get_card_by_id(card_data["card_id"])
        if not card_info:
            continue
        pos = position_names.get(card_data.get("position", ""), card_data.get("position", ""))
        reverse = "（逆位）" if card_data.get("is_reversed") else "（正位）"
        lines.append(f"- {pos}：{card_info['name_cn']} ({card_info['name_en']}){reverse}")
    return "\n".join(lines)


def format_cards_meanings(cards_drawn: list[dict], topic: str) -> str:
    lines = []
    for card_data in cards_drawn:
        card_info = get_card_by_id(card_data["card_id"])
        if not card_info:
            continue
        reverse = card_data.get("is_reversed", False)
        pos_key = "reversed_cn" if reverse else "upright_cn"

        kw = card_info["keywords"].get(pos_key, [])
        meaning = card_info["meanings"].get(pos_key, "")
        topic_meaning = ""
        if topic in card_info.get("topic_meanings", {}):
            topic_meaning = card_info["topic_meanings"][topic].get(pos_key, "")

        lines.append(
            f"【{card_info['name_cn']}】\n"
            f"关键词：{', '.join(kw)}\n"
            f"基本含义：{meaning}\n"
            f"话题含义：{topic_meaning}"
        )
    return "\n\n".join(lines)


def build_user_info(user) -> str:
    parts = []
    if user.name:
        parts.append(f"姓名：{user.name}")
    if user.gender:
        parts.append(f"性别：{user.gender}")
    if user.birth_date:
        parts.append(f"出生日期：{user.birth_date}")
    return "；".join(parts) if parts else ""


async def generate_brief_reading(db: AsyncSession, reading: Reading, user) -> str:
    topic_name = TOPICS.get(reading.topic, reading.topic)
    cards_text = format_cards_text(reading.cards_drawn)
    user_info = build_user_info(user)

    system_prompt, user_prompt = build_brief_prompt(
        topic_name=topic_name,
        question=reading.question_text,
        cards_text=cards_text,
        user_info=user_info,
    )

    provider = get_provider()
    result = await provider.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=400,
        temperature=0.8,
    )

    reading.brief_reading = result
    reading.llm_provider = settings.LLM_PROVIDER
    reading.llm_model = getattr(provider, "model", None)
    db.add(reading)
    await db.commit()
    return result


async def generate_detailed_reading(db: AsyncSession, reading: Reading, user) -> str:
    topic_name = TOPICS.get(reading.topic, reading.topic)
    cards_text = format_cards_text(reading.cards_drawn)
    cards_meanings = format_cards_meanings(reading.cards_drawn, reading.topic)
    user_info = build_user_info(user)

    system_prompt, user_prompt = build_detailed_prompt(
        topic_name=topic_name,
        question=reading.question_text,
        cards_text=cards_text,
        cards_meanings=cards_meanings,
        user_info=user_info,
    )

    provider = get_provider()
    result = await provider.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=2000,
        temperature=0.7,
    )

    reading.detailed_reading = result
    reading.status = "completed"
    db.add(reading)
    await db.commit()
    return result


async def stream_detailed_reading(db: AsyncSession, reading: Reading, user):
    topic_name = TOPICS.get(reading.topic, reading.topic)
    cards_text = format_cards_text(reading.cards_drawn)
    cards_meanings = format_cards_meanings(reading.cards_drawn, reading.topic)
    user_info = build_user_info(user)

    system_prompt, user_prompt = build_detailed_prompt(
        topic_name=topic_name,
        question=reading.question_text,
        cards_text=cards_text,
        cards_meanings=cards_meanings,
        user_info=user_info,
    )

    provider = get_provider()
    full_text = ""

    async for chunk in provider.stream_generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=2000,
        temperature=0.7,
    ):
        full_text += chunk
        yield chunk

    reading.detailed_reading = full_text
    reading.status = "completed"
    db.add(reading)
    await db.commit()


async def generate_follow_up(db: AsyncSession, reading: Reading, user, question: str):
    if reading.follow_up_count >= 3:
        raise ValueError("最多只能追问3次")

    topic_name = TOPICS.get(reading.topic, reading.topic)
    cards_text = format_cards_text(reading.cards_drawn)
    cards_meanings = format_cards_meanings(reading.cards_drawn, reading.topic)
    user_info = build_user_info(user)

    history = reading.conversation_history or []

    system_prompt, user_prompt = build_follow_up_prompt(
        topic_name=topic_name,
        question=reading.question_text,
        cards_text=cards_text,
        cards_meanings=cards_meanings,
        user_info=user_info,
        history=history,
        follow_up_question=question,
    )

    provider = get_provider()
    result = await provider.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=1000,
        temperature=0.7,
    )

    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": result})

    reading.follow_up_count += 1
    reading.conversation_history = history
    reading.detailed_reading = (reading.detailed_reading or "") + f"\n\n【追问 {reading.follow_up_count}】\n{question}\n\n答案：{result}"
    db.add(reading)
    await db.commit()
    return result
