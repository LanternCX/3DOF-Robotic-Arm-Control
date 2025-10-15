from .base import BaseDetector
from utils.logger import get_logger

logger = get_logger("YoloDetector")

class YoloDetector(BaseDetector):
    """
    YOLO 模型检测器（预留）
    """
    def __init__(self, tag, model_path="yolov8n.pt"):
        super().__init__(tag)
        self.model_path = model_path
        # 延迟加载 YOLO 模型逻辑

    def detect(self, frame):
        # 未来可在这里加载 YOLO 模型并执行检测
        logger.debug(f"[YOLO] Detecting tag '{self.tag}' not implemented yet.")
        return [], frame
