"""Data models for trading operations."""

from dataclasses import dataclass
from enum import Enum
from typing import TypedDict


class OrderType(Enum):
    """Order types for trading"""

    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """Order status types"""

    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    """Represents a trading order"""

    symbol: str
    order_type: OrderType
    quantity: float
    price: float
    order_id: str | None = None
    status: OrderStatus = OrderStatus.PENDING


class Position(TypedDict):
    """Represents a position in the account"""

    symbol: str
    quantity: float
    price: float


class AccountInfo(TypedDict):
    """Represents account information"""

    username: str
    account_balance: float
    positions: list[Position]


class MarketData(TypedDict):
    """Represents market data for a symbol"""

    symbol: str
    last_price: float
    bid_price: float
    ask_price: float
    volume: int
    timestamp: str
