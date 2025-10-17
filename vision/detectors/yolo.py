from .base import BaseDetector
from utils.logger import get_logger
import cv2
import os
from ultralytics import YOLO

logger = get_logger("YoloDetector")

class YoloDetector(BaseDetector):
    """
    YOLOv11 模型检测器（离线加载本地权重）
    """
    def __init__(self, tag=None, model_path=None, conf_thres=0.25, filter_by_tag=True):
        super().__init__(tag)
        if model_path is None:
            current_dir = os.path.dirname(__file__)
            model_path = os.path.abspath(os.path.join(current_dir, "../../data/best.pt"))
        self.model_path = model_path
        self.model = None
        self.conf_thres = conf_thres
        self.filter_by_tag = filter_by_tag
        self._model_loaded = False  # 用于保证只加载一次

    def _load_model(self):
        if not self._model_loaded:
            if not os.path.exists(self.model_path):
                logger.error(f"[YOLO] Model file not found: {self.model_path}")
                return
            logger.info(f"[YOLO] Loading model from {self.model_path}")
            self.model = YOLO(self.model_path)
            self._model_loaded = True

    def detect(self, frame):
        self._load_model()
        if self.model is None:
            return [], frame

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.model(img)

        boxes = []
        for result in results:
            for det in result.boxes:
                x1, y1, x2, y2 = map(int, det.xyxy[0])
                conf = float(det.conf[0])
                cls_id = int(det.cls[0])
                label = self.model.names[cls_id]

                if conf < self.conf_thres:
                    continue

                # 标签过滤可选
                if self.filter_by_tag and self.tag is not None and label != self.tag:
                    continue

                boxes.append(((x1, y1), (x2, y2)))
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        logger.debug(f"[YOLO] Detected {len(boxes)} boxes (tag='{self.tag}').")
        return boxes, frame
