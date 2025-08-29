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
from cybotrade.encoder import JSONEncoder
from cybotrade.exceptions import DeserializationError, InvalidParameterError
from cybotrade.bybit.exceptions import BybitError
from cybotrade.io.exchange import ExchangeClient
from cybotrade.utils import extract_precision
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


class BybitLinearClient(ExchangeClient):
    """
    Bybit linear market exchange API client implementation.

    This class implements the abstract ExchangeClient for the Bybit exchange.
    """

    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        Initialize the Bybit linear market client.

        Args:
            api_key: Bybit API key
            api_secret: Bybit API secret
            testnet: Whether to use the testnet API (default: False)
        """
        self.url = (
            "https://api-testnet.bybit.com" if testnet else "https://api.bybit.com"
        )
        self.api_key = api_key
        self.api_secret = api_secret
        super().__init__()

    def _get_headers(self, **kwargs) -> dict[str, str]:
        """
        Generate authentication headers for Bybit API requests.

        Bybit requires:
        - X-BAPI-API-KEY: API key
        - X-BAPI-TIMESTAMP: Current timestamp in milliseconds
        - X-BAPI-SIGN: HMAC SHA256 signature
        - X-BAPI-RECV-WINDOW: Receive window in milliseconds (optional)

        Args:
            **kwargs: Additional parameters needed for authentication
                - params: Query parameters for GET requests
                - data: Request body for POST requests

        Returns:
            Sorted dict containing headers required for authentication
        """
        recv_window = 5000

        params_str = ""
        if "params" in kwargs and kwargs["params"]:
            params_str = urllib.parse.urlencode(kwargs["params"])

        data_str = ""
        if "data" in kwargs and kwargs["data"]:
            data_str = json.dumps(
                kwargs["data"], separators=(",", ":"), sort_keys=True, cls=JSONEncoder
            )

        timestamp = time.time_ns() // 1_000_000
        sign_str = f"{timestamp}{self.api_key}{recv_window}{params_str}{data_str}"
        signature = hmac.new(
            self.api_secret.encode(), sign_str.encode(), hashlib.sha256
        ).hexdigest()

        headers = {
            "X-BAPI-API-KEY": self.api_key,
            "X-BAPI-TIMESTAMP": str(timestamp),
            "X-BAPI-SIGN": signature,
            "X-BAPI-RECV-WINDOW": str(recv_window),
            "Content-Type": "application/json",
        }
        return headers

    def exchange(self) -> Exchange:
        return Exchange.BYBIT_LINEAR

    async def _request(
        self,
        method,
        url: str,
        headers: dict[str, str] | None = None,
        body: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        self.logger.debug(f"Sending {method} request to {url}")
        req_body = (
            None
            if body is None
            else json.dumps(
                dict(sorted(body.items())),
                separators=(",", ":"),
                sort_keys=True,
                cls=JSONEncoder,
            )
        )
        response = await self.client.request(
            method=method,
            url=url,
            headers=headers,
            body=req_body,
        )
        if not response.ok:
            raise BybitError(response)

        try:
            resp_body = json.loads(response.body)
            if resp_body["retCode"] != 0:
                raise BybitError(response)
            self.logger.debug(
                f"Received ({response.status}) {method} response from {url}"
            )
            return resp_body
        except Exception:
            raise BybitError(response)

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
            order_type = OrderType.MARKET if limit is None else OrderType.LIMIT

            data = {
                "category": "linear",
                "symbol": str(symbol),
                "side": "Buy" if side == OrderSide.BUY else "Sell",
                "orderType": "Market" if order_type == OrderType.MARKET else "Limit",
                "qty": str(quantity),
                "timeInForce": "PostOnly" if post_only else time_in_force.upper(),
                **kwargs,
            }

            if limit is not None:
                data["price"] = str(limit)

            if client_order_id is not None:
                data["orderLinkId"] = client_order_id

            headers = self._get_headers(data=data)

            body = await self._request(
                "POST",
                f"{self.url}/v5/order/create",
                headers,
                body=data,
            )

            return OrderResponse(
                exchange=Exchange.BYBIT_LINEAR,
                order_id=body["result"]["orderId"],
                client_order_id=body["result"]["orderLinkId"],
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
            BybitError: Failed operation with error from the exchange.
        """
        try:
            data = {"category": "linear", "symbol": str(symbol), **kwargs}

            if order_id is not None:
                data["orderId"] = order_id
            elif client_order_id is not None:
                data["orderLinkId"] = client_order_id
            else:
                raise InvalidParameterError(
                    "Neither order_id or client_order_id was provided."
                )

            headers = self._get_headers(data=data)

            body = await self._request(
                "POST",
                f"{self.url}/v5/order/cancel",
                headers,
                body=data,
            )

            return OrderResponse(
                exchange=Exchange.BYBIT_LINEAR,
                order_id=body["result"]["orderId"],
                client_order_id=body["result"]["orderLinkId"],
                exchange_response=body,
            )
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    async def get_positions(
        self, symbol: Symbol | None = None, **kwargs
    ) -> list[Position]:
        """
        Get current positions from Bybit.

        Args:
            symbol: Optional trading pair symbol to filter positions

        Returns:
            list[Position]: List of position.
        """
        try:
            params = {"category": "linear", **kwargs}

            if symbol:
                params["symbol"] = str(symbol)
            else:
                params["settleCoin"] = "USDT"

            headers = self._get_headers(params=params)

            url = f"{self.url}/v5/position/list?" + urllib.parse.urlencode(params)
            body = await self._request("GET", url, headers, None)

            position_list = body["result"]["list"]
            position = []

            for pos in position_list:
                sym = Symbol(pos["symbol"])
                match pos["side"]:
                    case "Buy":
                        position.append(
                            Position(
                                symbol=sym,
                                quantity=Decimal(pos["size"]),
                                entry_price=Decimal(pos["avgPrice"]),
                                updated_time=datetime.fromtimestamp(
                                    int(pos["updatedTime"]) // 1000
                                ),
                                orig=pos,
                            )
                        )
                    case "Sell":
                        position.append(
                            Position(
                                symbol=sym,
                                quantity=Decimal(f"-{pos['size']}"),
                                entry_price=Decimal(pos["avgPrice"]),
                                updated_time=datetime.fromtimestamp(
                                    int(pos["updatedTime"]) // 1000
                                ),
                                orig=pos,
                            )
                        )
                    case "":
                        position.append(
                            Position(
                                symbol=sym,
                                quantity=Decimal("0"),
                                entry_price=Decimal("0"),
                                updated_time=datetime.fromtimestamp(
                                    int(pos["updatedTime"]) // 1000
                                ),
                                orig=pos,
                            )
                        )
                    case _:
                        raise DeserializationError(
                            "Failed to load json: Unrecognized order side in returned data."
                        )

            return position
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    async def get_wallet_balance(self, coin: str | None = None, **kwargs) -> Balance:
        """
        Get wallet balances from Bybit linear market.

        Note:
            The only valid `coin` values here would be 'USDT' or 'USDC' as this client
            only handles interactions with the linear market. This function searches with
            `coin = "USDT"` set. Leaving coin set to None, is fine.

        Args:
            coin: Optional coin to filter balances (e.g., "USDC")

        Returns:
            WalletBalance with balance details
        """
        try:
            params = {"accountType": "UNIFIED", **kwargs}
            url = f"{self.url}/v5/account/wallet-balance?" + urllib.parse.urlencode(
                params
            )
            body = await self._request(
                method="GET",
                url=url,
                headers=self._get_headers(params=params),
                body=None,
            )
            account = body["result"]["list"][0]

            if coin is None:
                return Balance(
                    exchange=Exchange.BYBIT_LINEAR,
                    coin=None,
                    wallet_balance=Decimal(account["totalWalletBalance"]),
                    available_balance=Decimal(account["totalAvailableBalance"]),
                    initial_margin=Decimal(account["totalInitialMargin"]),
                    margin_balance=Decimal(account["totalMarginBalance"]),
                    maintenance_margin=Decimal(account["totalMaintenanceMargin"]),
                    equity=Decimal(account["totalEquity"]),
                    unrealised_pnl=Decimal(account["totalPerpUPL"]),
                    orig=account,
                )
            else:
                coins = account["coin"]
                filtered = list(filter(lambda c: c["coin"] == coin, coins))
                if len(filtered) == 0:
                    raise InvalidParameterError(
                        f"Coin {coin} is not found in the account"
                    )
                _coin = filtered[0]

                return Balance(
                    exchange=Exchange.BYBIT_LINEAR,
                    coin=_coin["coin"],
                    wallet_balance=Decimal(_coin["walletBalance"]),
                    available_balance=Decimal(_coin["walletBalance"])
                    + Decimal(_coin["unrealisedPnl"])
                    - Decimal(_coin["totalPositionIM"]),
                    margin_balance=Decimal(_coin["walletBalance"])
                    + Decimal(_coin["unrealisedPnl"]),
                    initial_margin=Decimal(_coin["totalPositionIM"]),
                    maintenance_margin=Decimal(_coin["totalPositionMM"]),
                    equity=Decimal(_coin["equity"]),
                    unrealised_pnl=Decimal(_coin["unrealisedPnl"]),
                    orig=_coin,
                )
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    @override
    async def get_open_orders(
        self, symbol: Symbol | None = None, **kwargs
    ) -> list[OrderUpdate]:
        """
        Get open orders from Bybit

        Args:
            symbol: Symbol name (optional, if not provided returns all symbols)

        Returns:
            Dict containing open orders data
        """
        try:
            params = {"category": "linear", **kwargs}

            if symbol:
                params["symbol"] = str(symbol)

            headers = self._get_headers(params=params)
            url = f"{self.url}/v5/order/realtime?" + urllib.parse.urlencode(params)
            body = await self._request("GET", url, headers, None)

            orders = body["result"]["list"]
            resp = []

            for order in orders:
                tif = TimeInForce.from_str(tif=order["timeInForce"])
                status = OrderStatus.from_str(order["orderStatus"])
                if status is None:
                    raise DeserializationError(
                        f"Unrecognized status: {order['orderStatus']}"
                    )
                elif (
                    status == OrderStatus.CANCELLED
                    and Decimal(order["qty"]) - Decimal(order["cumExecQty"]) != 0.0
                ):
                    status = OrderStatus.PARTIALLY_FILLED_CANCELLED
                resp.append(
                    OrderUpdate(
                        symbol=Symbol(order["symbol"]),
                        order_type=OrderType.MARKET
                        if order["orderType"] == "Market"
                        else OrderType.LIMIT,
                        side=OrderSide.BUY
                        if order["side"] == "Buy"
                        else OrderSide.SELL,
                        time_in_force=TimeInForce.GTC if tif is None else tif,
                        order_id=order["orderId"],
                        order_time=datetime.fromtimestamp(
                            float(order["createdTime"]) / 1000.0
                        ),
                        updated_time=datetime.fromtimestamp(
                            float(order["updatedTime"]) / 1000.0
                        ),
                        size=Decimal(order["qty"]),
                        filled_size=Decimal(order["cumExecQty"]),
                        remain_size=Decimal(order["qty"])
                        - Decimal(order["cumExecQty"]),
                        price=Decimal(order["price"]),
                        client_order_id=order["orderLinkId"],
                        status=status,
                        exchange=Exchange.BYBIT_LINEAR,
                        is_reduce_only=False,
                        is_hedge_mode=False,
                        orig=order,
                    )
                )
            return resp
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    async def get_orderbook_snapshot(
        self, symbol: Symbol, **kwargs
    ) -> OrderbookSnapshot:
        try:
            params = {"category": "linear", "symbol": str(symbol), **kwargs}

            headers = self._get_headers(params=params)
            url = f"{self.url}/v5/market/orderbook?" + urllib.parse.urlencode(params)
            body = await self._request("GET", url, headers, None)

            def into_level(data: tuple[float, float]):
                return Level(
                    price=Decimal(data[0]),
                    quantity=Decimal(data[1]),
                )

            bids = list(map(into_level, body["result"]["b"]))
            asks = list(map(into_level, body["result"]["a"]))

            return OrderbookSnapshot(
                symbol=symbol,
                last_update_time=body["result"]["ts"],
                last_update_id=body["result"]["u"],
                bids=bids,
                asks=asks,
                exchange=Exchange.BYBIT_LINEAR,
                orig=body["result"],
            )
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    async def get_symbol_info(self, symbol, **kwargs) -> SymbolInfo:
        """"""
        try:
            params = {"category": "linear", "symbol": str(symbol), **kwargs}

            headers = self._get_headers(params=params)
            url = f"{self.url}/v5/market/instruments-info?" + urllib.parse.urlencode(
                params
            )
            body = await self._request("GET", url, headers, None)

            response = body["result"]["list"][0]

            min_order_qty = Decimal(response["lotSizeFilter"]["minOrderQty"])
            tick_size = Decimal(response["priceFilter"]["tickSize"])

            return SymbolInfo(
                symbol=symbol,
                quantity_precision=extract_precision(min_order_qty),
                price_precision=extract_precision(tick_size),
                exchange=Exchange.BYBIT_LINEAR,
                tick_size=tick_size,
                max_post_only_qty=Decimal(
                    response["lotSizeFilter"]["postOnlyMaxOrderQty"]
                ),
                max_limit_qty=Decimal(response["lotSizeFilter"]["maxOrderQty"]),
                min_limit_qty=min_order_qty,
                max_market_qty=Decimal(response["lotSizeFilter"]["maxMktOrderQty"]),
                min_market_qty=None,
                min_notional=Decimal(response["lotSizeFilter"]["minNotionalValue"]),
                max_notional=Decimal(str(sys.float_info.max)),
                quanto_multiplier=None,
            )
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    async def get_order_details(
        self,
        symbol: Symbol | None = None,
        order_id: str | None = None,
        client_order_id: str | None = None,
        **kwargs,
    ) -> OrderUpdate | None:
        """
        Get a id-specific order from the exchange's order realtime.
        The intended use case of this function is to be able to validate/verify an order's state
        on the exchange on demand.

        Note: if both parameters are provided, the order_id will be prioritized.

        Args:
            order_id: Optional id from exchange
            client_order_id: Optional user-set id

        Returns:
            List of Order dataclasses
        """
        try:
            params = {"category": "linear", **kwargs}

            if symbol is not None:
                params["symbol"] = str(symbol)
            else:
                raise InvalidParameterError("symbol is required")

            if order_id is not None:
                params["orderId"] = order_id
            elif client_order_id is not None:
                params["orderLinkId"] = client_order_id
            else:
                raise InvalidParameterError(
                    "Neither order_id or client_order_id was provided."
                )

            headers = self._get_headers(params=params)
            url = f"{self.url}/v5/order/realtime?" + urllib.parse.urlencode(params)
            body = await self._request("GET", url, headers, None)

            orders = body["result"]["list"]

            if len(orders) == 0:
                return None
            else:
                tif = TimeInForce.from_str(tif=orders[0]["timeInForce"])
                status = OrderStatus.from_str(orders[0]["orderStatus"])
                if status is None:
                    raise DeserializationError(
                        f"Unrecognized status: {orders[0]['orderStatus']}"
                    )
                elif (
                    status == OrderStatus.CANCELLED
                    and Decimal(orders[0]["qty"]) - Decimal(orders[0]["cumExecQty"])
                    != 0.0
                ):
                    status = OrderStatus.PARTIALLY_FILLED_CANCELLED
                return OrderUpdate(
                    symbol=Symbol(orders[0]["symbol"]),
                    order_type=OrderType.MARKET
                    if orders[0]["orderType"] == "Market"
                    else OrderType.LIMIT,
                    side=OrderSide.BUY
                    if orders[0]["side"] == "Buy"
                    else OrderSide.SELL,
                    time_in_force=TimeInForce.GTC if tif is None else tif,
                    order_id=orders[0]["orderId"],
                    order_time=datetime.fromtimestamp(
                        float(orders[0]["createdTime"]) / 1000.0
                    ),
                    updated_time=datetime.fromtimestamp(
                        float(orders[0]["updatedTime"]) / 1000.0
                    ),
                    size=Decimal(orders[0]["qty"]),
                    filled_size=Decimal(orders[0]["cumExecQty"]),
                    remain_size=Decimal(orders[0]["qty"])
                    - Decimal(orders[0]["cumExecQty"]),
                    price=Decimal(orders[0]["price"]),
                    client_order_id=orders[0]["orderLinkId"],
                    status=status,
                    exchange=Exchange.BYBIT_LINEAR,
                    is_reduce_only=False,
                    is_hedge_mode=False,
                    orig=orders[0],
                )
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

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
        try:
            params = {"category": "linear", **kwargs}

            if order_id is not None:
                params["orderId"] = order_id
            elif client_order_id is not None:
                params["orderLinkId"] = client_order_id
            else:
                raise InvalidParameterError(
                    "Neither order_id or client_order_id was provided."
                )

            headers = self._get_headers(params=params)

            url = f"{self.url}/v5/order/history?" + urllib.parse.urlencode(params)

            body = await self._request("GET", url, headers, None)

            orders = body["result"]["list"]

            if len(orders) == 0:
                return None
            else:
                tif = TimeInForce.from_str(tif=orders[0]["timeInForce"])
                status = OrderStatus.from_str(orders[0]["orderStatus"])
                if (
                    status == OrderStatus.CANCELLED
                    and Decimal(orders[0]["qty"]) - Decimal(orders[0]["cumExecQty"])
                    != 0.0
                ):
                    status = OrderStatus.PARTIALLY_FILLED_CANCELLED
                return OrderUpdate(
                    symbol=Symbol(orders[0]["symbol"]),
                    order_type=OrderType.MARKET
                    if orders[0]["orderType"] == "Market"
                    else OrderType.LIMIT,
                    side=OrderSide.BUY
                    if orders[0]["side"] == "Buy"
                    else OrderSide.SELL,
                    time_in_force=TimeInForce.GTC if tif is None else tif,
                    order_id=orders[0]["orderId"],
                    order_time=datetime.fromtimestamp(
                        float(orders[0]["createdTime"]) / 1000.0
                    ),
                    updated_time=datetime.fromtimestamp(
                        float(orders[0]["updatedTime"]) / 1000.0
                    ),
                    size=Decimal(orders[0]["qty"]),
                    filled_size=Decimal(orders[0]["cumExecQty"]),
                    remain_size=Decimal(orders[0]["qty"])
                    - Decimal(orders[0]["cumExecQty"]),
                    price=Decimal(orders[0]["price"]),
                    client_order_id=orders[0]["orderLinkId"],
                    status=status,
                    exchange=Exchange.BYBIT_LINEAR,
                    is_reduce_only=False,
                    is_hedge_mode=False,
                    orig=orders[0],
                )
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")
