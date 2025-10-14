import json

from command.registry import command
from utils.logger import get_logger
from control.move import move_to
from utils.math import rad2deg

logger = get_logger("echo")

@command("ik")
async def ik_handler(websocket, *args):
    """
    逆解坐标值
    :param websocket: websocket 对象
    :param args: 命令参数
    :return: none
    """

    r, theta, h = float(args[0]), float(args[1]), float(args[2])
    angles = move_to(r, theta, h)
    return {"type": "success", "args": rad2deg(angles)}