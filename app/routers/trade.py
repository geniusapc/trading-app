from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.trade import TradeRequest
from app.services.ib_client import ib, connect_ib
from app.services.trade_service import process_trades, place_deriv_trade, place_tws_trade, is_valid_ib_instrument
from ib_insync import Forex, Order
from typing import List

router = APIRouter()

@router.post("/api/place_trade")
async def place_trade(trade_request: TradeRequest):
    symbol = trade_request.symbol
    size = trade_request.size
    expiry = trade_request.expiry
    action = trade_request.action
    ib_symbol = (trade_request.ib_symbol or trade_request.symbol)[-6:]

    trade_request2 = {
    "symbol": symbol,
    "size": size,
    "expiry": expiry,
    "action": action,
    "ib_symbol":ib_symbol

    }
    print(trade_request2)
    print("_" * 30)

    valid_ib_symbol = await is_valid_ib_instrument(ib_symbol)
    
    if not valid_ib_symbol:
         raise HTTPException(status_code=400, detail= f"Instrument not found or invalid ({ib_symbol})")
    
    await place_deriv_trade(trade_request2)
    await place_tws_trade(trade_request2)
    
    return {"message": f"{action.capitalize()} order for {symbol} placed."}


@router.get("/api/get_ib_orders")
async def get_ib_orders():
    trades = ib.trades()
    processed_trades = process_trades(trades)
    return processed_trades
