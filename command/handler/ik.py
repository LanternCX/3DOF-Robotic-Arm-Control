import json

from command.registry import command
from utils.logger import get_logger
from control.move import move_to

logger = get_logger("echo")

@command("ik")
async def echo_handler(websocket, *args):
    """
    逆解坐标值
    :param websocket: websocket 对象
    :param args: 命令参数
    :return: none
    """

    r, theta, h = args[0], args[1], args[2]
    move_to(r, theta, h)