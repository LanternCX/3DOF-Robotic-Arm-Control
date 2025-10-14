import json

from command.registry import command
from utils.logger import get_logger
from control.move import set_angle

logger = get_logger("echo")

@command("fk")
async def echo_handler(websocket, *args):
    """
    正解运动学
    :param websocket: websocket 对象
    :param args: 命令参数
    :return: none
    """

    angle1, angle2, angle3 = args[0], args[1], args[2]
    set_angle(angle1, angle2, angle3)
