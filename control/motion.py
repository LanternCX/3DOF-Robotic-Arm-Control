import math

from utils.math import polar2xyz, xyz2polar
from utils.logger import get_logger
from utils.serials import Serials
from .control import move_to, set_angle
from .kinematics import ik

logger = get_logger("motion")

REAL_W = 245
READ_H = 130

"""
调整相机中心到目标
"""
def move_to_box(boxes, frame_w, frame_h, now_r, now_theta, now_h):
    from vision.detection import get_first_box_center
    center = get_first_box_center(boxes)
    if center is None:
        logger.warning("No target box detected.")
        return now_r, now_theta, now_h

    cx, cy = center
    dy = (cx - frame_w / 2) * (REAL_W / frame_w)
    dx = (cy - frame_h / 2) * (READ_H / frame_h)

    now_x, now_y, now_z = polar2xyz(now_r, now_theta, now_h)
    target_x = now_x + dx
    target_y = now_y + dy
    target_r, target_theta, target_h = xyz2polar(target_x, target_y, now_z)

    logger.info(f"Move to box: {center}")
    move_to(target_r, target_theta, target_h)

    return target_r, target_theta, target_h, dx, dy
