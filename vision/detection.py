import cv2
import numpy as np
from utils.logger import get_logger

logger = get_logger("vision")

def detect_boxes_from_frame(frame):
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

def get_first_box_center(boxes):
    if not boxes:
        return None
    (x1, y1), (x2, y2) = boxes[0]
    return (x1 + x2) / 2, (y1 + y2) / 2
