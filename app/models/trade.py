from pydantic import BaseModel
from typing import Optional

class TradeRequest(BaseModel):
    symbol: str
    size: int
    expiry: str
    action: str
    ib_symbol: Optional[str] = None  # Make ib_symbol optional with a default value of None
