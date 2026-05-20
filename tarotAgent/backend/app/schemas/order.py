from datetime import datetime
from pydantic import BaseModel


class OrderCreate(BaseModel):
    reading_id: str
    payment_method: str  # "wechat" / "alipay"


class OrderOut(BaseModel):
    id: str
    reading_id: str
    out_trade_no: str
    amount_cents: int
    payment_method: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderStatusOut(BaseModel):
    out_trade_no: str
    status: str
    paid_at: datetime | None = None
