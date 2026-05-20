import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.order import Order
from app.models.reading import Reading


async def create_order(db: AsyncSession, reading_id: str, user_id: str, payment_method: str) -> Order:
    result = await db.execute(select(Reading).where(Reading.id == reading_id))
    reading = result.scalar_one_or_none()
    if not reading:
        raise ValueError("Reading not found")
    if reading.user_id != user_id:
        raise ValueError("Not your reading")

    out_trade_no = f"TO{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}"

    order = Order(
        reading_id=reading_id,
        user_id=user_id,
        out_trade_no=out_trade_no,
        amount_cents=settings.READING_PRICE_CENTS,
        payment_method=payment_method,
        status="pending",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


async def mock_pay_success(db: AsyncSession, out_trade_no: str) -> Order:
    """V1 mock: mark order as paid for development testing."""
    result = await db.execute(select(Order).where(Order.out_trade_no == out_trade_no))
    order = result.scalar_one_or_none()
    if not order:
        raise ValueError("Order not found")

    order.status = "paid"
    order.paid_at = datetime.now()
    order.transaction_id = f"MOCK_{uuid.uuid4().hex[:12]}"
    order.raw_callback = {"mock": True, "paid_at": order.paid_at.isoformat()}

    result2 = await db.execute(select(Reading).where(Reading.id == order.reading_id))
    reading = result2.scalar_one_or_none()
    if reading:
        reading.status = "paid"

    db.add(order)
    if reading:
        db.add(reading)
    await db.commit()
    return order


async def get_order_status(db: AsyncSession, out_trade_no: str) -> dict:
    result = await db.execute(select(Order).where(Order.out_trade_no == out_trade_no))
    order = result.scalar_one_or_none()
    if not order:
        raise ValueError("Order not found")
    return {
        "out_trade_no": order.out_trade_no,
        "status": order.status,
        "paid_at": order.paid_at.isoformat() if order.paid_at else None,
    }
