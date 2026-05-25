from datetime import datetime
from pydantic import BaseModel


class ReadingCreate(BaseModel):
    question_text: str
    mock: bool = False


class CardDrawn(BaseModel):
    card_id: int
    name_en: str
    name_cn: str
    position: str
    is_reversed: bool = False


class BriefReadingOut(BaseModel):
    id: str
    topic: str = ""
    question_text: str | None = None
    cards_drawn: list[dict]
    card_count: int = 0
    brief_reading: str | None = None
    status: str = "draft"
    cards_selected_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class DetailedReadingOut(BaseModel):
    id: str
    topic: str = ""
    question_text: str | None = None
    cards_drawn: list[dict]
    brief_reading: str
    detailed_reading: str | None = None
    share_image_url: str | None = None
    status: str
    llm_provider: str
    follow_up_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class FollowUpIn(BaseModel):
    question: str


class ReadingListItem(BaseModel):
    id: str
    question_text: str | None = None
    topic: str
    card_count: int
    cards_drawn: list[dict]
    brief_reading: str | None = None
    status: str
    cards_selected_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
