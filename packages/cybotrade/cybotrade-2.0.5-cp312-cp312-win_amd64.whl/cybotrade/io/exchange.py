import logging
from decimal import Decimal
from abc import ABC, abstractmethod
from typing import AsyncIterator, Any

from cybotrade import Symbol
from cybotrade.models import (
    Exchange,
    TimeInForce,
    OrderbookSnapshot,
    OrderResponse,
    OrderUpdate,
    Position,
    OrderSide,
    Balance,
    SymbolInfo,
)
from cybotrade.http import Client
from cybotrade.io import EventHandler
from cybotrade.event import ws_stream, WsSender


class ExchangeClient(ABC):
    """
    Abstract base class for cryptocurrency exchange API clients.

    This class provides a foundation for implementing exchange-specific clients
    by defining common methods for trading operations.
    """

    logger: logging.Logger = logging.getLogger(__name__)

    def __init__(self):
        """
        Initialize the exchange client.

        Args:
            api_key: API key for authentication
            api_secret: API secret for authentication
            testnet: Determine which environment the API key is tied to.
        """
        self.client = Client()

    @abstractmethod
    def exchange(self) -> Exchange:
        """
        Get the exchange of the current client.

        Returns:
            Exchange, it is a StrEnum of which exchange this client talks to.
        """

    @abstractmethod
    async def place_order(
        self,
        symbol: Symbol,
        side: OrderSide,
        quantity: Decimal,
        limit: Decimal | None = None,
        client_order_id: str | None = None,
        time_in_force: TimeInForce = TimeInForce.GTC,
        post_only: bool = False,
        **kwargs,
    ) -> OrderResponse:
        """
        Place an order on the exchange.

        Args:
            symbol: Trading pair symbol (e.g., "BTC/USDT")
            side: Order side (buy or sell)
            order_type: Order type (limit or market)
            quantity: Order quantity
            price: Order price (required for limit orders, ignored for market orders)

        Returns:
            Order details from the exchange
        """
        pass

    @abstractmethod
    async def cancel_order(
        self,
        symbol: Symbol,
        order_id: str | None = None,
        client_order_id: str | None = None,
        **kwargs,
    ) -> OrderResponse:
        """
        Cancels an order on the exchange.

        Args:
            symbol: Trading pair symbol (e.g., "BTC/USDT")
            id: order id from exchange or client-set to cancel.

        Returns:
            Order details from the exchange
        """
        pass

    @abstractmethod
    async def get_positions(
        self, symbol: Symbol | None = None, **kwargs
    ) -> list[Position]:
        """
        Get current positions.

        Args:
            symbol: Optional trading pair symbol to filter positions

        Returns:
            List of position details
        """
        pass

    @abstractmethod
    async def get_wallet_balance(self, coin: str | None = None, **kwargs) -> Balance:
        """
        Get wallet balances.

        Args:
            coin: Optional coin to filter balances

        Returns:
            Wallet balance details
        """
        pass

    @abstractmethod
    async def get_order_details(
        self,
        symbol: Symbol | None = None,
        order_id: str | None = None,
        client_order_id: str | None = None,
        **kwargs,
    ) -> OrderUpdate | None:
        """"""
        pass

    @abstractmethod
    async def get_open_orders(
        self, symbol: Symbol | None = None, **kwargs
    ) -> list[OrderUpdate]:
        """"""
        pass

    @abstractmethod
    async def get_symbol_info(self, symbol: Symbol, **kwargs) -> SymbolInfo:
        """"""
        pass

    @abstractmethod
    async def get_orderbook_snapshot(
        self, symbol: Symbol, **kwargs
    ) -> OrderbookSnapshot:
        """
        Get orderbook snapshot for symbol.

        Args:
            symbol: trading pair to query for orderbook.

        Returns:
            Orderbook snapshot for requested symbol.
        """
        pass

    @abstractmethod
    async def get_order_details_from_history(
        self,
        symbol: Symbol | None = None,
        order_id: str | None = None,
        client_order_id: str | None = None,
        **kwargs,
    ) -> OrderUpdate | None:
        """
        Get a id-specific order from the exchange's order history.
        The intended use case of this function is to be able to validate/verify an order's state
        on the exchange on demand.

        Note: if both parameters are provided, the order_id will be prioritized.

        Args:
            order_id: Optional id from exchange
            client_order_id: Optional user-set id

        Returns:
            List of Order dataclasses
        """
        pass

    async def get_current_price(self, symbol: Symbol) -> Decimal:
        """
        Get current price for symbol.

        Args:
            symbol: traded pair to query for price.

        Returns:
            Wallet balance details
        """
        snapshot = await self.get_orderbook_snapshot(symbol)
        return (snapshot.bids[-1].price + snapshot.asks[0].price) / Decimal("2.0")


class ExchangeEvent(EventHandler):
    heartbeat_interval: int = 120
    url: str
    sender: WsSender

    def set_heartbeat_interval(self, interval: int):
        """Assign heartbeat interval"""
        self.heartbeat_interval = interval
        pass

    def set_sender(self, sender: WsSender) -> None:
        self.sender = sender

    @abstractmethod
    async def heartbeat(self, sender: WsSender):
        """Send heartbeat"""
        pass

    @abstractmethod
    async def on_msg(self, msg) -> None:
        """Called when message is returned from Exchange WS connection."""
        pass

    @abstractmethod
    async def on_connected(self, sender: WsSender) -> None:
        """Send authentication."""
        pass

    @abstractmethod
    async def on_login(self) -> None:
        """Send subscription."""
        pass

    async def _stream(self) -> AsyncIterator[dict[str, Any]]:
        """
        Provide an async iterator interface to the exchange stream.

        Usage:
            async for msg in client.stream():
                print(f"Received: {msg}")
        """
        _sender, stream_iter = await ws_stream(self.url, self.heartbeat_interval, self)

        try:
            while True:
                try:
                    msg_text = await stream_iter.__anext__()
                    yield msg_text
                except StopAsyncIteration:
                    break
                except Exception as e:
                    print(f"Stream error: {e}")
                    break
        finally:
            pass
