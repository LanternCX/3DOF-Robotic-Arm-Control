from abc import ABC, abstractmethod

class BaseDetector(ABC):
    """
    所有检测器的基类
    """
    def __init__(self, tag):
        self.tag = tag

    @abstractmethod
    def detect(self, frame):
        """
        在图像中检测目标
        返回值: boxes, frame
        boxes: [((x1, y1), (x2, y2)), ...]
        frame: 可视化后的图像
        """
        pass
