import json
from cybotrade.exceptions import CybotradeError
from cybotrade import http


class BinanceError(CybotradeError):
    """
    Error based on Binance's error code.

    See [docs](https://bybit-exchange.github.io/docs/v5/error).
    """

    code: int | None = None

    def __init__(self, response: http.Response) -> None:
        try:
            body = json.loads(response.body)
            if "code" in body:
                self.code = int(body["code"])
                self.message = f"Error Code {body['code']}: {body}"
            else:
                self.message = f"{body}"
        except Exception:
            self.message = f"HTTP {response.status}: {response.body}"
        super().__init__(self.message)
