import atexit
import threading
import time
import cv2
import asyncio

from command.controller import handle_server_message
from utils.socket import WebSocketServer

from control.control import control_state_machine
from control.kinematics import fk
from control.move import set_angle, catch_on
from utils.logger import get_logger
from utils.math import deg2rad
from utils.serials import Serials
from vision.vision import vision_thread_func

from shared.state import state

logger = get_logger("Main")

# ---------- 可调参数 ----------
SETTLE_CONSECUTIVE_FRAMES = 30
VISION_SLEEP = 0.01
CONTROL_POLL = 0.05
TARGET_TOLERANCE_MM = 8.0
MAX_MICROADJUST = 10
MAX_SETTLE_WAIT = 8.0
MAX_MOVE_START_WAIT = 4.0

ser = Serials.register("/dev/cu.usbserial-0001", "arm")


def cleanup():
    try:
        try:
            cv2.destroyAllWindows()
        except Exception as e:
            logger.warning(f"Failed to destroy windows: {e}")

        logger.info("Cleaned up and closed serial/camera.")
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")



# ---------------------- 新增部分 ----------------------
async def websocket_task():
    """异步启动 WebSocket 服务"""
    server = WebSocketServer(host="localhost", port=8765, on_message=handle_server_message)
    await server.start()
    logger.info("WebSocket server started.")


def start_websocket_in_thread():
    """在独立线程中运行 WebSocket 事件循环"""
    asyncio.run(websocket_task())
# -----------------------------------------------------


def main():
    # 注册退出函数
    atexit.register(cleanup)

    # 初始化视觉
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Cannot open camera.")
        return

    state.cap = cap
    state.frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    state.frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 初始化机械臂构型
    angle1, angle2, angle3 = deg2rad(0, 0, 30)
    set_angle(angle1, angle2, angle3)
    r, theta, h = fk(angle1, angle2, angle3)
    state.current_pos = r, theta, h
    catch_on()

    logger.info("Robot arm system initialized.")

    # 启动视觉线程与控制线程
    vis_t = threading.Thread(target=vision_thread_func, args=(state,), daemon=True)
    ctrl_t = threading.Thread(
        target=control_state_machine,
        args=(state, state.frame_w, state.frame_h),
        daemon=True
    )
    vis_t.start()
    ctrl_t.start()

    # 启动 WebSocket 服务线程（异步运行）
    ws_thread = threading.Thread(target=start_websocket_in_thread, daemon=True)
    ws_thread.start()

    logger.info("WebSocket server thread started.")
    cv2.namedWindow("frame", cv2.WINDOW_NORMAL)

    # OpenCV 调试窗口主循环（运行在主线程中）
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
                    cv2.putText(frame, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (0, 255, 255), 1)
                    y += 18

                cv2.imshow("frame", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('m'):
                state.manual_trigger = True
                state.move_request.set()
                logger.info("Manual move request (key 'm').")
            elif key == ord('q'):
                logger.info("Quit requested (key 'q').")
                state.stop_request.set()
                break

            time.sleep(0.02)

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt: stopping.")
        state.stop_request.set()
    finally:
        set_angle(deg2rad(0, 0, 0))
        catch_on()
        cap.release()
        cv2.destroyAllWindows()
        ctrl_t.join(timeout=1)
        vis_t.join(timeout=1)
        ws_thread.join(timeout=1)
        logger.info("Main exiting.")


if __name__ == "__main__":
    main()
