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
