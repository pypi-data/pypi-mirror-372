import sys
import time
import hmac
import json
import hashlib
import urllib.parse
from decimal import Decimal
from datetime import datetime
from typing import override, Any

from cybotrade import Symbol
from cybotrade.exceptions import DeserializationError, InvalidParameterError
from cybotrade.binance.exceptions import BinanceError
from cybotrade.io.exchange import ExchangeClient
from cybotrade.models import (
    Exchange,
    Level,
    OrderbookSnapshot,
    OrderResponse,
    OrderUpdate,
    Position,
    Balance,
    OrderStatus,
    OrderSide,
    OrderType,
    SymbolInfo,
    TimeInForce,
)


class BinanceLinearClient(ExchangeClient):
    """
    Binance linear market exchange API client implementation.

    This class implements the abstract ExchangeClient for the Binance exchange.
    """

    exchange_info: dict[str, Any] | None = None

    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        Initialize the Binance linear market client.

        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Whether to use the testnet API (default: False)
        """
        self.url = (
            "https://testnet.binancefuture.com"
            if testnet
            else "https://fapi.binance.com"
        )
        self.api_key = api_key
        self.api_secret = api_secret
        super().__init__()

    def _get_headers(self) -> dict[str, str]:
        """
        Generate authentication headers for Binance API requests.

        Binance requires:
        - X-MBX-APIKEY: API key
        """
        headers = {
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/json",
        }
        return headers

    def _gen_sign(self, params: dict[str, str]) -> str:
        sorted_params = sorted(params.items(), key=lambda p: p[0])
        payload = urllib.parse.urlencode(sorted_params)
        return hmac.new(
            self.api_secret.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()

    async def _request(
        self,
        method,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
        auth: bool = False,
    ) -> Any:
        self.logger.debug(f"Sending {method} request to {url}")

        # add timestamp if authenticated
        if auth:
            params = params if params is not None else {}
            params["timestamp"] = str(time.time_ns() // 1_000_000)
            params["recvWindow"] = "5000"  # default receive window

        # sort params by key
        sorted_params = (
            sorted(params.items(), key=lambda p: p[0]) if params is not None else None
        )

        # add signature if authenticated
        if auth:
            params = params if params is not None else {}
            params["signature"] = self._gen_sign(params=params)
            sorted_params = sorted(params.items(), key=lambda p: p[0])

        url = (
            url
            if sorted_params is None
            else url + f"?{urllib.parse.urlencode(sorted_params)}"
        )
        response = await self.client.request(
            method=method,
            url=url,
            headers=headers,
        )
        if not response.ok:
            raise BinanceError(response)

        try:
            resp_body = json.loads(response.body)
            self.logger.debug(
                f"Received ({response.status}) {method} response from {url}"
            )
            return resp_body
        except Exception:
            raise BinanceError(response)

    def exchange(self) -> Exchange:
        return Exchange.BINANCE_LINEAR

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
        try:
            if side == OrderSide.NONE:
                raise InvalidParameterError("Order side cannot be NONE")

            order_type = OrderType.MARKET if limit is None else OrderType.LIMIT

            data = {
                "symbol": str(symbol),
                "side": side.upper(),
                "type": order_type.upper(),
                "quantity": str(quantity),
                **kwargs,
            }

            if client_order_id is not None:
                data["newClientOrderId"] = client_order_id

            if limit is not None:
                data["price"] = str(limit)
                data["timeInForce"] = "GTX" if post_only else time_in_force.upper()

            headers = self._get_headers()

            body = await self._request(
                "POST",
                f"{self.url}/fapi/v1/order",
                headers,
                params=data,
                auth=True,
            )

            return OrderResponse(
                exchange=Exchange.BINANCE_LINEAR,
                order_id=body["orderId"],
                client_order_id=body["clientOrderId"],
                exchange_response=body,
            )
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    async def cancel_order(
        self,
        symbol: Symbol,
        order_id: str | None = None,
        client_order_id: str | None = None,
        **kwargs,
    ) -> OrderResponse:
        """
        Cancel an order.

        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT").
            order_id: Order ID from the exchange.
            client_order_id: Order ID provided by the client.

        Returns:
            OrderResponse: Details of the cancelled order.

        Raises:
            DeserializationError: Failed to deserialize parameters or response body.
            BinanceError: Failed operation with error from the exchange.
        """
        try:
            data = {"symbol": str(symbol), **kwargs}

            if order_id is not None:
                data["orderId"] = order_id
            elif client_order_id is not None:
                data["origClientOrderId"] = client_order_id
            else:
                raise InvalidParameterError(
                    "Neither order_id or client_order_id was provided."
                )

            headers = self._get_headers()

            body = await self._request(
                "DELETE", f"{self.url}/fapi/v1/order", headers, params=data, auth=True
            )

            return OrderResponse(
                exchange=Exchange.BINANCE_LINEAR,
                order_id=body["orderId"],
                client_order_id=body["clientOrderId"],
                exchange_response=body,
            )
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    async def get_positions(
        self, symbol: Symbol | None = None, **kwargs
    ) -> list[Position]:
        """
        Get current positions from Binance.

        Args:
            symbol: Optional trading pair symbol to filter positions

        Returns:
            list[Position]: List of position.
        """
        try:
            params = {**kwargs}

            if symbol:
                params["symbol"] = str(symbol)

            positions = await self._request(
                method="GET",
                url=f"{self.url}/fapi/v3/positionRisk",
                headers=self._get_headers(),
                params=params,
                auth=True,
            )

            return list(
                map(
                    lambda p: Position(
                        symbol=Symbol(p["symbol"]),
                        quantity=Decimal(p["positionAmt"]),
                        entry_price=Decimal(p["entryPrice"]),
                        updated_time=datetime.fromtimestamp(
                            int(p["updateTime"]) // 1000
                        ),
                        orig=p,
                    ),
                    positions,
                )
            )
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    async def get_wallet_balance(self, coin: str | None = None, **kwargs) -> Balance:
        """
        Get wallet balances from Binance linear market.

        Note:
            The only valid `coin` values here would be 'USDT', 'FDUSD', 'BFUSD' or 'USDC' as this client
            only handles interactions with the linear market. This function searches with
            `coin = "USDT"` set. Leaving coin set to None, is fine.

        Args:
            coin: Optional coin to filter balances (e.g., "USDC")

        Returns:
            WalletBalance with balance details
        """
        try:
            account = await self._request(
                method="GET",
                url=f"{self.url}/fapi/v3/account",
                headers=self._get_headers(),
                params=None,
                auth=True,
            )

            if coin is None:
                return Balance(
                    exchange=Exchange.BINANCE_LINEAR,
                    coin=None,
                    wallet_balance=Decimal(account["totalWalletBalance"]),
                    available_balance=Decimal(account["availableBalance"]),
                    initial_margin=Decimal(account["totalInitialMargin"]),
                    margin_balance=Decimal(account["totalMarginBalance"]),
                    maintenance_margin=Decimal(account["totalMaintMargin"]),
                    equity=Decimal(account["totalWalletBalance"])
                    + Decimal(account["totalUnrealizedProfit"]),
                    unrealised_pnl=Decimal(account["totalUnrealizedProfit"]),
                    orig=account,
                )
            else:
                assets = account["assets"]
                filtered = list(filter(lambda a: a["asset"] == coin, assets))
                if len(filtered) == 0:
                    raise InvalidParameterError(
                        f"Coin {coin} not found in account balances"
                    )
                asset = filtered[0]

                return Balance(
                    exchange=Exchange.BYBIT_LINEAR,
                    coin=asset["asset"],
                    wallet_balance=Decimal(asset["walletBalance"]),
                    available_balance=Decimal(asset["availableBalance"]),
                    margin_balance=Decimal(asset["marginBalance"]),
                    initial_margin=Decimal(asset["initialMargin"]),
                    maintenance_margin=Decimal(asset["maintMargin"]),
                    equity=Decimal(asset["walletBalance"])
                    + Decimal(asset["unrealizedProfit"]),
                    unrealised_pnl=Decimal(asset["unrealizedProfit"]),
                    orig=asset,
                )

        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    @override
    async def get_open_orders(
        self, symbol: Symbol | None = None, **kwargs
    ) -> list[OrderUpdate]:
        """
        Get open orders from Binance

        Args:
            symbol: Symbol name (optional, if not provided returns all symbols)

        Returns:
            Dict containing open orders data
        """
        try:
            params = {**kwargs}

            if symbol:
                params["symbol"] = str(symbol)

            orders = await self._request(
                method="GET",
                url=f"{self.url}/fapi/v1/openOrders",
                headers=self._get_headers(),
                params=params,
                auth=True,
            )

            updates = []

            for order in orders:
                tif = TimeInForce.from_str(order["timeInForce"])
                if tif is None:
                    tif = order["timeInForce"]

                status = OrderStatus.from_str(order["status"])
                if status is None:
                    raise DeserializationError(
                        f"Unrecognized status: {order['status']}"
                    )
                elif (
                    status == OrderStatus.CANCELLED
                    and Decimal(order["origQty"]) - Decimal(order["executedQty"]) != 0.0
                ):
                    status = OrderStatus.PARTIALLY_FILLED_CANCELLED

                order_type = OrderType.from_str(order["type"])
                if order_type is None:
                    order_type = order["type"]

                updates.append(
                    OrderUpdate(
                        symbol=order["symbol"],
                        order_type=order_type,
                        side=OrderSide.from_str(order["side"]),
                        time_in_force=tif,
                        order_id=order["orderId"],
                        order_time=datetime.fromtimestamp(
                            float(order["time"]) / 1000.0
                        ),
                        updated_time=datetime.fromtimestamp(
                            float(order["updateTime"]) / 1000.0
                        ),
                        size=Decimal(order["origQty"]),
                        filled_size=Decimal(order["executedQty"]),
                        remain_size=Decimal(order["origQty"])
                        - Decimal(order["executedQty"]),
                        price=Decimal(order["price"])
                        if status == OrderStatus.CREATED
                        else Decimal(order["avgPrice"]),
                        client_order_id=order["clientOrderId"],
                        status=status,
                        exchange=Exchange.BINANCE_LINEAR,
                        is_reduce_only=order["reduceOnly"],
                        is_hedge_mode=False,
                        orig=order,
                    )
                )

            return updates
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    async def get_orderbook_snapshot(
        self, symbol: Symbol, **kwargs
    ) -> OrderbookSnapshot:
        try:
            params = {"symbol": str(symbol), **kwargs}

            # default depth to 1000 if not specified
            if "depth" not in params:
                params["depth"] = 1000

            body = await self._request(
                method="GET",
                url=f"{self.url}/fapi/v1/depth",
                headers=self._get_headers(),
                params=params,
            )

            def into_level(data: tuple[float, float]):
                return Level(
                    price=Decimal(data[0]),
                    quantity=Decimal(data[1]),
                )

            bids = list(map(into_level, body["bids"]))
            asks = list(map(into_level, body["asks"]))

            return OrderbookSnapshot(
                symbol=symbol,
                last_update_time=body["T"],
                last_update_id=body["lastUpdateId"],
                bids=bids,
                asks=asks,
                exchange=Exchange.BINANCE_LINEAR,
                orig=body,
            )
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    async def get_symbol_info(self, symbol: Symbol, **kwargs) -> SymbolInfo:
        # function to find and transform symbol info from exchange info
        def find_symbol(exchange_info: dict[str, Any], symbol: Symbol) -> SymbolInfo:
            filtered = list(
                filter(lambda s: s["symbol"] == str(symbol), exchange_info["symbols"])
            )
            if len(filtered) == 0:
                raise InvalidParameterError(
                    f"Symbol {symbol} not found in exchangeInfo"
                )
            info = filtered[0]

            (
                tick_size,
                max_limit_qty,
                min_limit_qty,
                max_market_qty,
                min_market_qty,
                min_notional,
            ) = None, None, None, None, None, None
            for _filter in info["filters"]:
                if _filter["filterType"] == "PRICE_FILTER":
                    tick_size = Decimal(_filter["tickSize"])
                elif _filter["filterType"] == "LOT_SIZE":
                    min_limit_qty = Decimal(_filter["minQty"])
                    max_limit_qty = Decimal(_filter["maxQty"])
                elif _filter["filterType"] == "MARKET_LOT_SIZE":
                    min_market_qty = Decimal(_filter["minQty"])
                    max_market_qty = Decimal(_filter["maxQty"])
                elif _filter["filterType"] == "MIN_NOTIONAL":
                    min_notional = Decimal(_filter["notional"])

            if not tick_size:
                raise Exception("tick_size not found in exchangeInfo")
            if not max_limit_qty:
                raise Exception("max_limit_qty not found in exchangeInfo")
            if not min_limit_qty:
                raise Exception("min_limit_qty not found in exchangeInfo")
            if not max_market_qty:
                raise Exception("max_market_qty not found in exchangeInfo")
            if not min_market_qty:
                raise Exception("min_market_qty not found in exchangeInfo")
            if not min_notional:
                raise Exception("min_notional not found in exchangeInfo")

            return SymbolInfo(
                symbol=symbol,
                quantity_precision=info["quantityPrecision"],
                price_precision=info["pricePrecision"],
                exchange=Exchange.BINANCE_LINEAR,
                tick_size=tick_size,
                max_post_only_qty=max_limit_qty,
                max_limit_qty=max_limit_qty,
                min_limit_qty=min_limit_qty,
                max_market_qty=max_market_qty,
                min_market_qty=min_market_qty,
                min_notional=min_notional,
                max_notional=Decimal(str(sys.float_info.max)),
                quanto_multiplier=None,
            )

        # cache the results for 10 minutes
        MILLIS = 1000
        MINUTE = 60 * MILLIS
        timestamp = time.time_ns() // 1_000_000
        if self.exchange_info is not None and (
            timestamp - self.exchange_info["serverTime"] < 10 * MINUTE
        ):
            return find_symbol(self.exchange_info, symbol)

        try:
            body = await self._request(
                method="GET",
                url=f"{self.url}/fapi/v1/exchangeInfo",
                headers=self._get_headers(),
                params=None,
            )
            self.exchange_info = body  # set local cache
            return find_symbol(body, symbol)
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    async def get_order_details(
        self,
        symbol: Symbol | None = None,
        order_id: str | None = None,
        client_order_id: str | None = None,
        **kwargs,
    ) -> OrderUpdate | None:
        try:
            params = {**kwargs}

            if symbol is not None:
                params["symbol"] = str(symbol)
            else:
                raise InvalidParameterError("symbol is required")

            if order_id is not None:
                params["orderId"] = order_id
            elif client_order_id is not None:
                params["origClientOrderId"] = client_order_id
            else:
                raise InvalidParameterError(
                    "Neither order_id or client_order_id was provided."
                )

            order = await self._request(
                method="GET",
                url=f"{self.url}/fapi/v1/order",
                headers=self._get_headers(),
                params=params,
                auth=True,
            )

            tif = TimeInForce.from_str(order["timeInForce"])
            if tif is None:
                tif = order["timeInForce"]

            status = OrderStatus.from_str(order["status"])
            if status is None:
                raise DeserializationError(f"Unrecognized status: {order['status']}")
            elif (
                status == OrderStatus.CANCELLED
                and Decimal(order["origQty"]) - Decimal(order["executedQty"]) != 0.0
            ):
                status = OrderStatus.PARTIALLY_FILLED_CANCELLED

            order_type = OrderType.from_str(order["type"])
            if order_type is None:
                order_type = order["type"]

            return OrderUpdate(
                symbol=order["symbol"],
                order_type=order_type,
                side=OrderSide.from_str(order["side"]),
                time_in_force=tif,
                order_id=order["orderId"],
                order_time=datetime.fromtimestamp(float(order["time"]) / 1000.0),
                updated_time=datetime.fromtimestamp(
                    float(order["updateTime"]) / 1000.0
                ),
                size=Decimal(order["origQty"]),
                filled_size=Decimal(order["executedQty"]),
                remain_size=Decimal(order["origQty"]) - Decimal(order["executedQty"]),
                price=Decimal(order["price"])
                if status == OrderStatus.CREATED
                else Decimal(order["avgPrice"]),
                client_order_id=order["clientOrderId"],
                status=status,
                exchange=Exchange.BINANCE_LINEAR,
                is_reduce_only=order["reduceOnly"],
                is_hedge_mode=False,
                orig=order,
            )
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")
        except BinanceError as e:
            if e.code is not None and e.code == -2013:  # Order does not exist
                return None
            raise e

    async def get_order_details_from_history(
        self,
        symbol: Symbol | None = None,
        order_id: str | None = None,
        client_order_id: str | None = None,
        **kwargs,
    ) -> OrderUpdate | None:
        order = await self.get_order_details(
            symbol=symbol, order_id=order_id, client_order_id=client_order_id
        )
        if order is None:
            return None

        match order.status:
            case OrderStatus.CREATED | OrderStatus.PARTIALLY_FILLED:
                return None
            case _:
                return order
