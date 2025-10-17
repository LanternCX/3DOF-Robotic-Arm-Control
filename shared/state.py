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
        self.now_target_type = None
        self.has_target = False

        # 当前机械臂位置 (r, theta, h)
        self.current_pos = (0.0, 0.0, 0.0)
        # 抓取前位置，用于抓取流程
        self.pre_catch_pos = None

        # 用于控制多线程同步
        self.condition = threading.Condition()



state = SharedState()