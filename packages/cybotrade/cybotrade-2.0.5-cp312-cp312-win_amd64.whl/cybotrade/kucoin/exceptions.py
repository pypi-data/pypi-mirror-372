import json
from cybotrade.exceptions import CybotradeError
from cybotrade.http import Response


class KucoinError(CybotradeError):
    """
    Error based on Kucoin's error code.

    See [docs](https://www.kucoin.com/docs/errors-code/futures-errors-code).
    """

    code: int | None = None

    def __init__(self, response: Response) -> None:
        try:
            body = json.loads(response.body)
            if "code" in body:
                self.message = f"Error Code {body['code']}: {body}"
                self.code = int(body["code"])
            else:
                self.message = f"{body}"
        except Exception:
            self.message = f"HTTP {response.status}: {response.body}"
        super().__init__(self.message)
