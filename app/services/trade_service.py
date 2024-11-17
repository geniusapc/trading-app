from ib_insync import Forex, Trade, Order, Contract
from typing import List

def process_trades(trades: List[Trade]):
    trade_data = []
    for trade in trades:
        contract = trade.contract
        order = trade.order
        order_status = trade.orderStatus

        trade_info = {
            "symbol": contract.localSymbol,
            "action": order.action,
            "quantity": order.totalQuantity,
            "status": order_status.status,
            "filled": order_status.filled,
            "remaining": order_status.remaining,
            "average_fill_price": order_status.avgFillPrice,
            "profit": calculate_profit(order_status.filled, order_status.avgFillPrice, contract)
        }
        trade_data.append(trade_info)
    return trade_data

def calculate_profit(filled, avg_fill_price, contract):
    if filled > 0:
        return filled * avg_fill_price
    return 0.0