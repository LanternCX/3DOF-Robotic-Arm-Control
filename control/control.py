import time
from enum import Enum, auto

from control.motion import move_to_box, REAL_W, READ_H
from utils.math import deg2rad
from vision.detection import get_first_box_center
from .kinematics import fk
from .move import move_to, catch_on, catch_off, set_angle


# 状态机状态定义
# 状态机状态定义
class SMState(Enum):
    # 空闲，等待命令
    IDLE = auto()
    # 发送移动指令到目标上方
    SEND_MOVE = auto()
    # 等待运动开始
    WAIT_START = auto()
    # 等待运动停止
    WAIT_STOP = auto()
    # 检测目标位置偏差
    EVALUATE = auto()
    # 对齐完成
    ALIGN_DONE = auto()
    # 对齐失败
    ALIGN_FAILED = auto()

    # 准备抓取
    CATCH_BEGIN = auto()
    # 下降到物体高度
    CATCH_DESCEND = auto()
    # 闭合夹爪
    CATCH_GRAB = auto()
    # 抬升机械臂
    CATCH_ASCEND = auto()
    # 移动到目标框内
    CATCH_MOVE = auto()
    # 张开夹爪
    CATCH_PUT = auto()
    # 抓取完成
    CATCH_DONE = auto()
    # 抓取流程结束
    CATCH_END = auto()

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


def control_state_machine(state, frame_w, frame_h,
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
            # 等待 move_request
            if state.move_request.wait(timeout=CONTROL_POLL):
                # 等待视觉线程的目标匹配
                with state.condition:
                    matched = state.condition.wait_for(lambda: state.target_type == state.now_target_type,
                                                       timeout=CONTROL_POLL)
                if not matched:
                    continue  # 超时或未匹配，回到循环等待

                state.move_request.clear()

                with state.lock:
                    local_boxes = list(state.boxes)

                if not local_boxes:
                    state.logger.warning("SM: move requested but no boxes visible -> remain IDLE")
                    sm_state = SMState.IDLE
                else:
                    adjust_count = 0
                    sm_state = SMState.SEND_MOVE
            else:
                continue

        elif sm_state == SMState.SEND_MOVE:
            adjust_count += 1
            try:
                state.logger.info(f"SM: SEND_MOVE #{adjust_count} -> sending move_to_box")

                r, theta, h = state.current_pos
                r, theta, h, dx, dy = move_to_box(local_boxes, local_frame_w, local_frame_h, r, theta, h)
                state.current_pos = r, theta, h

                state.logger.info(f"SM: move command sent Δx={dx:.2f}, Δy={dy:.2f}")
                sm_state = SMState.WAIT_START
            except Exception as e:
                state.logger.error(f"SM: error sending move command: {e}")
                sm_state = SMState.ALIGN_FAILED

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
                    sm_state = SMState.ALIGN_FAILED
                else:
                    sm_state = SMState.SEND_MOVE
                continue

            abs_dx_mm, abs_dy_mm, sdx, sdy = error
            state.logger.info(f"SM: post-move error dx={sdx:.2f}mm, dy={sdy:.2f}mm")

            if abs_dx_mm <= TARGET_TOLERANCE_MM and abs_dy_mm <= TARGET_TOLERANCE_MM:
                sm_state = SMState.ALIGN_DONE
            elif adjust_count >= MAX_MICROADJUST:
                sm_state = SMState.ALIGN_FAILED
            else:
                sm_state = SMState.SEND_MOVE

        elif sm_state == SMState.ALIGN_DONE:
            state.logger.info(f"SM: micro-adjust success after {adjust_count} attempts. error={last_error}")
            state.move_done.set()
            sm_state = SMState.CATCH_BEGIN
            adjust_count = 0
            last_error = None

        elif sm_state == SMState.ALIGN_FAILED:
            state.logger.warning(f"SM: micro-adjust failed after {adjust_count} attempts. last_error={last_error}")
            state.move_done.set()
            sm_state = SMState.CATCH_BEGIN
            adjust_count = 0
            last_error = None

        elif sm_state == SMState.CATCH_BEGIN:
            state.logger.info("SM: Catch begin -> preparing to grab")
            # 保存当前位置（若无 current_pos 则使用当前参数）
            state.pre_catch_pos = state.current_pos
            # try:
            #     # 打开夹爪
            #     catch_on()
            # except Exception as e:
            #     state.logger.error(f"SM: error during catch begin: {e}")
            #     sm_state = SMState.IDLE
            sm_state = SMState.CATCH_DESCEND
            time.sleep(1)

        elif sm_state == SMState.CATCH_DESCEND:
            state.logger.info("SM: Catch descend 10cm")
            try:
                r0, theta0, h0 = state.pre_catch_pos
                move_to(r0 - 50, theta0, h0 - 100)  # 向下 10 cm
                state.current_pos = (r0 - 50, theta0, h0 - 100)
            except Exception as e:
                state.logger.error(f"SM: error during descend: {e}")
                sm_state = SMState.CATCH_END
                continue

            sm_state = SMState.CATCH_GRAB
            time.sleep(5)

        elif sm_state == SMState.CATCH_GRAB:
            state.logger.info("SM: Catch grab (closing gripper)")
            try:
                # 闭合夹爪
                catch_off()
            except Exception as e:
                state.logger.error(f"SM: error closing gripper: {e}")
            sm_state = SMState.CATCH_ASCEND
            time.sleep(2)

        elif sm_state == SMState.CATCH_ASCEND:
            state.logger.info("SM: Catch ascend back to pre-catch height")
            try:
                r0, theta0, h0 = state.pre_catch_pos
                move_to(r0, theta0, h0)
                state.current_pos = (r0, theta0, h0)
            except Exception as e:
                state.logger.error(f"SM: error during ascend: {e}")
                sm_state = SMState.CATCH_END
                continue

            sm_state = SMState.CATCH_MOVE
            time.sleep(5)

        elif sm_state == SMState.CATCH_MOVE:
            state.logger.info("SM: Catch move to target box")
            try:
                target_angle = deg2rad(90, 0, 0)
                set_angle(target_angle)
                state.current_pos = fk(target_angle[0], target_angle[1], target_angle[2])
            except Exception as e:
                state.logger.error(f"SM: error during move: {e}")
                sm_state = SMState.CATCH_END
            sm_state = SMState.CATCH_PUT
            time.sleep(10)

        elif sm_state == SMState.CATCH_PUT:
            state.logger.info("SM: Put object to target box")
            try:
                # 打开夹爪
                catch_on()
            except Exception as e:
                state.logger.error(f"SM: error during put: {e}")
                sm_state = SMState.IDLE
            sm_state = SMState.CATCH_DONE
            time.sleep(2)

        elif sm_state == SMState.CATCH_DONE:
            state.logger.info("SM: Catch done -> return to safe position")
            try:
                state.logger.info("Catch done.")
                target_angle = deg2rad(0, 0, 30)
                set_angle(target_angle)
                state.current_pos = fk(target_angle[0], target_angle[1], target_angle[2])
            except Exception as e:
                state.logger.error(f"SM: error returning to safe pos: {e}")
                sm_state = SMState.IDLE
            sm_state = SMState.CATCH_END
            time.sleep(5)

        elif sm_state == SMState.CATCH_END:
            state.logger.info("SM: Catch process finished, switching to IDLE")
            state.move_done.set()
            sm_state = SMState.IDLE
            time.sleep(5)

        else:
            state.logger.error(f"SM: unexpected state {sm_state}, resetting to IDLE")
            sm_state = SMState.IDLE

    state.logger.info("Control SM exiting.")
