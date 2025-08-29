from typing import Literal

class Response:
    """
    HTTP Response.
    """

    ok: bool
    status: int
    version: str
    content_length: int | None
    url: str
    headers: dict[str, str]
    body: str

class Client:
    """
    HTTP client that handle requests to another HTTP server.
    It is implemented in Rust through [reqwest](https://github.com/seanmonstar/reqwest).
    """

    async def request(
        self,
        method: Literal["CONNECT", "DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT", "TRACE"],
        url: str,
        headers: dict[str, str] | None = None,
        body: str | None = None,
    ) -> Response:
        """
        Sends a HTTP request to the specified address and returns a response.
        """
