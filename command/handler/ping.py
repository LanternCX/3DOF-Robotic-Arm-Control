import json

from command.registry import command
from utils.logger import get_logger

logger = get_logger("ping")

@command("ping")
async def ping_handler(websocket, *args):
    """
    ping command demo
    :param websocket:
    :return:
    """
    logger.info("Ping received, replying pong")
    await websocket.send(json.dumps({"type": "pong"}))