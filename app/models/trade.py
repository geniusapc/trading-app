from pydantic import BaseModel

class TradeRequest(BaseModel):
    symbol: str
    size: int
    expiry: str
    action: str