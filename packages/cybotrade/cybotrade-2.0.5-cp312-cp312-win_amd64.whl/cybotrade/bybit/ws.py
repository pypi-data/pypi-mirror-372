import json
import logging
from typing import Any
from decimal import Decimal
from datetime import datetime

from cybotrade.models import (
    Exchange,
    OrderSide,
    OrderStatus,
    OrderType,
    OrderUpdate,
    Symbol,
    TimeInForce,
)
from cybotrade.io.event import Event, EventType
from cybotrade.io.exchange import ExchangeEvent


class BybitPrivateWS(ExchangeEvent):
    """Bybit exchange client implementing the EventHandler interface."""

    def __init__(
        self, api_key: str, api_secret: str, topics: list[str], testnet: bool = False
    ):
        self.topics = topics
        self.url = (
            "wss://stream.bybit.com/v5/private?max_active_time=330s"
            if not testnet
            else "wss://stream-testnet.bybit.com/v5/private?max_active_time=330s"
        )
        self.api_key = api_key
        self.api_secret = api_secret
        self.set_heartbeat_interval(30)

    def create_auth_message(self) -> str:
        """Create authentication message for Bybit."""
        import time
        import hmac
        import hashlib

        expires = int((time.time() + 10) * 1000)
        signature_payload = f"GET/realtime{expires}"
        signature = hmac.new(
            self.api_secret.encode(), signature_payload.encode(), hashlib.sha256
        ).hexdigest()

        auth_message = json.dumps(
            {
                "op": "auth",
                "args": [self.api_key, expires, signature],
            }
        )

        return auth_message

    def create_subscription_message(self) -> str:
        """Create subscription message for Bybit order updates."""
        subscription_message = json.dumps({"op": "subscribe", "args": self.topics})
        return subscription_message

    async def heartbeat(self, sender):
        logging.info("Sending bybit heartbeat ping.")
        await sender.ping(None)
        await sender.send(json.dumps({"op": "ping"}))

    async def on_event(self, event) -> None:
        """
        User-defined
        """
        pass

    async def on_msg(self, msg: dict[str, Any]) -> None:
        """
        Re-assign or overload this method to invoke your logic when the WS client
        receives a msg from the exchange.

        ***The default implementation will only actively filter for 'order updates'.***

        E.g:
        ```
        def my_on_msg(msg):
            if msg["topic"] == 'order':
                self.on_order_update(msg)

        ws_client = BybitWsClient("api_key", "api_secret")
        ws_client.on_msg = my_on_msg;
        stream = ws_client.stream()
        ...
        ```
        """
        if msg.__contains__("op"):
            match msg["op"]:
                case "auth":
                    # invoke on_login once successfully authenticated
                    if msg["success"]:
                        await self.on_login()

                    event_type = (
                        EventType.Authenticated if msg["success"] else EventType.Error
                    )
                    await self.on_event(
                        event=Event(
                            event_type=event_type,
                            orig=msg,
                            data=msg,
                        )
                    )
                case "subscribe":
                    event_type = (
                        EventType.Subscribed if msg["success"] else EventType.Error
                    )
                    await self.on_event(
                        event=Event(
                            event_type=event_type,
                            orig=msg,
                            data=msg,
                        )
                    )
                case _:
                    pass
        elif msg.__contains__("topic"):
            match msg["topic"]:
                case "order":
                    for update in msg["data"]:
                        order_type = (
                            OrderType.MARKET
                            if update["orderType"] == "Market"
                            else OrderType.LIMIT
                        )
                        side = (
                            OrderSide.BUY if update["side"] == "Buy" else OrderSide.SELL
                        )
                        tif = TimeInForce.from_str(update["timeInForce"])
                        if tif is None:
                            tif = TimeInForce.GTC

                        await self.on_event(
                            Event(
                                event_type=EventType.OrderUpdate,
                                orig=msg,
                                data=OrderUpdate(
                                    symbol=Symbol(update["symbol"]),
                                    order_type=order_type,
                                    side=side,
                                    time_in_force=tif,
                                    order_id=update["orderId"],
                                    order_time=datetime.fromtimestamp(
                                        int(update["createdTime"]) / 1000
                                    ),
                                    updated_time=datetime.fromtimestamp(
                                        int(update["updatedTime"]) / 1000
                                    ),
                                    size=Decimal(update["qty"]),
                                    filled_size=Decimal(update["cumExecQty"]),
                                    remain_size=Decimal(update["leavesQty"]),
                                    price=Decimal(update["price"]),
                                    client_order_id=update.get("orderLinkId", ""),
                                    status=OrderStatus.from_str(update["orderStatus"]),
                                    exchange=Exchange.BYBIT_LINEAR,
                                    is_reduce_only=False,
                                    is_hedge_mode=False,
                                    orig=msg,
                                ),
                            )
                        )
                case _:
                    await self.on_event(
                        Event(event_type=EventType.Unknown, orig=msg, data=None)
                    )

    async def on_connected(self, sender) -> None:
        """
        Re-assign or overload this method to invoke your logic when the WS client
        connects to the exchange.

        If this method is not re-assigned, it will automatically send a login request.

        E.g:
        ```
        def my_on_connected():
            print("Connected to the exchange!")

        ws_client = BybitWsClient("api_key", "api_secret")
        ws_client.on_connected = my_on_connected;
        stream = ws_client.stream()
        ...
        ```
        """
        await sender.send(self.create_auth_message())
        self.set_sender(sender)

    async def on_login(self) -> None:
        """
        Re-assign or overload this method to invoke your logic when the WS client
        connects to the exchange.

        If this method is not re-assigned, it will automatically send a subscription request
        based off the topics provided when instantiating the class.

        E.g:
        ```
        def my_on_connected():
            print("Connected to the exchange!")

        ws_client = BybitWsClient("api_key", "api_secret")
        ws_client.on_connected = my_on_connected;
        stream = ws_client.stream()
        ...
        ```
        """
        await self.sender.send(self.create_subscription_message())

    async def start(self):
        async for item in self._stream():
            try:
                await self.on_msg(item)
            except Exception as e:
                logging.warning(f"Bybit WS encountered an Exception: {e}")
                continue
