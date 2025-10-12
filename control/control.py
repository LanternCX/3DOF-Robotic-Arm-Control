import time
from enum import Enum, auto

from control.motion import move_to_box, REAL_W, READ_H
from vision.detection import get_first_box_center


# 状态机状态定义
class SMState(Enum):
    IDLE = auto()
    SEND_MOVE = auto()
    WAIT_START = auto()
    WAIT_STOP = auto()
    EVALUATE = auto()
    DONE = auto()
    FAILED = auto()


def compute_center_error_mm(state, boxes, frame_w, frame_h):
    """
    计算目标偏差（像素 -> 毫米）
    返回：abs_dx_mm, abs_dy_mm, signed_dx_mm, signed_dy_mm
    """
    try:
        center = get_first_box_center(boxes)
    except Exception:
        return None

    if center is None:
        return None

    cx, cy = center
    signed_dx_mm = (cx - frame_w / 2.0) * (REAL_W / frame_w)
    signed_dy_mm = (cy - frame_h / 2.0) * (READ_H / frame_h)
    return abs(signed_dx_mm), abs(signed_dy_mm), signed_dx_mm, signed_dy_mm


def wait_for_movement_start(state, timeout_secs=4.0, CONTROL_POLL=0.05):
    """
    等待相机检测到开始移动（camera_moved False -> True）
    """
    start_time = time.time()
    seen_not_moved = False
    while time.time() - start_time < timeout_secs and not state.stop_request.is_set():
        with state.lock:
            cm = state.camera_moved
        if not cm:
            seen_not_moved = True
        elif seen_not_moved and cm:
            return True
        time.sleep(CONTROL_POLL)
    return False


def wait_for_settle(state, SETTLE_CONSECUTIVE_FRAMES=30, timeout_secs=8.0, CONTROL_POLL=0.05):
    """
    等待相机连续稳定 N 帧（camera_moved 连续为 False）
    """
    consecutive = 0
    start_time = time.time()
    while time.time() - start_time < timeout_secs and not state.stop_request.is_set():
        with state.lock:
            cm = state.camera_moved
        if not cm:
            consecutive += 1
        else:
            consecutive = 0
        if consecutive >= SETTLE_CONSECUTIVE_FRAMES:
            return True
        time.sleep(CONTROL_POLL)
    return False


def control_state_machine(state, frame_w, frame_h, r, theta, h,
                          TARGET_TOLERANCE_MM=5.0, MAX_MICROADJUST=10,
                          CONTROL_POLL=0.05):
    """
    机械臂状态机实现：
    IDLE -> SEND_MOVE -> WAIT_START -> WAIT_STOP -> EVALUATE -> (DONE/FAILED/->SEND_MOVE)
    """
    sm_state = SMState.IDLE
    local_boxes = []
    local_frame_w = frame_w
    local_frame_h = frame_h
    adjust_count = 0
    last_error = None

    while not state.stop_request.is_set():
        state.sm_state = sm_state
        state.adjust_count = adjust_count
        state.last_error = last_error

        if sm_state == SMState.IDLE:
            if state.move_request.wait(timeout=CONTROL_POLL):
                state.move_request.clear()
                with state.lock:
                    local_boxes = list(state.boxes)
                if not local_boxes:
                    state.logger.warning("SM: move requested but no boxes visible -> remain IDLE")
                    sm_state = SMState.FAILED
                else:
                    adjust_count = 0
                    sm_state = SMState.SEND_MOVE
            else:
                continue

        elif sm_state == SMState.SEND_MOVE:
            adjust_count += 1
            try:
                state.logger.info(f"SM: SEND_MOVE #{adjust_count} -> sending move_to_box")
                r, theta, h, dx, dy = move_to_box(local_boxes, local_frame_w, local_frame_h, r, theta, h)
                state.logger.info(f"SM: move command sent Δx={dx:.2f}, Δy={dy:.2f}")
                sm_state = SMState.WAIT_START
            except Exception as e:
                state.logger.error(f"SM: error sending move command: {e}")
                sm_state = SMState.FAILED

        elif sm_state == SMState.WAIT_START:
            started = wait_for_movement_start(state)
            if not started:
                state.logger.warning("SM: did not detect movement start (timeout). Proceeding to WAIT_STOP.")
            else:
                state.logger.debug("SM: movement start detected.")
            sm_state = SMState.WAIT_STOP

        elif sm_state == SMState.WAIT_STOP:
            settled = wait_for_settle(state)
            if not settled:
                state.logger.warning("SM: wait_for_settle timed out.")
            else:
                state.logger.debug("SM: movement settled (stopped).")
            sm_state = SMState.EVALUATE

        elif sm_state == SMState.EVALUATE:
            with state.lock:
                local_boxes = list(state.boxes)
            error = compute_center_error_mm(state, local_boxes, local_frame_w, local_frame_h)
            last_error = error
            if error is None:
                state.logger.warning("SM: target lost after move.")
                if adjust_count >= MAX_MICROADJUST:
                    sm_state = SMState.FAILED
                else:
                    sm_state = SMState.SEND_MOVE
                continue

            abs_dx_mm, abs_dy_mm, sdx, sdy = error
            state.logger.info(f"SM: post-move error dx={sdx:.2f}mm, dy={sdy:.2f}mm")

            if abs_dx_mm <= TARGET_TOLERANCE_MM and abs_dy_mm <= TARGET_TOLERANCE_MM:
                sm_state = SMState.DONE
            elif adjust_count >= MAX_MICROADJUST:
                sm_state = SMState.FAILED
            else:
                sm_state = SMState.SEND_MOVE

        elif sm_state == SMState.DONE:
            state.logger.info(f"SM: micro-adjust success after {adjust_count} attempts. error={last_error}")
            state.move_done.set()
            sm_state = SMState.IDLE
            adjust_count = 0
            last_error = None

        elif sm_state == SMState.FAILED:
            state.logger.warning(f"SM: micro-adjust failed after {adjust_count} attempts. last_error={last_error}")
            state.move_done.set()
            sm_state = SMState.IDLE
            adjust_count = 0
            last_error = None

        else:
            state.logger.error(f"SM: unexpected state {sm_state}, resetting to IDLE")
            sm_state = SMState.IDLE

    state.logger.info("Control SM exiting.")
