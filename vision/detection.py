from .detectors.color import ColorDetector
from .detectors.yolo import YoloDetector

from utils.logger import get_logger

logger = get_logger("vision")
# 保存上一帧的目标中心点
prev_centers = []
# 用于保存上一帧的 boxes 边缘信息
prev_boxes_edges = []

DETECTOR_MAP = {
    "green": ColorDetector,
    "red": ColorDetector,
    "blue": ColorDetector,
    "yolo": YoloDetector,
}

def detect_boxes(frame, tag="green"):
    """
    根据 tag 自动选择检测器
    """
    if tag not in DETECTOR_MAP:
        logger.error(f"Unknown detection tag: {tag}")
        return [], frame

    detector_class = DETECTOR_MAP[tag]
    detector = detector_class(tag)
    return detector.detect(frame)


def get_first_box_center(boxes):
    """
    获取第一个目标的中心
    """
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
        logger.debug("Camera not moved: no target")
        return False  # 无目标，默认稳定

    # 计算当前 boxes 边缘
    current_edges = []
    for box in current_boxes:
        if len(box) != 2:
            continue
        (x1, y1), (x2, y2) = box
        current_edges.append((x1, y1, x2, y2))

    # 第一次调用，没有上一帧，保存并返回 False
    if not prev_boxes_edges:
        prev_boxes_edges = current_edges
        logger.debug("Camera not moved: no prev")
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
