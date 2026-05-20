from datetime import datetime
from pydantic import BaseModel


class CardDrawn(BaseModel):
    card_id: int
    name_en: str
    name_cn: str
    position: str  # "past" / "present" / "future"
    is_reversed: bool = False


class ReadingCreate(BaseModel):
    topic: str
    question_text: str | None = None
    cards: list[CardDrawn]


class BriefReadingOut(BaseModel):
    id: str
    topic: str
    cards_drawn: list[dict]
    brief_reading: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DetailedReadingOut(BaseModel):
    id: str
    topic: str
    question_text: str | None = None
    cards_drawn: list[dict]
    brief_reading: str
    detailed_reading: str | None = None
    share_image_url: str | None = None
    status: str
    llm_provider: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReadingListItem(BaseModel):
    id: str
    topic: str
    card_count: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
