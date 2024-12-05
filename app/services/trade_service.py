from ib_insync import Forex, Trade, Order, Contract, Stock, Option, LimitOrder
from app.services.ib_client import ib, connect_ib
from typing import List
import websockets
import json
from datetime import datetime, timedelta

APP_ID = 1089
API_KEY = "jVBDVAobhBYJuJY"

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


async def place_deriv_trade(trade_request):
    # Replace `app_id` with yours if needed
    print("This is the service")


   
    uri = f'wss://ws.binaryws.com/websockets/v3?app_id={APP_ID}'

    async with websockets.connect(uri) as websocket:
        # Step 1: Authorize
        await websocket.send(json.dumps({"authorize": API_KEY}))
        auth_response = json.loads(await websocket.recv())
        if "error" in auth_response:
            print("Authorization Error:", auth_response["error"]["message"])
            return

        print("Authorized Successfully:", auth_response.get(
            "authorize", {}).get("email"))

        # Step 2: Place a trade on EUR/USD
        trade_request = {
            "buy": 1,
            "price": 10,  # Amount to trade
            "parameters": {
                "amount": 10,
                "basis": "stake",
                "contract_type": "CALL",  # Predicting the market will rise
                "currency": "USD",
                "duration": 1,  # Update with a valid duration
                "duration_unit": "h",  # Update with a valid unit
                "symbol": "frxEURUSD"  # EUR/USD market
            }
        }

        # await websocket.send(json.dumps(trade_request))
        # trade_response = json.loads(await websocket.recv())

        # if "error" in trade_response:
        #     print("Trade Error:", trade_response["error"]["message"])
        # else:
        #     print("Trade Placed Successfully:", trade_response.get("buy"))

        # # (Optional) Step 3: Monitor the trade result
        # transaction_id = trade_response.get("buy", {}).get("transaction_id")
        # if transaction_id:
        #     await websocket.send(json.dumps({"proposal_open_contract": 1}))
        #     result = json.loads(await websocket.recv())
        #     print("Trade Result:", result)


async def place_tws_trade(trade_request):
    if not ib.isConnected():
        await connect_ib()

    print(trade_request)
    
    ib_symbol  = trade_request["ib_symbol"][:3]
    action  = trade_request["action"].upper()
    totalQuantity = trade_request["size"]


    expiration_date = (datetime.now() + timedelta(days=1)).strftime('%Y%m%d')

    # contract = Forex(ib_symbol)

    option_contract = Option(
        symbol="6A",
        lastTradeDateOrContractMonth=expiration_date,  # Expiration date in YYYYMMDD
        strike=1.10,
        right='C',
        exchange='GLOBEX'
    )

    # order = Order(
    #     action=action,
    #     totalQuantity=totalQuantity,
    #     orderType='MKT'
    # )

    ib.qualifyContracts(option_contract)

    # Define the order
    order = LimitOrder(
        action='BUY',         # Buy the option
        totalQuantity=1,      # Number of contracts
        lmtPrice=0.01         # Limit price (per unit)
    )

    # Place the order
    trade = ib.placeOrder(option_contract, order)



    print(option_contract)
    print(order)
    print("*" * 50)

    # tt =  ib.placeOrder(option_contract, order)
    # print(tt)




async def is_valid_ib_instrument(symbol):
    try:
        contract = Forex(symbol)

        # Request contract details
        details = await  ib.reqContractDetailsAsync(contract)
        
        # If details are returned, the instrument is valid
        return len(details) > 0
    except Exception as e:
        print(f"Error: {e}")
        return False
