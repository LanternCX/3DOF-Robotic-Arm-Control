import math

from utils.logger import get_logger
from utils.serials import Serials
from .kinematics import ik

logger = get_logger("Control")

def move_to(r, theta, h):
    """
    移动到柱面坐标，弧度制，长度单位为毫米
    :return: none
    """
    logger.info(f"Move to: {r, theta, h}")
    angles = ik(r, theta, h)
    set_angle(angles)
    return angles

def set_angle(angle1, angle2=None, angle3=None):
    """
    设置三个关节的角度，弧度制
    :return: none
    """
    if angle2 is None and angle3 is None:
        if isinstance(angle1, (tuple, list)):
            angle1, angle2, angle3 = angle1
        else:
            raise ValueError("Three independent parameters or a triplet/list need to be passed in")

    logger.info(f"Set Angle: {angle1, angle2, angle3}")
    cmd = f"ANGLE {math.degrees(angle1):.2f} {math.degrees(angle2):.2f} {math.degrees(angle3):.2f}"
    Serials.send("arm", cmd)

def catch_on():
    """
    打开夹爪
    :return: none
    """
    logger.info("Catch on")
    Serials.send("arm", "CATCH ON")

def catch_off():
    """
    闭合夹爪
    :return: none
    """
    logger.info("Catch off")
    Serials.send("arm", "CATCH OFF")
