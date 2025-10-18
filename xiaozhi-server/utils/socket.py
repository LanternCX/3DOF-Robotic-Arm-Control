import websockets
from config.logger import setup_logging

logger = setup_logging()

class WebSocketClient:
    def __init__(self, uri="ws://127.0.0.1:8765"):
        self.uri = uri
        self.websocket = None

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        logger.info(f"Connect to {self.uri}")


    async def send(self, message: str):
        if not self.websocket:
            raise RuntimeError("WebSocket not connect, use connect() first")
        await self.websocket.send(message)
        logger.info(f"Send: {message}")

    async def receive(self):
        if not self.websocket:
            raise RuntimeError("WebSocket not connect, use connect() first")
        msg = await self.websocket.recv()
        logger.info(f"receive: {msg}")
        return msg

    async def close(self):
        if self.websocket:
            await self.websocket.close()
            logger.info(f"Websocket {self.uri} dis connect")
