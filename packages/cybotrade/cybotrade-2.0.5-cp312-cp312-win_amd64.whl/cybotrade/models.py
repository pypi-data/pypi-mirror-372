from cybotrade import Symbol
from enum import Enum
from typing import Any
from datetime import datetime
from dataclasses import dataclass
from decimal import Decimal


class Exchange(str, Enum):
    BYBIT_LINEAR = "bybit_linear"
    BINANCE_LINEAR = "binance_linear"
    KUCOIN_LINEAR = "kucoin_linear"


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"
    NONE = "none"

    @staticmethod
    def from_str(s: str):
        match s.upper():
            case "BUY":
                return OrderSide.BUY
            case "SELL":
                return OrderSide.SELL
            case _:
                return OrderSide.NONE


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"

    @staticmethod
    def from_str(s: str):
        match s.upper():
            case "MARKET":
                return OrderType.MARKET
            case "LIMIT":
                return OrderType.LIMIT
            case _:
                return None


class OrderStatus(str, Enum):
    CREATED = "created"
    PARTIALLY_FILLED = "partially_filled"
    PARTIALLY_FILLED_CANCELLED = "partially_filled_cancelled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    UNKNOWN = "unknown"

    @staticmethod
    def from_str(s: str):
        match s.upper():
            case "CREATED" | "NEW" | "OPEN":
                return OrderStatus.CREATED
            case "PARTIALLYFILLED" | "PARTIALLY_FILLED" | "MATCH":
                return OrderStatus.PARTIALLY_FILLED
            case "PARTIALLYFILLEDCANCELLED" | "PARTIALLY_FILLED_CANCELLED":
                return OrderStatus.PARTIALLY_FILLED_CANCELLED
            case "FILLED" | "DONE":
                return OrderStatus.FILLED
            case "CANCELLED" | "CANCELED":
                return OrderStatus.CANCELLED
            case "REJECTED":
                return OrderStatus.REJECTED
            case _:
                return OrderStatus.UNKNOWN


class TimeInForce(str, Enum):
    GTC = "gtc"  # Good till cancelled
    IOC = "ioc"  # Immediate or cancel
    FOK = "fok"  # Fill or kill
    GTX = "gtx"  # Good till crossing (post only)
    GTD = "gtd"  # Good till date
    GTT = "gtt"  # Good till time

    @staticmethod
    def from_str(tif: str):
        match tif.upper():
            case "GTC":
                return TimeInForce.GTC
            case "IOC":
                return TimeInForce.IOC
            case "FOK":
                return TimeInForce.FOK
            case "POSTONLY" | "POST_ONLY" | "GTX":
                return TimeInForce.GTX
            case "GTD":
                return TimeInForce.GTD
            case "GTT":
                return TimeInForce.GTT
            case "_":
                return None


class PositionSide(str, Enum):
    CLOSED = "closed"
    ONE_WAY_LONG = "one_way_long"
    ONE_WAY_SHORT = "one_way_short"
    HEDGE_LONG = "hedge_long"
    HEDGE_SHORT = "hedge_short"


class PositionMargin(str, Enum):
    CROSS = "cross"
    ISOLATED = "isolated"


class Interval(str, Enum):
    ONE_MINUTE = "1m"
    THREE_MINUTE = "3m"
    FIVE_MINUTE = "5m"
    FIFTEEN_MINUTE = "15m"
    THIRTY_MINUTE = "30m"
    ONE_HOUR = "1h"
    TWO_HOUR = "2h"
    FOUR_HOUR = "4h"
    SIX_HOUR = "6h"
    TWELVE_HOUR = "12h"
    ONE_DAY = "1d"
    THREE_DAY = "3d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"


class Direction(str, Enum):
    UP = "up"
    DOWN = "down"


@dataclass
class OrderUpdate:
    symbol: Symbol
    order_type: OrderType
    side: OrderSide
    time_in_force: TimeInForce
    order_id: str
    order_time: datetime
    updated_time: datetime
    size: Decimal
    filled_size: Decimal
    remain_size: Decimal
    price: Decimal
    client_order_id: str
    status: OrderStatus
    exchange: Exchange
    is_reduce_only: bool
    is_hedge_mode: bool
    orig: dict


@dataclass
class Level:
    price: Decimal
    quantity: Decimal


@dataclass
class OrderbookSnapshot:
    symbol: Symbol
    last_update_time: datetime
    last_update_id: int | None
    bids: list[Level]
    asks: list[Level]
    exchange: Exchange
    orig: dict[str, Any] | None


@dataclass
class OrderResponse:
    exchange: Exchange
    order_id: str
    client_order_id: str
    exchange_response: dict


@dataclass
class Position:
    symbol: Symbol
    quantity: Decimal
    entry_price: Decimal
    updated_time: datetime
    orig: dict[str, Any] | None = None


@dataclass
class Balance:
    exchange: Exchange
    coin: str | None
    wallet_balance: Decimal
    available_balance: Decimal
    equity: Decimal
    unrealised_pnl: Decimal
    initial_margin: Decimal | None
    margin_balance: Decimal | None
    maintenance_margin: Decimal | None
    orig: dict


@dataclass
class Order:
    order_id: str
    client_order_id: str
    symbol: str | None
    time_in_force: TimeInForce | None
    side: OrderSide | None
    order_type: OrderType | None
    exchange: Exchange
    price: float
    quantity: float
    is_reduce_only: bool | None
    orig: dict[str, Any] | None = None


@dataclass
class StopParams:
    trigger_direction: Direction
    trigger_price: float


@dataclass
class OrderParams:
    side: OrderSide
    quantity: float
    symbol: Symbol
    exchange: Exchange
    is_hedge_mode: bool
    limit: float | None
    stop: StopParams | None
    reduce: bool | None
    client_order_id: str | None
    market_price: float | None
    is_post_only: bool | None


@dataclass
class OpenedTrade:
    quantity: float
    side: OrderSide
    price: float
    time: datetime


@dataclass
class FloatWithTime:
    value: float
    timestamp: datetime


@dataclass
class ActiveOrderParams:
    quantity: float
    take_profit: float | None
    stop_loss: float | None
    side: OrderSide


@dataclass
class ActiveOrder:
    params: ActiveOrderParams
    symbol: Symbol
    exchange: Exchange
    updated_time: int
    created_time: int
    order_id: str
    client_order_id: str


@dataclass
class SymbolInfo:
    symbol: Symbol
    quantity_precision: int
    price_precision: int
    exchange: Exchange
    tick_size: Decimal
    max_post_only_qty: Decimal
    max_limit_qty: Decimal
    min_limit_qty: Decimal
    max_market_qty: Decimal
    min_market_qty: Decimal | None
    min_notional: Decimal
    max_notional: Decimal
    quanto_multiplier: Decimal | None


@dataclass
class OrderBookSubscriptionParams:
    depth: int
    speed: int | None
    extra_params: dict[str, str] | None
