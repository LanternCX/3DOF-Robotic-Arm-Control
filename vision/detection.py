import cv2
import numpy as np

from utils.logger import get_logger

logger = get_logger("vision")
# 保存上一帧的目标中心点
prev_centers = []
# 用于保存上一帧的 boxes 边缘信息
prev_boxes_edges = []

"""
识别目标
"""
def detect_boxes(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])

    mask = cv2.inRange(hsv, lower_green, upper_green)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for cnt in contours:
        if cv2.contourArea(cnt) < 500:
            continue
        x, y, w, h = cv2.boundingRect(cnt)
        boxes.append(((x, y), (x + w, y + h)))
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    logger.debug(f"Detected {len(boxes)} green boxes.")
    return boxes, frame

"""
获取第一个目标的中心
"""
def get_first_box_center(boxes):
    if not boxes:
        return None
    (x1, y1), (x2, y2) = boxes[0]
    return (x1 + x2) / 2, (y1 + y2) / 2


def is_camera_moved(current_boxes, threshold_px=5):
    """
    判断相机是否移动（基于 box 边缘位置和大小变化）

    参数:
        current_boxes: list of boxes，每个 box = (x1, y1, x2, y2)
        threshold_px: 超过此像素偏移认为移动

    返回:
        True / False
    """
    global prev_boxes_edges

    if not current_boxes:
        prev_boxes_edges = []
        return False  # 无目标，默认稳定

    # 计算当前 boxes 边缘
    current_edges = []
    for box in current_boxes:
        if len(box) != 4:
            continue
        x1, y1, x2, y2 = box
        current_edges.append((x1, y1, x2, y2))

    # 第一次调用，没有上一帧，保存并返回 False
    if not prev_boxes_edges:
        prev_boxes_edges = current_edges
        return False

    # 如果数量不同，也认为相机移动
    if len(current_edges) != len(prev_boxes_edges):
        prev_boxes_edges = current_edges
        logger.debug("Camera moved: box count changed")
        return True

    # 比较每个 box 的边缘偏移
    moved = False
    for prev, curr in zip(prev_boxes_edges, current_edges):
        dx_left = abs(curr[0] - prev[0])
        dy_top = abs(curr[1] - prev[1])
        dx_right = abs(curr[2] - prev[2])
        dy_bottom = abs(curr[3] - prev[3])

        # 如果任意边缘移动超过阈值，认为相机移动
        if max(dx_left, dy_top, dx_right, dy_bottom) > threshold_px:
            moved = True
            logger.debug(
                f"Camera movement detected: box edges shift=({dx_left:.1f},{dy_top:.1f},{dx_right:.1f},{dy_bottom:.1f})")
            break

    prev_boxes_edges = current_edges
    if not moved:
        logger.debug("Camera stable based on box edges")
    return moved
