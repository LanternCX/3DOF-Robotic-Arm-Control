# utils/socket.py
import asyncio
import json
import websockets
from typing import Callable, Optional
from utils.logger import get_logger

logger = get_logger("socket")

class WebSocketServer:
    def __init__(self, host="localhost", port=8765, on_message: Optional[Callable] = None):
        """
        WebSocket 服务端
        :param host: 主机地址
        :param port: 监听端口
        :param on_message: 回调函数，形如 on_message(data, websocket)
        """
        self.host = host
        self.port = port
        self.on_message = on_message
        self.clients = set()

    async def _handler(self, websocket):
        self.clients.add(websocket)
        addr = websocket.remote_address
        logger.info(f"Client connected: {addr}")
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if self.on_message:
                        await self.on_message(data, websocket)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from {addr}: {message}")
        except Exception as e:
            logger.warning(f"Client {addr} disconnected with error: {e}")
        finally:
            self.clients.remove(websocket)
            logger.info(f"Client disconnected: {addr}")

    async def send_to_all(self, data: dict):
        """广播 JSON 消息"""
        if not self.clients:
            return
        message = json.dumps(data)
        await asyncio.gather(*(client.send(message) for client in self.clients))

    async def start(self):
        """启动服务器"""
        async with websockets.serve(self._handler, self.host, self.port):
            logger.info(f"Listening on ws://{self.host}:{self.port}")
            await asyncio.Future()  # 保持运行

# ----------------------------------------------------------------------

class WebSocketClient:
    def __init__(self, uri="ws://localhost:8765", on_message: Optional[Callable] = None, reconnect=True):
        """
        WebSocket 客户端
        :param uri: 服务端地址
        :param on_message: 回调函数，形如 on_message(data)
        :param reconnect: 断开后是否自动重连
        """
        self.uri = uri
        self.on_message = on_message
        self.reconnect = reconnect
        self.websocket = None

    async def connect(self):
        """连接并持续监听"""
        while True:
            try:
                async with websockets.connect(self.uri) as ws:
                    self.websocket = ws
                    logger.info(f"Connected to {self.uri}")
                    async for message in ws:
                        try:
                            data = json.loads(message)
                            if self.on_message:
                                await self.on_message(data)
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON received: {message}")
            except Exception as e:
                logger.warning(f"Connection error: {e}")
                if not self.reconnect:
                    break
                logger.info("Reconnecting in 3 seconds...")
                await asyncio.sleep(3)

    async def send(self, data: dict):
        """发送 JSON 数据"""
        if self.websocket:
            await self.websocket.send(json.dumps(data))
        else:
            logger.warning("Not connected yet, cannot send.")
