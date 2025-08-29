import sys
import time
import base64
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
from cybotrade.kucoin.exceptions import KucoinError
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


class KucoinLinearClient(ExchangeClient):
    """
    Kucoin linear market exchange API client implementation.

    This class implements the abstract ExchangeClient for the Kucoin exchange.
    """

    symbol_infos: dict[Symbol, SymbolInfo] | None = None

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        api_passphrase: str,
        sandbox: bool = False,
        api_key_version: int = 3,
    ):
        """
        Initialize the Kucoin linear market client.

        Args:
            api_key: Kucoin API key
            api_secret: Kucoin API secret
        """
        self.url = "https://api-futures.kucoin.com"
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.sandbox = sandbox
        self.api_key_version = api_key_version
        super().__init__()

    def _get_headers(self, method: str, path: str, **kwargs) -> dict[str, str]:
        """
        Generate authentication headers for Kucoin API requests.

        Kucoin requires:
        - KC-API-KEY: API key
        - KC-API-SIGN: HMAC SHA256 signature
        - KC-API-TIMESTAMP: Current timestamp in milliseconds
        - KC-API-PASSPHRASE: The passphrase you specified when creating the API key.
        - KC-API-KEY-VERSION: API key version

        Args:
            method: HTTP method (e.g. GET, POST)
            path: Request path (e.g. /api/v1/position)
            **kwargs: Additional parameters needed for authentication
                - params: Query parameters for GET requests
                - data: Request body for POST requests

        Returns:
            Sorted dict containing headers required for authentication
        """
        params_str = ""
        if "params" in kwargs and kwargs["params"]:
            params_str = f"?{urllib.parse.urlencode(kwargs['params'])}"

        data_str = ""
        if "data" in kwargs and kwargs["data"]:
            data_str = json.dumps(
                kwargs["data"], separators=(",", ":"), sort_keys=True, cls=JSONEncoder
            )

        timestamp = time.time_ns() // 1_000_000
        sign_str = f"{timestamp}{method}{path}{params_str}{data_str}"
        signature = base64.b64encode(
            hmac.new(
                self.api_secret.encode(), sign_str.encode(), hashlib.sha256
            ).digest()
        )
        passphrase = base64.b64encode(
            hmac.new(
                self.api_secret.encode(), self.api_passphrase.encode(), hashlib.sha256
            ).digest()
        )

        headers = {
            "KC-API-SIGN": signature.decode(),
            "KC-API-TIMESTAMP": str(timestamp),
            "KC-API-KEY": self.api_key,
            "KC-API-PASSPHRASE": passphrase.decode(),
            "KC-API-KEY-VERSION": str(self.api_key_version),
            "Content-Type": "application/json",
        }
        return headers

    def exchange(self) -> Exchange:
        return Exchange.KUCOIN_LINEAR

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
            raise KucoinError(response)

        try:
            resp_body = json.loads(response.body)
            if resp_body["code"] != "200000":
                raise KucoinError(response)
            self.logger.debug(
                f"Received ({response.status}) {method} response from {url}"
            )
            return resp_body
        except Exception:
            raise KucoinError(response)

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

            # clientOid is mandatory
            if client_order_id is None:
                raise InvalidParameterError("client_order_id must be provided")

            data = {
                "symbol": str(symbol),
                "side": "buy" if side == OrderSide.BUY else "sell",
                "qty": str(quantity),
                "type": "market" if order_type == OrderType.MARKET else "limit",
                "timeInForce": time_in_force.upper(),
                "postOnly": post_only,
                "clientOid": client_order_id,
                "marginMode": "CROSS",  # will be overidden by kwargs if specified
                "leverage": 1,  # default leverage to 1
                **kwargs,
            }

            if limit is not None:
                data["price"] = str(limit)

            path = "/api/v1/orders/test" if self.sandbox else "/api/v1/orders"
            headers = self._get_headers(method="POST", path=path, data=data)

            body = await self._request(
                "POST",
                f"{self.url}{path}",
                headers,
                body=data,
            )

            return OrderResponse(
                exchange=Exchange.KUCOIN_LINEAR,
                order_id=body["data"]["orderId"],
                client_order_id=body["data"]["clientOid"],
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
            KucoinError: Failed operation with error from the exchange.
        """
        try:
            params = {"symbol": str(symbol), **kwargs}

            if order_id is not None:
                path = f"/api/v1/orders/{order_id}"
            elif client_order_id is not None:
                path = f"/api/v1/orders/client-order/{client_order_id}"
            else:
                raise InvalidParameterError(
                    "Neither order_id or client_order_id was provided."
                )

            headers = self._get_headers(method="DELETE", path=path, params=params)

            url = f"{self.url}{path}"
            if len(params) > 0:
                url += f"?{urllib.parse.urlencode(params)}"

            body = await self._request("DELETE", url, headers)

            if order_id is not None:
                return OrderResponse(
                    exchange=Exchange.KUCOIN_LINEAR,
                    order_id=body["data"]["cancelledOrderIds"][0],
                    client_order_id="",
                    exchange_response=body,
                )
            else:
                return OrderResponse(
                    exchange=Exchange.KUCOIN_LINEAR,
                    order_id="",
                    client_order_id=body["data"]["clientOid"],
                    exchange_response=body,
                )
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    async def get_positions(
        self, symbol: Symbol | None = None, **kwargs
    ) -> list[Position]:
        """
        Get current positions from Kucoin.

        Args:
            symbol: Optional trading pair symbol to filter positions

        Returns:
            list[Position]: List of position.
        """
        try:
            if self.symbol_infos is None:
                self.symbol_infos = await self._fetch_symbol_infos()

            params = {**kwargs}

            if symbol:
                params["symbol"] = str(symbol)
                path = "/api/v1/position"  # position details
            else:
                path = "/api/v1/positions"  # position list

            headers = self._get_headers(method="GET", path=path, params=params)

            url = f"{self.url}{path}"
            if len(params) > 0:
                url += f"?{urllib.parse.urlencode(params)}"

            body = await self._request("GET", url, headers, None)

            def parse_pos(pos: Any):
                symbol = Symbol(pos["symbol"])

                # find symbol info
                if self.symbol_infos is None:
                    raise Exception(
                        "Symbol infos not loaded. Call _fetch_symbol_infos first."
                    )
                if symbol not in self.symbol_infos:
                    raise Exception(f"Symbol {symbol} not found in symbol infos.")
                multiplier = self.symbol_infos[symbol].quanto_multiplier
                if multiplier is None:
                    raise Exception(
                        f"Symbol {symbol} does not have a quanto multiplier."
                    )

                return Position(
                    symbol=symbol,
                    quantity=Decimal(str(pos["currentQty"])) * multiplier,
                    entry_price=Decimal(str(pos["avgEntryPrice"])),
                    updated_time=datetime.fromtimestamp(
                        int(pos["currentTimestamp"]) // 1000
                    ),
                    orig=pos,
                )

            if symbol:
                return [parse_pos(body["data"])]
            else:
                return list(map(parse_pos, body["data"]))
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    async def get_wallet_balance(self, coin: str | None = None, **kwargs) -> Balance:
        """
        Get wallet balances from Kucoin linear market.

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
            params = {"currency": coin if coin is not None else "USDT", **kwargs}

            path = "/api/v1/account-overview"
            url = f"{self.url}{path}?" + urllib.parse.urlencode(params)

            body = await self._request(
                method="GET",
                url=url,
                headers=self._get_headers(method="GET", path=path, params=params),
                body=None,
            )
            account = body["data"]

            margin_balance = Decimal(str(account["marginBalance"]))
            available_balance = Decimal(str(account["availableBalance"]))

            return Balance(
                exchange=Exchange.KUCOIN_LINEAR,
                coin=account["currency"],
                wallet_balance=margin_balance,
                available_balance=available_balance,
                initial_margin=None,
                margin_balance=margin_balance,
                maintenance_margin=None,
                equity=Decimal(str(account["accountEquity"])),
                unrealised_pnl=Decimal(str(account["unrealisedPNL"])),
                orig=account,
            )
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    @override
    async def get_open_orders(
        self, symbol: Symbol | None = None, **kwargs
    ) -> list[OrderUpdate]:
        """
        Get open orders from Kucoin

        Args:
            symbol: Symbol name (optional, if not provided returns all symbols)

        Returns:
            Dict containing open orders data
        """
        try:
            if self.symbol_infos is None:
                self.symbol_infos = await self._fetch_symbol_infos()

            params = {"status": "active", "pageSize": 1000, **kwargs}

            if symbol:
                params["symbol"] = str(symbol)

            path = "/api/v1/orders"
            headers = self._get_headers(method="GET", path=path, params=params)
            url = f"{self.url}{path}?" + urllib.parse.urlencode(params)
            body = await self._request("GET", url, headers, None)

            return list(map(self._parse_order, body["data"]["items"]))
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    async def get_orderbook_snapshot(
        self, symbol: Symbol, **kwargs
    ) -> OrderbookSnapshot:
        try:
            if self.symbol_infos is None:
                self.symbol_infos = await self._fetch_symbol_infos()

            if symbol not in self.symbol_infos:
                raise Exception(f"Symbol {symbol} not found in symbol infos.")
            multiplier = self.symbol_infos[symbol].quanto_multiplier
            if multiplier is None:
                raise Exception(f"Symbol {symbol} does not have a quanto multiplier.")

            params = {"symbol": str(symbol), **kwargs}

            path = "/api/v1/level2/snapshot"
            headers = self._get_headers(method="GET", path=path, params=params)
            url = f"{self.url}{path}?" + urllib.parse.urlencode(params)
            body = await self._request("GET", url, headers, None)

            def into_level(data: tuple[float, int]):
                return Level(
                    price=Decimal(str(data[0])),
                    quantity=data[1] * multiplier,
                )

            bids = list(map(into_level, body["data"]["bids"]))
            asks = list(map(into_level, body["data"]["asks"]))

            return OrderbookSnapshot(
                symbol=symbol,
                last_update_time=datetime.fromtimestamp(
                    body["data"]["ts"] / 1_000_000_000
                ),
                last_update_id=body["data"]["sequence"],
                bids=bids,
                asks=asks,
                exchange=Exchange.KUCOIN_LINEAR,
                orig=body["data"],
            )
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    async def get_symbol_info(self, symbol, **kwargs) -> SymbolInfo:
        """"""
        try:
            path = f"/api/v1/contracts/{symbol}"
            headers = self._get_headers(method="GET", path=path)
            url = f"{self.url}{path}"
            body = await self._request("GET", url, headers, None)

            response = body["data"]

            multiplier = Decimal(str(response["multiplier"]))
            tick_size = Decimal(str(response["tickSize"]))
            min_qty, max_qty = (
                Decimal(str(response["lotSize"])) * multiplier,
                Decimal(str(response["maxOrderQty"])),
            )

            return SymbolInfo(
                symbol=symbol,
                quantity_precision=extract_precision(multiplier),
                price_precision=extract_precision(tick_size),
                exchange=Exchange.KUCOIN_LINEAR,
                tick_size=tick_size,
                max_post_only_qty=max_qty,
                max_limit_qty=max_qty,
                min_limit_qty=min_qty,
                max_market_qty=max_qty,
                min_market_qty=min_qty,
                min_notional=Decimal("0"),
                max_notional=Decimal(str(sys.float_info.max)),
                quanto_multiplier=multiplier,
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
            OrderUpdate: Details of the order, or None if not found.
        """
        try:
            if self.symbol_infos is None:
                self.symbol_infos = await self._fetch_symbol_infos()

            params = {}

            path = "/api/v1/orders"

            if order_id is not None:
                path = f"{path}/{order_id}"
            elif client_order_id is not None:
                path = f"{path}/byClientOid"
                params["clientOid"] = client_order_id
            else:
                raise InvalidParameterError(
                    "Neither order_id or client_order_id was provided."
                )

            headers = self._get_headers(method="GET", path=path, params=params)
            url = f"{self.url}{path}"
            if len(params) > 0:
                url += f"?{urllib.parse.urlencode(params)}"
            body = await self._request("GET", url, headers, None)

            return self._parse_order(body["data"])
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")
        except KucoinError as e:
            if "orderNotExist" in e.message:  # order does not exist
                return None
            else:
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

    def _parse_order(self, order: Any) -> OrderUpdate:
        symbol = Symbol(order["symbol"])

        # find symbol info
        if self.symbol_infos is None:
            raise Exception("Symbol infos not loaded. Call _fetch_symbol_infos first.")
        if symbol not in self.symbol_infos:
            raise Exception(f"Symbol {symbol} not found in symbol infos.")
        multiplier = self.symbol_infos[symbol].quanto_multiplier
        if multiplier is None:
            raise Exception(f"Symbol {symbol} does not have a quanto multiplier.")

        # determine order status
        ostatus = order["status"]
        if ostatus == "open":
            status = OrderStatus.CREATED
        elif ostatus == "done" and order["dealSize"] == 0:
            status = OrderStatus.CANCELLED
        elif ostatus == "done" and order["size"] != order["dealSize"]:
            status = OrderStatus.PARTIALLY_FILLED_CANCELLED
        elif ostatus == "done" and order["size"] == order["dealSize"]:
            status = OrderStatus.FILLED
        else:
            raise DeserializationError(f"Unrecognized status: {ostatus}")

        order_type = OrderType.from_str(order["type"])
        if order_type is None:
            raise DeserializationError(f"Unrecognized order type: {order_type}")

        order_side = OrderSide.from_str(order["side"])
        if order_side is None:
            raise DeserializationError(f"Unrecognized order side: {order_side}")

        tif = TimeInForce.from_str(tif=order["timeInForce"])
        if tif is None:
            raise DeserializationError(f"Unrecognized time in force: {tif}")

        size = Decimal(str(order["size"])) * multiplier
        filled_size = Decimal(str(order["dealSize"])) * multiplier

        return OrderUpdate(
            symbol=symbol,
            order_type=order_type,
            side=order_side,
            time_in_force=tif,
            order_id=order["id"],
            order_time=datetime.fromtimestamp(float(order["createdAt"]) / 1000.0),
            updated_time=datetime.fromtimestamp(float(order["updatedAt"]) / 1000.0),
            size=size,
            filled_size=filled_size,
            remain_size=size - filled_size,
            price=Decimal(str(order["price"])),
            client_order_id=order["clientOid"],
            status=status,
            exchange=Exchange.KUCOIN_LINEAR,
            is_reduce_only=order["reduceOnly"],
            is_hedge_mode=False,
            orig=order,
        )

    async def get_bullet_public(self) -> dict[str, Any]:
        try:
            path = "/api/v1/bullet-public"
            headers = self._get_headers(method="POST", path=path)
            url = f"{self.url}{path}"
            body = await self._request("POST", url, headers, None)
            return body["data"]
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    async def get_bullet_private(self) -> dict[str, Any]:
        try:
            path = "/api/v1/bullet-private"
            headers = self._get_headers(method="POST", path=path)
            url = f"{self.url}{path}"
            body = await self._request("POST", url, headers, None)
            return body["data"]
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")

    async def _fetch_symbol_infos(self) -> dict[Symbol, SymbolInfo]:
        try:
            path = "/api/v1/contracts/active"
            headers = self._get_headers(method="GET", path=path)
            url = f"{self.url}{path}"
            body = await self._request("GET", url, headers, None)

            symbol_infos = {}

            responses = body["data"]
            for response in responses:
                multiplier = Decimal(str(response["multiplier"]))
                tick_size = Decimal(str(response["tickSize"]))
                min_qty, max_qty = (
                    Decimal(str(response["lotSize"])) * multiplier,
                    Decimal(str(response["maxOrderQty"])),
                )
                symbol = Symbol(response["symbol"])

                symbol_infos[symbol] = SymbolInfo(
                    symbol=symbol,
                    quantity_precision=extract_precision(multiplier),
                    price_precision=extract_precision(tick_size),
                    exchange=Exchange.KUCOIN_LINEAR,
                    tick_size=tick_size,
                    max_post_only_qty=max_qty,
                    max_limit_qty=max_qty,
                    min_limit_qty=min_qty,
                    max_market_qty=max_qty,
                    min_market_qty=min_qty,
                    min_notional=Decimal("0"),
                    max_notional=Decimal(str(sys.float_info.max)),
                    quanto_multiplier=multiplier,
                )

            return symbol_infos
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise DeserializationError(f"Failed to load json: {e}")
