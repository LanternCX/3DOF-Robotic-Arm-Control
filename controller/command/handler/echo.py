import json

from command.registry import command
from utils.logger import get_logger

logger = get_logger("echo")

@command("echo")
async def echo_handler(websocket, *args):
    """
    echo command demo
    :param websocket: websocket 对象
    :param args: 命令参数
    :return: none
    """
    # args 是客户端发送的 args 列表
    await websocket.send(json.dumps({"type": "echo_reply", "msg": str(args)}))