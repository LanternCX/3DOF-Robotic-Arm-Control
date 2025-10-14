import json

from command.registry import command
from utils.logger import get_logger
from control.move import set_angle
from control.kinematics import fk
from utils.math import rad2deg

logger = get_logger("echo")

@command("fk")
async def fk_handler(websocket, *args):
    """
    正解运动学
    :param websocket: websocket 对象
    :param args: 命令参数
    :return: none
    """

    angle1, angle2, angle3 = args[0], args[1], args[2]
    angle1, angle2, angle3 = float(angle1), float(angle2), float(angle3)
    set_angle(angle1, angle2, angle3)
    r, theta, h = fk(angle1, angle2, angle3)
    return {"type": "success", "args": [r, rad2deg(theta), h]}