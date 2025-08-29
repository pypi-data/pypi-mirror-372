import asyncio
import logging
import signal
import polars as pl

from typing import Any
from abc import abstractmethod
from apscheduler import AsyncScheduler
from apscheduler.abc import Trigger

from cybotrade_datasource import stream, query_paginated
from cybotrade import Topic
from cybotrade.io import Event, EventType, EventHandler


class BaseStrategy:
    """
    This is the 'base' Strategy class that Cybotrade provides standardization and ease of use.
    Any self-defined 'strategies' class will have to inherit this class.
    The `BaseStrategy` class provides the `schedule` and `start` methods that allows Cybotrade to
    abstract away logic to make running your strategies seamless and straight forward.

    E.g:
    ```
    trader = BybitLinearClient("api_key", "api_secret")
    exchange_ws = WSBybitClient("api_key", "api_secret")
    class MyStrategy(BaseStrategy):
        def __init__(self, trader: ExchangeClient):
            self.schedule("active_order", self.on_active_order_interval, 60)
            super().__init__(trader)

        def on_active_order_interval(self):
            self.trader.place_order(...)
            ...
        ...

    MyStrategy(trader, exchange_ws).start()
    ```
    """

    logger: logging.Logger = logging.getLogger(__name__)

    datasource_api_key: str | None = None
    datasource_topics: list[Topic] | None = None
    lookback_size: int | None = None
    datamap: dict[Topic, pl.DataFrame] = {}

    def __init__(
        self,
        datasource_api_key: str | None = None,
        datasource_topics: list[Topic] | None = None,
        lookback_size: int | None = None,
    ):
        self.scheduler = AsyncScheduler()
        self.lookback_size = lookback_size

        # Only setup datasource if topics are provided
        if datasource_topics is not None:
            if len(datasource_topics) == 0:
                raise Exception(
                    "'datasource_topics' must be an array with more than 1 topic."
                )
            if datasource_api_key is None:
                raise Exception(
                    "'datasource_api_key' must be provided if 'datasource_topics' is set."
                )

            self.datasource_topics = datasource_topics
            self.datasource_api_key = datasource_api_key

        def handle_signal(signum, frame):
            match signum:
                case signal.SIGINT | signal.SIGTERM:
                    self.on_shutdown()
                    exit(0)
                case _:
                    self.logger.warning(f"Handling signal ({signum}) by doing nothing.")

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

        self.on_init()

    async def schedule(
        self,
        fn_name: str,
        fn,
        trigger: Trigger,
    ):
        """
        Schedule a job in the background
        """
        await self.scheduler.add_schedule(
            id=fn_name, func_or_task_id=fn, trigger=trigger
        )

    def maintain_datamap(
        self, topic: Topic, data: Any, lookback_size: int | None = None
    ) -> bool:
        """
        Maintain the datamap for the given topic.
        This is used to store historical data for the topic.
        """
        if self.lookback_size is None and lookback_size is None:
            raise ValueError(
                "Either 'lookback_size' or 'self.lookback_size' must be set to maintain the datamap."
            )

        lookback_size = (
            self.lookback_size if self.lookback_size is not None else lookback_size
        )

        # make data into a dataframe (replace the start_time as a UTC timestamp)
        data = pl.DataFrame(data).with_columns(
            pl.col("start_time").dt.replace_time_zone(time_zone="UTC")
        )

        # maintain the datamap (push and pop from DataFrame)
        if topic not in self.datamap:
            self.datamap[topic] = data
        else:
            if len(self.datamap[topic]) == lookback_size:
                self.datamap[topic] = self.datamap[topic][1:]

            self.datamap[topic] = self.datamap[topic].extend(data)

        if self.lookback_size is not None:
            # check if all queues have the same length
            return all(
                len(queue) == self.lookback_size for queue in self.datamap.values()
            )
        else:
            # check if the queue has the same length as the lookback_size
            return len(self.datamap[topic]) == lookback_size

    @abstractmethod
    def on_init(self):
        pass

    @abstractmethod
    async def on_event(self, event: Event):
        """
        User-defined
        """
        pass

    @abstractmethod
    def on_shutdown(self):
        """user-defined"""
        pass

    async def _start_datasource(
        self,
        api_key: str,
        topics: list[Topic],
        lookback_size: int | None,
    ):
        if len(topics) > 0:
            if lookback_size is not None:
                for topic in topics:
                    self.logger.info(
                        f"retrieving lookback data with size of {lookback_size} for {topic}"
                    )
                    data = await query_paginated(
                        api_key, str(topic), limit=lookback_size
                    )
                    self.datamap[topic] = pl.DataFrame(data)
                    self.logger.info(
                        f"successfully collected data with size of {lookback_size} for {topic}"
                    )

            data_stream = await stream(api_key, list(map(lambda t: str(t), topics)))
            async for data in data_stream:
                try:
                    if "data" in data:
                        await self.on_event(
                            Event(
                                event_type=EventType.DatasourceUpdate,
                                orig=data,
                                data=data,
                            )
                        )
                    else:
                        await self.on_event(
                            Event(event_type=EventType.Subscribed, orig=data, data=data)
                        )
                except Exception as e:
                    self.logger.warning(f"Datasource WS encountered an exception: {e}")
                    continue

    async def start(self, events: EventHandler):
        events.on_event = self.on_event

        if self.datasource_topics is None or self.datasource_api_key is None:
            await asyncio.gather(self.scheduler.run_until_stopped(), events.start())
        else:
            await asyncio.gather(
                self.scheduler.run_until_stopped(),
                events.start(),
                self._start_datasource(
                    api_key=self.datasource_api_key,
                    topics=self.datasource_topics,
                    lookback_size=self.lookback_size,
                ),
            )
