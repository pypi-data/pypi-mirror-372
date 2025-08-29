import json
from cybotrade.exceptions import CybotradeError
from cybotrade.http import Response


class BybitError(CybotradeError):
    """
    Error based on Bybit's error code.

    See [docs](https://bybit-exchange.github.io/docs/v5/error).
    """

    def __init__(self, response: Response) -> None:
        try:
            body = json.loads(response.body)
            if "retCode" in body:
                self.message = f"Error Code {body['retCode']}: {body}"
            else:
                self.message = f"{body}"
        except Exception:
            self.message = f"HTTP {response.status}: {response.body}"
        super().__init__(self.message)
