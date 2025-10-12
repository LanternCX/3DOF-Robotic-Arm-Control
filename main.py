import atexit
import threading
import time

import cv2

from control.control import control_state_machine
from control.kinematics import fk
from control.move import set_angle
from utils.logger import get_logger
from utils.math import deg2rad
from utils.serials import Serials
from vision.vision import vision_thread_func

# ---------- 可调参数 ----------
# 判断机械臂运动稳定的连续帧数
SETTLE_CONSECUTIVE_FRAMES = 30
# 视觉线程循环等待时间，单位秒
VISION_SLEEP = 0.01
# 控制线程轮询间隔
CONTROL_POLL = 0.05
# 移动到中心点的目标误差，单位毫米
TARGET_TOLERANCE_MM = 8.0
# 最大微调尝试次数
MAX_MICROADJUST = 10
# 单次移动后的最长等待时间，单位秒
MAX_SETTLE_WAIT = 8.0
# 单次命令后，等待开始移动的的最长时间，单位秒
MAX_MOVE_START_WAIT = 4.0


# -------------------------------

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


state = SharedState()
ser = Serials.register("/dev/cu.usbserial-0001", "arm")

def cleanup():
    try:
        set_angle(deg2rad(0, 0, 0))
        Serials.close_all()
        cv2.destroyAllWindows()
        state.logger.info("Cleaned up and closed serial/camera.")
    except Exception as e:
        state.logger.error(f"Cleanup failed: {e}")


atexit.register(cleanup)


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        state.logger.error("Cannot open camera.")
        return

    state.cap = cap
    state.frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    state.frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    angle1, angle2, angle3 = deg2rad(0, 0, 45)
    set_angle(angle1, angle2, angle3)
    r, theta, h = fk(angle1, angle2, angle3)

    state.logger.info("Robot arm system initialized.")

    vis_t = threading.Thread(target=vision_thread_func, args=(state,), daemon=True)
    ctrl_t = threading.Thread(target=control_state_machine, args=(state, state.frame_w, state.frame_h, r, theta, h),
                              daemon=True)
    vis_t.start()
    ctrl_t.start()

    cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
    try:
        while not state.stop_request.is_set():
            with state.lock:
                frame = state.frame.copy() if state.frame is not None else None
                cam_moved = state.camera_moved
                sm_state = state.sm_state
                adjust_cnt = state.adjust_count
                last_err = state.last_error

            if frame is not None:
                info_lines = [
                    f"SM: {sm_state.name if sm_state else 'N/A'}",
                    f"Moved: {cam_moved}",
                    f"Adjust#: {adjust_cnt}",
                ]
                if last_err:
                    info_lines.append(f"Err(mm): dx={last_err[2]:.2f}, dy={last_err[3]:.2f}")

                y = 20
                for line in info_lines:
                    cv2.putText(frame, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                    y += 18

                cv2.imshow("frame", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('m'):
                state.manual_trigger = True
                state.move_request.set()
                state.logger.info("Manual move request (key 'm').")
            elif key == ord('q'):
                state.logger.info("Quit requested (key 'q').")
                state.stop_request.set()
                break

            time.sleep(0.02)

    except KeyboardInterrupt:
        state.logger.info("KeyboardInterrupt: stopping.")
        state.stop_request.set()
    finally:
        cap.release()
        cv2.destroyAllWindows()
        vis_t.join(timeout=1)
        ctrl_t.join(timeout=1)
        state.logger.info("Main exiting.")


if __name__ == "__main__":
    main()
