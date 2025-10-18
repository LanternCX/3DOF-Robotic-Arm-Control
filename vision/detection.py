from .detectors.color import ColorDetector
from .detectors.yolo import YoloDetector
from utils.logger import get_logger

logger = get_logger("vision")

# 缓存检测器实例，避免每次都 new
DETECTOR_INSTANCES = {}

# 支持的检测器类
DETECTOR_MAP = {
    "green": ColorDetector,
    "red": ColorDetector,
    "blue": ColorDetector,
    "yolo": YoloDetector,
}

def get_detector(tag="green"):
    if tag in DETECTOR_INSTANCES:
        return DETECTOR_INSTANCES[tag]

    if tag not in DETECTOR_MAP:
        logger.error(f"Unknown detection tag: {tag}")
        return None

    detector_class = DETECTOR_MAP[tag]

    # YOLO 可以选择关闭标签过滤，先显示所有框
    if tag == "yolo":
        detector = detector_class(tag=None, filter_by_tag=False)
    else:
        detector = detector_class(tag)

    DETECTOR_INSTANCES[tag] = detector
    return detector

def detect_boxes(frame, tag="yolo"):
    detector = get_detector(tag)
    if detector is None:
        return [], frame
    return detector.detect(frame)

# 以下函数保持不变
prev_centers = []
prev_boxes_edges = []

def get_first_box_center(boxes):
    if not boxes:
        return None
    (x1, y1), (x2, y2) = boxes[0]
    return (x1 + x2) / 2, (y1 + y2) / 2

def is_camera_moved(current_boxes, threshold_px=5):
    global prev_boxes_edges
    if not current_boxes:
        prev_boxes_edges = []
        logger.debug("Camera not moved: no target")
        return False

    current_edges = []
    for box in current_boxes:
        if len(box) != 2:
            continue
        (x1, y1), (x2, y2) = box
        current_edges.append((x1, y1, x2, y2))

    if not prev_boxes_edges:
        prev_boxes_edges = current_edges
        logger.debug("Camera not moved: no prev")
        return False

    if len(current_edges) != len(prev_boxes_edges):
        prev_boxes_edges = current_edges
        logger.debug("Camera moved: box count changed")
        return True

    moved = False
    for prev, curr in zip(prev_boxes_edges, current_edges):
        dx_left = abs(curr[0] - prev[0])
        dy_top = abs(curr[1] - prev[1])
        dx_right = abs(curr[2] - prev[2])
        dy_bottom = abs(curr[3] - prev[3])
        if max(dx_left, dy_top, dx_right, dy_bottom) > threshold_px:
            moved = True
            logger.debug(
                f"Camera movement detected: box edges shift=({dx_left:.1f},{dy_top:.1f},{dx_right:.1f},{dy_bottom:.1f})")
            break

    prev_boxes_edges = current_edges
    if not moved:
        logger.debug("Camera stable based on box edges")
    return moved
