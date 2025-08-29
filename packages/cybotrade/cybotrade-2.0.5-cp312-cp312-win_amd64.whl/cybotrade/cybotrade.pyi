from datetime import datetime, timedelta

__version__: str

class Symbol:
    def __init__(self, symbol: str):
        """
        Construct a symbol.

        Args:
            symbol: Symbol (e.g., "BTCUSDT")
        """
        pass

    def split(self) -> tuple[str, str] | None:
        """
        Split the symbol into a (base, quote) pair.

        Returns:
            Tuple of base and quote currency. (e.g., ("BTC", "USDT"))
        """
        pass

class Topic:
    def __init__(self, provider: str, endpoint: str, query_params: dict[str, str]):
        """
        Initialize a Topic instance.

        Args:
            provider: Provider name (e.g., "bybit-linear")
            endpoint: Endpoint name (e.g., "candle")
            query_params: Additional parameters as a query string (e.g., {"symbol":"BTCUSDT","interval":"1m"})
        """
        pass

    @staticmethod
    def from_str(topic: str) -> Topic:
        """
        Create a Topic instance from a string representation.

        Args:
            topic: Topic string in the format "provider|endpoint?query_params"

        Returns:
            Topic instance
        """
        pass

    def provider(self) -> str:
        """
        Get the provider of the topic.

        Returns:
            Provider name as a string (e.g., "bybit-linear")
        """
        pass

    def endpoint(self) -> str:
        """
        Get the endpoint of the topic.

        Returns:
            Endpoint name as a string (e.g., "candle")
        """
        pass

    def endpoint_with_query_params(self) -> str:
        """
        Get the endpoint with query parameters.

        Returns:
            Endpoint with query parameters as a string (e.g., "candle?symbol=BTCUSDT&interval=1m")
        """
        pass

    def query_params(self) -> dict[str, str]:
        """
        Get the query parameters of the topic.

        Returns:
            Query parameters as a dictionary (e.g., {"symbol": "BTCUSDT", "interval": "1m"})
        """
        pass

    def query_params_str(self) -> str:
        """
        Get the query parameters of the topic.

        Returns:
            Query parameters as a string (e.g., "symbol=BTCUSDT&interval=1m")
        """
        pass

    def interval(self) -> timedelta | None:
        """
        Get the interval of the topic.

        Returns:
            Interval as a timedelta object (e.g., timedelta(minutes=1) for "1m")
        """
        pass

    def last_closed_time_relative(
        self, timestamp: datetime, is_collect: bool
    ) -> datetime | None:
        """
        Get the last closed time relative to a given timestamp.

        Args:
            timestamp: The reference timestamp to calculate from
            is_collect: Whether get the last closed time for data collection
        """
        pass

    def last_closed_time(self, is_collect: bool) -> datetime | None:
        """
        Get the last closed time for the topic.

        Args:
            is_collect: Whether to get the last closed time for data collection
        """
        pass

    def delay_ms(self) -> int:
        """
        Get the delay in milliseconds for the topic.

        Returns:
            Delay in milliseconds (e.g., 1000 for 1 second)
        """
        pass

    def is_block(self) -> bool:
        """
        Check if the topic is a block topic.

        Returns:
            True if the topic is a block topic, False otherwise
        """
        pass
