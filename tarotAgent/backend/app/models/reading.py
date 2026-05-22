import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Reading(Base):
    __tablename__ = "readings"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    topic: Mapped[str] = mapped_column(String(32))
    question_text: Mapped[str | None] = mapped_column(Text)
    cards_drawn: Mapped[dict] = mapped_column(JSON)
    card_count: Mapped[int] = mapped_column(Integer, default=3)
    brief_reading: Mapped[str | None] = mapped_column(Text)
    detailed_reading: Mapped[str | None] = mapped_column(Text)
    share_image_url: Mapped[str | None] = mapped_column(String(512))
    follow_up_count: Mapped[int] = mapped_column(Integer, default=0)
    conversation_history: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="brief")
    llm_provider: Mapped[str] = mapped_column(String(32), default="deepseek")
    llm_model: Mapped[str | None] = mapped_column(String(64))
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
