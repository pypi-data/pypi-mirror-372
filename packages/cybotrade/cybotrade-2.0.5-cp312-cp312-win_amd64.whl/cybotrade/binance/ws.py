import logging
import requests
from typing import Any
from decimal import Decimal
from datetime import datetime

from cybotrade.models import (
    Exchange,
    OrderSide,
    OrderStatus,
    OrderType,
    OrderUpdate,
    TimeInForce,
)
from cybotrade.io.event import Event, EventType
from cybotrade.io.exchange import ExchangeEvent
from cybotrade.exceptions import DeserializationError


def start_user_data_stream(api_key: str, is_testnet: bool) -> str:
    api_url = (
        "https://testnet.binancefuture.com"
        if is_testnet
        else "https://fapi.binance.com"
    )
    resp = requests.post(
        url=f"{api_url}/fapi/v1/listenKey",
        headers={
            "X-MBX-APIKEY": api_key,
            "Content-Type": "application/json",
        },
    )
    print(f"api key: {api_key}")
    data = resp.json()
    print(data)
    return data["listenKey"]


def keepalive_user_data_stream(api_key: str, is_testnet: bool) -> str:
    api_url = (
        "https://testnet.binancefuture.com"
        if is_testnet
        else "https://fapi.binance.com"
    )
    resp = requests.put(
        url=f"{api_url}/fapi/v1/listenKey",
        headers={
            "X-MBX-APIKEY": api_key,
            "Content-Type": "application/json",
        },
    )
    data = resp.json()
    return data["listenKey"]


class BinancePrivateWS(ExchangeEvent):
    """Binance exchange client implementing the EventHandler interface."""

    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        self.listen_key = start_user_data_stream(api_key, testnet)
        self.url = (
            f"wss://fstream.binance.com/ws/{self.listen_key}"
            if not testnet
            else f"wss://stream.binancefuture.com/ws/{self.listen_key}"
        )
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.set_heartbeat_interval(30)

    async def heartbeat(self, sender):
        logging.info("Sending binance heartbeat ping.")
        listen_key = keepalive_user_data_stream(self.api_key, self.testnet)
        logging.info(
            f"Kept alive listenKey {listen_key} and current connected listen_key is {self.listen_key}"
        )
        await sender.ping(None)

    async def on_event(self, event) -> None:
        """
        User-defined
        """
        pass

    async def on_msg(self, msg: dict[str, Any]) -> None:
        """
        Re-assign or overload this method to invoke your logic when the WS client
        receives a msg from the exchange.

        **The default implementation will only actively filter for 'order updates'.**

        E.g:
        ```
        def my_on_msg(msg):
            if msg["topic"] == 'order':
                self.on_order_update(msg)

        ws_client = BinanceWsClient("api_key", "api_secret")
        ws_client.on_msg = my_on_msg;
        stream = ws_client.stream()
        ...
        ```
        """
        if msg.__contains__("e"):
            match msg["e"]:
                case "ORDER_TRADE_UPDATE":
                    order = msg["o"]

                    tif = TimeInForce.from_str(order["f"])
                    if tif is None:
                        tif = order["f"]

                    status = OrderStatus.from_str(order["X"])
                    if status is None:
                        raise DeserializationError(f"Unrecognized status: {order['X']}")

                    order_type = OrderType.from_str(order["o"])
                    if order_type is None:
                        order_type = order["o"]

                    await self.on_event(
                        Event(
                            event_type=EventType.OrderUpdate,
                            data=OrderUpdate(
                                symbol=order["s"],
                                order_type=order_type,
                                side=OrderSide.from_str(order["S"]),
                                time_in_force=tif,
                                order_id=str(order["i"]),
                                client_order_id=order["c"],
                                order_time=datetime.fromtimestamp(
                                    int(order["T"]) / 1000
                                ),
                                updated_time=datetime.fromtimestamp(
                                    int(order["T"]) / 1000
                                ),
                                price=Decimal(order["p"])
                                if Decimal(order["ap"]) == 0
                                else Decimal(order["ap"]),
                                size=Decimal(order["q"]),
                                filled_size=Decimal(order["z"]),
                                remain_size=Decimal(order["q"]) - Decimal(order["z"]),
                                status=status,
                                is_reduce_only=order["R"],
                                is_hedge_mode=False if order["ps"] == "BOTH" else True,
                                exchange=Exchange.BINANCE_LINEAR,
                                orig=order,
                            ),
                            orig=msg,
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

        ws_client = BinanceWsClient("api_key", "api_secret")
        ws_client.on_connected = my_on_connected;
        stream = ws_client.stream()
        ...
        ```
        """
        self.set_sender(sender)
        await self.on_event(
            event=Event(
                event_type=EventType.Authenticated,
                orig={},
                data=None,
            )
        )
        await self.on_login()

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

        ws_client = BinanceWsClient("api_key", "api_secret")
        ws_client.on_connected = my_on_connected;
        stream = ws_client.stream()
        ...
        ```
        """
        await self.on_event(
            event=Event(
                event_type=EventType.Subscribed,
                orig={},
                data=None,
            )
        )

    async def start(self):
        async for item in self._stream():
            try:
                await self.on_msg(item)
            except Exception as e:
                logging.warning(f"Binance WS encountered an Exception: {e}")
                continue
