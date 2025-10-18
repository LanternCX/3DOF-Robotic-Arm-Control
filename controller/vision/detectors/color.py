import cv2
import numpy as np
from .base import BaseDetector
from utils.logger import get_logger

logger = get_logger("ColorDetector")

COLOR_RANGES = {
    "green": ((35, 100, 100), (85, 255, 255)),
    "red":   ((0, 150, 150), (10, 255, 255)),
    "blue":  ((100, 150, 100), (140, 255, 255))
}

class ColorDetector(BaseDetector):
    """
    基于颜色阈值的目标检测器
    """

    def detect(self, frame):
        if self.tag not in COLOR_RANGES:
            logger.warning(f"Unknown color tag: {self.tag}")
            return [], frame

        lower, upper = COLOR_RANGES[self.tag]
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
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

        logger.debug(f"Detected {len(boxes)} {self.tag} boxes.")
        return boxes, frame
