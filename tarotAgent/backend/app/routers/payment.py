from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut, OrderStatusOut
from app.services.payment_service import create_order, mock_pay_success, get_order_status

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.post("/create-order")
async def create_payment_order(
    data: OrderCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrderOut:
    order = await create_order(db, data.reading_id, user.id, data.payment_method)
    return OrderOut.model_validate(order)


@router.post("/mock-pay/{out_trade_no}")
async def mock_pay(out_trade_no: str, db: AsyncSession = Depends(get_db)) -> OrderOut:
    """Dev only: instantly mark an order as paid."""
    order = await mock_pay_success(db, out_trade_no)
    return OrderOut.model_validate(order)


@router.post("/wechat-notify")
async def wechat_notify():
    """Stub: WeChat payment callback. Implement with real signature verification in production."""
    return {"code": "SUCCESS", "message": "Mock received"}


@router.post("/alipay-notify")
async def alipay_notify():
    """Stub: Alipay payment callback."""
    return "success"


@router.get("/order/{out_trade_no}/status")
async def order_status(out_trade_no: str, db: AsyncSession = Depends(get_db)) -> OrderStatusOut:
    status_data = await get_order_status(db, out_trade_no)
    return OrderStatusOut(**status_data)
