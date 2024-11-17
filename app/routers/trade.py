from fastapi import APIRouter, BackgroundTasks
from app.models.trade import TradeRequest
from app.services.ib_client import ib, connect_ib
from app.services.trade_service import process_trades
from ib_insync import Forex, Order
from typing import List

router = APIRouter()

@router.post("/api/place_trade")
async def place_trade(trade_request: TradeRequest, background_tasks: BackgroundTasks):
    symbol = trade_request.symbol
    size = trade_request.size
    expiry = trade_request.expiry
    action = trade_request.action

    if not ib.isConnected():
        await connect_ib()

    contract = Forex(symbol)
    order = Order(
        action=action.upper(),
        totalQuantity=size,
        orderType='MKT'
    )

    ib.placeOrder(contract, order)
    return {"message": f"{action.capitalize()} order for {symbol} placed."}

@router.get("/api/get_ib_orders")
async def get_ib_orders():
    trades = ib.trades()
    processed_trades = process_trades(trades)
    return processed_trades
