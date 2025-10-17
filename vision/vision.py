import time

from vision.detection import detect_boxes, is_camera_moved

def vision_thread_func(state, VISION_SLEEP=0.01):
    """
    视觉线程函数：
    1. 读取摄像头帧
    2. 检测目标盒子
    3. 判断相机是否移动
    4. 更新共享状态
    """
    cap = state.cap  # main 已经初始化

    state.logger.info("Vision thread started.")

    while not state.stop_request.is_set():
        if not cap.isOpened():
            state.logger.warning("Camera closed, exiting vision thread.")
            break

        ret, frame = cap.read()
        if not ret:
            time.sleep(VISION_SLEEP)
            continue

        boxes, vis_frame = detect_boxes(frame, state.target_type)
        num_boxes = len(boxes)

        # === 新增逻辑：根据目标数量与抓取次数判断 ===
        with state.lock:
            state.valid_target_count = num_boxes

        # 规则：奇数次抓取时目标数应为偶数，偶数次抓取时目标数应为奇数
        should_proceed = (num_boxes > 0) and ((num_boxes % 2) == (state.catch_cnt % 2))

        if should_proceed:
            state.has_target = True
            state.now_target_type = state.target_type
        else:
            # 清空状态，防止进入状态机
            boxes = []
            state.has_target = False

        with state.lock:
            state.boxes = boxes
            state.frame = vis_frame

        try:
            moved = is_camera_moved(boxes)
        except Exception as e:
            state.logger.error(f"is_camera_moved error: {e}")
            moved = False

        with state.lock:
            state.camera_moved = moved

        time.sleep(VISION_SLEEP)

    state.logger.info("Vision thread exiting.")
