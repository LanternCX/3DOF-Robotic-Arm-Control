import json

from command.registry import command
from utils.logger import get_logger
from shared.state import state

logger = get_logger("catch")

@command("catch")
async def echo_handler(websocket, *args):
    """
    echo command demo
    :param websocket: websocket 对象
    :param args: 命令参数
    :return: none
    """
    # args 是客户端发送的 args 列表
    target_type = args[0]
    state.target_type = target_type
    state.move_request.set()
