# app/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.services.ib_client import connect_ib, disconnect_ib
from app.routers import ui, trade
from fastapi.staticfiles import StaticFiles
import json
import websockets
import asyncio
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import *
import threading
import time
from datetime import datetime, timedelta




# Define the IBAPI Wrapper and Client
class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.nextorderId = None

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print("The next valid order id is:", self.nextorderId)

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        print("orderStatus - orderId:", orderId, "status:", status, "filled:", filled, "remaining:", remaining, "lastFillPrice:", lastFillPrice)

    def openOrder(self, orderId, contract, order, orderState):
        print("openOrder id:", orderId, contract.symbol, contract.secType, "@", contract.exchange, ":", order.action, order.orderType, order.totalQuantity, orderState.status)

    def execDetails(self, reqId, contract, execution):
        print("Order Executed:", reqId, contract.symbol, contract.secType, contract.currency, execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)

# Helper to create options contract
def options_contract(symbol, expiry, strike, right):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = "OPT"  # Options
    contract.exchange = "SMART"  # Use SMART routing
    contract.currency = "USD"
    contract.lastTradeDateOrContractMonth = expiry  # Format: YYYYMMDD
    contract.strike = strike
    contract.right = right  # 'C' for Call, 'P' for Put
    contract.multiplier = "100"
    return contract


app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

ib_client = IBapi()
# Event handlers
@app.on_event("startup")
def startup_event():
    """Start IBAPI connection when the FastAPI app starts."""
    ib_client.connect("127.0.0.1", 7497, 123)
    threading.Thread(target=ib_client.run, daemon=True).start()

    # Wait for connection and orderId to initialize
    for _ in range(10):  # Retry up to 10 seconds
        if isinstance(ib_client.nextorderId, int):
            print("IBAPI connected")
            break
        time.sleep(1)
    else:
        raise HTTPException(status_code=500, detail="Failed to connect to IBAPI")

@app.on_event("shutdown")
def shutdown_event():
    """Disconnect IBAPI when the FastAPI app shuts down."""
    ib_client.disconnect()
    print("IBAPI disconnected")


# Include routers
app.include_router(ui.router)
app.include_router(trade.router)


DERIV_API_URL = "wss://ws.binaryws.com/websockets/v3?app_id=1089"


@app.get("/symbols")
async def get_symbols():
    """
    Fetch and return available symbols from Deriv API.
    """
    async with websockets.connect(DERIV_API_URL) as websocket:
        # Request available symbols
        await websocket.send(json.dumps({"active_symbols": "brief", "product_type": "basic"}))


        response = await websocket.recv()
        data = json.loads(response)

        print(data)

        # Extract and return symbols
        # symbols = [
        #     {"symbol": item["symbol"], "name": item["display_name"]}
        #     for item in data.get("active_symbols", [])
        # ]

        symbols = [
            {"symbol": item["symbol"], "name": item["display_name"]}
            for item in data.get("active_symbols", [])
            if item.get("symbol_type") == "stockindex"
        ]
   
        return {"symbols": symbols}


async def subscribe_ticks(websocket: websockets.WebSocketClientProtocol, client_ws: WebSocket, symbol: str):
    """
    Subscribe to a specific symbol's ticks and forward them to the client WebSocket.
    """
    subscribe_message = {
        "ticks": symbol,
        "subscribe": 1
    }
    await websocket.send(json.dumps(subscribe_message))

    try:
        # Listen for messages from Deriv API and send them to the client
        async for message in websocket:
            data = json.loads(message)
            if "tick" in data:
                print("tick in data")
                tick_info = {
                    "symbol": data["tick"]["symbol"],
                    "price": data["tick"]["quote"]
                }
                try:
                    await client_ws.send_json(tick_info)
                except WebSocketDisconnect:
                    # Stop sending if the client disconnects
                    break
    except Exception as e:
        print(f"Error during subscription: {e}")


@app.websocket("/ws/ticks/{symbol}")
async def ticks_websocket_endpoint(client_ws: WebSocket, symbol: str):
    """
    WebSocket endpoint to provide ticks for the selected symbol.
    """
    await client_ws.accept()
    try:
        # Connect to Deriv's WebSocket API
        async with websockets.connect(DERIV_API_URL) as websocket:
            await subscribe_ticks(websocket, client_ws, symbol)
    except WebSocketDisconnect:
        print(f"Client disconnected: {client_ws.client}")
    except Exception as e:
        try:
            await client_ws.send_json({"error": str(e)})
        except RuntimeError:
            # Avoid errors if the client is already disconnected
            pass
    finally:
        try:
            await client_ws.close()
        except RuntimeError:
            # Avoid errors if the WebSocket is already closed
            pass

# Pydantic model for order details
class OrderRequest(BaseModel):
    symbol: str
    ib_symbol: str
    expiry: str  # Format: YYYYMMDD
    strike: float
    action: str  # 'BUY' or 'SELL'
    quantity: int
    


def place_ib_trade(order, background_tasks):
    """Endpoint to place a market options order."""
    if not ib_client.isConnected():
        raise HTTPException(status_code=500, detail="IBAPI is not connected")

    if ib_client.nextorderId is None:
        raise HTTPException(status_code=500, detail="Order ID not initialized")

    # symbol='OTC_SPC' ib_symbol='APPL' expiry='1 d' strike=100.0 action='buy' quantity=1
    expiry  = (datetime.now() + timedelta(days=1)).strftime('%Y%m%d')
    right = "C" if order.action == "BUY" else "P"
    # Create the contract and order
    contract = options_contract(order.ib_symbol, expiry, order.strike, right)
    print(contract)
    ib_order = Order()
    ib_order.action = order.action
    ib_order.totalQuantity = order.quantity
    ib_order.orderType = "MKT"  # Market order
    ib_order.eTradeOnly = False  # Ensure this attribute is set to False
    ib_order.firmQuoteOnly = False
    print(ib_order)
    # Place the order in a background task
    def place_order_task():
        ib_client.placeOrder(ib_client.nextorderId, contract, ib_order)
        print(f"Market order placed: {ib_client.nextorderId}")
        ib_client.nextorderId += 1

    background_tasks.add_task(place_order_task)
    
@app.post("/api/place-market-order")
async def place_market_order(order: OrderRequest, background_tasks: BackgroundTasks):
    print(order)
    
    
    place_ib_trade(order, background_tasks)
    #    expiry: "1 H",
    #    limit_price: 0
    #    right:"C",
    return {"message": "Market order is being placed", "order_id": "ib_client.nextorderId"}