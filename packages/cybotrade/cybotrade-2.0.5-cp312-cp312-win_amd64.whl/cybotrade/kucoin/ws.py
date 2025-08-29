import uuid
import json
import logging
from typing import Any
from decimal import Decimal
from datetime import datetime, timezone

from cybotrade.models import (
    Exchange,
    OrderSide,
    OrderStatus,
    OrderType,
    OrderUpdate,
    Symbol,
    SymbolInfo,
    TimeInForce,
)
from cybotrade.io.event import Event, EventType
from cybotrade.io.exchange import ExchangeEvent
from cybotrade.exceptions import DeserializationError

from .linear import KucoinLinearClient


class KucoinPrivateWS(ExchangeEvent):
    """Kucoin exchange client implementing the EventHandler interface."""

    symbol_infos: dict[Symbol, SymbolInfo] | None = None
    last_pong_time: datetime | None = None

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        api_passphrase: str,
        topics: list[str],
        api_key_version: int = 3,
    ):
        self.topics = topics
        self.rest = KucoinLinearClient(
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=api_passphrase,
            api_key_version=api_key_version,
        )

    async def heartbeat(self, sender):
        await sender.ping(None)
        await sender.send(json.dumps({"id": str(uuid.uuid4()), "type": "ping"}))

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

        ws_client = KucoinWsClient("api_key", "api_secret")
        ws_client.on_msg = my_on_msg;
        stream = ws_client.stream()
        ...
        ```
        """
        if self.symbol_infos is None:
            raise Exception(
                "Symbol infos not initialized. Something went wrong in on_connected."
            )

        match msg["type"]:
            case "ack":
                await self.on_event(
                    event=Event(
                        event_type=EventType.Subscribed,
                        orig=msg,
                        data=msg,
                    )
                )
            case "pong":
                self.last_pong_time = datetime.now(tz=timezone.utc)
            case "message":
                match msg["subject"]:
                    case "orderChange":
                        order = msg["data"]
                        symbol = Symbol(order["symbol"])

                        if symbol not in self.symbol_infos:
                            raise Exception(
                                f"Symbol {symbol} not found in symbol infos."
                            )
                        multiplier = self.symbol_infos[symbol].quanto_multiplier
                        if multiplier is None:
                            raise Exception(
                                f"Symbol {symbol} does not have a quanto multiplier."
                            )

                        if "orderType" in order:
                            order_type = OrderType.from_str(order["orderType"])
                            if order_type is None:
                                raise DeserializationError(
                                    f"Unrecognized order type: {order_type}"
                                )
                        elif order["liquidity"] == "maker":
                            order_type = OrderType.LIMIT
                        else:
                            order_type = OrderType.MARKET

                        order_side = OrderSide.from_str(order["side"])
                        if order_side is None:
                            raise DeserializationError(
                                f"Unrecognized order side: {order_side}"
                            )

                        size = Decimal(order["size"]) * multiplier
                        filled_size = Decimal(order["filledSize"]) * multiplier
                        remain_size = Decimal(order["remainSize"]) * multiplier

                        # status
                        def eval_status(type: str, status: str) -> bool:
                            return order["type"] == type and order["status"] == status

                        if eval_status("open", "open"):
                            status = OrderStatus.CREATED
                        elif eval_status("update", "open"):
                            status = OrderStatus.PARTIALLY_FILLED
                        elif eval_status("canceled", "done"):
                            if size != filled_size and filled_size > 0:
                                status = OrderStatus.PARTIALLY_FILLED_CANCELLED
                            else:
                                status = OrderStatus.CANCELLED
                        elif eval_status("filled", "done"):
                            status = OrderStatus.FILLED
                        elif eval_status("match", "match"):
                            if remain_size == 0:
                                # skip this update (next update will be filled, done)
                                return
                            else:
                                status = OrderStatus.PARTIALLY_FILLED
                        else:
                            raise DeserializationError(
                                f"Unrecognized order type and order status: {order['type']} and {order['status']}"
                            )

                        await self.on_event(
                            Event(
                                event_type=EventType.OrderUpdate,
                                orig=msg,
                                data=OrderUpdate(
                                    symbol=symbol,
                                    order_type=order_type,
                                    side=order_side,
                                    time_in_force=TimeInForce.GTC,  # default to GTC (unable to derive)
                                    status=status,
                                    order_id=order["orderId"],
                                    client_order_id=order["clientOid"],
                                    order_time=datetime.fromtimestamp(
                                        order["orderTime"] // 1_000_000_000
                                    ),
                                    updated_time=datetime.fromtimestamp(
                                        order["ts"] // 1_000_000_000
                                    ),
                                    price=Decimal(order["price"]),
                                    size=size,
                                    filled_size=filled_size,
                                    remain_size=remain_size,
                                    is_reduce_only=False,
                                    is_hedge_mode=False,
                                    exchange=Exchange.KUCOIN_LINEAR,
                                    orig=order,
                                ),
                            )
                        )
                    case _:
                        await self.on_event(
                            Event(event_type=EventType.Unknown, orig=msg, data=None)
                        )

    async def on_connected(self, sender) -> None:
        self.set_sender(sender)
        self.symbol_infos = await self.rest._fetch_symbol_infos()
        await self.on_login()
        await self.on_event(
            event=Event(
                event_type=EventType.Authenticated,
                orig={},
                data={},
            )
        )

    async def on_login(self) -> None:
        for topic in self.topics:
            msg = json.dumps(
                {
                    "id": str(uuid.uuid4()),
                    "type": "subscribe",
                    "topic": topic,
                    "privateChannel": True,
                    "response": True,
                }
            )
            await self.sender.send(msg)

    async def start(self):
        bullet = await self.rest.get_bullet_private()
        server = bullet["instanceServers"][0]
        self.url = (
            f"{server['endpoint']}?token={bullet['token']}&[connectId={uuid.uuid4()}]"
        )
        self.set_heartbeat_interval(int(server["pingInterval"]) // 1_000)

        # TODO: should check last_pong_time and force reconnect if over
        async for item in self._stream():
            try:
                await self.on_msg(item)
            except Exception as e:
                logging.warning(f"Kucoin WS encountered an Exception: {e}")
                continue
