# ---------- 共享变量 ----------
import threading

from utils.logger import get_logger


class SharedState:
    def __init__(self):
        self.boxes = []
        self.frame = None
        self.frame_w = 0
        self.frame_h = 0
        self.camera_moved = False
        self.lock = threading.Lock()

        # 控制信号
        self.move_request = threading.Event()
        self.stop_request = threading.Event()
        self.move_done = threading.Event()
        self.manual_trigger = False

        # 可观察/调试的状态
        self.sm_state = None
        self.adjust_count = 0
        self.last_error = None

        # 线程和硬件相关
        self.cap = None
        self.logger = get_logger("Main")

        # 视觉目标
        self.target_type = "green"


state = SharedState()