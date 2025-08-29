from typing import Optional
from cybotrade.io.event import EventHandler

class WsSender:
    async def ping(self, text: Optional[str]):
        """
        Forwards `text` to the websocket connection with a PING frame.
        """

    async def send(self, text: str):
        """
        Forwards `text` to the websocket connection with the TEXT frame.
        """

async def ws_stream(url: str, heartbeat_interval: int, event_handler: EventHandler):
    """
    Connect to the websocket server with the provided topics to listen for live updates.
    """
