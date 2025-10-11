import math

import cv2
import numpy as np
import serial
import atexit

import utils

L1 = 124.75
L2 = 190
L3 = 197

REAL_W = 245
READ_H = 130

# ----------------- 运动学函数 -----------------
def ik(r_, theta_, h_):
    l = math.sqrt(r_ * r_ + (h_ - L1) ** 2)
    alpha = math.atan2(h_ - L1, r_)
    beta = math.acos((l ** 2 + L2 ** 2 - L3 ** 2) / (2 * L2 * l))
    _theta1 = theta_
    _theta2 = math.pi / 2 - (alpha + beta)
    _theta3 = math.acos((l ** 2 - L2 ** 2 - L3 ** 2) / (2 * L2 * L3)) - (alpha + beta)
    return _theta1, _theta2, _theta3

def fk(theta1_, theta2_, theta3_):
    r1 = L2 * math.sin(theta2_)
    alpha = math.pi / 2 - theta2_
    r2 = L3 * math.sin(math.pi - theta2_ - (theta3_ + alpha))
    h1 = L2 * math.cos(theta2_)
    h2 = L3 * math.cos(math.pi - theta2_ - (theta3_ + alpha))
    _r = r1 + r2
    _h = L1 + h1 - h2
    _theta = theta1_
    return _r, _theta, _h

def xyz2polar(x, y, z):
    r = math.hypot(x, y)
    theta = math.atan2(y, x)
    return r, theta, z

def polar2xyz(r, theta, h):
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return x, y, h

# ----------------- 摄像头检测 -----------------
def detect_boxes_from_frame(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # 适合较淡绿色
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])

    mask1 = cv2.inRange(hsv, lower_green, upper_green)
    mask2 = cv2.inRange(hsv, lower_green, upper_green)
    mask = cv2.bitwise_or(mask1, mask2)

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
    return boxes, frame

def get_first_box_center(boxes):
    if not boxes:
        return None
    (x1, y1), (x2, y2) = boxes[0]
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    return cx, cy

# ----------------- 移动逻辑 -----------------
def move_to_box(ser, boxes, frame_w, frame_h, now_r, now_theta, now_h):
    center = get_first_box_center(boxes)
    if center is None:
        print("No red box detected.")
        return now_r, now_theta, now_h

    cx, cy = center
    # 像素偏移映射到实际增量
    dy = (cx - frame_w / 2) * (REAL_W / frame_w)
    dx = (cy - frame_h / 2) * (READ_H / frame_h)

    print(dx, dy)

    # 从笛卡尔增量转换为柱面增量
    now_x, now_y, now_z = polar2xyz(now_r, now_theta, now_h)
    target_x = now_x + dx
    target_y = now_y + dy

    target_r, target_theta, target_h = xyz2polar(target_x, target_y, now_z)

    # 计算目标关节角度
    theta1, theta2, theta3 = ik(target_r, target_theta, target_h)

    # 发送指令
    cmd = f"ANGLE {math.degrees(theta1):.2f} {math.degrees(theta2):.2f} {math.degrees(theta3):.2f}"
    ser.write(cmd.encode('utf-8'))
    print(f"Sent command: {cmd}")

    return target_r, target_theta, target_h, dx, dy

def deg2rad(a1, a2, a3):
    return math.radians(a1), math.radians(a2), math.radians(a3)

# ----------------- 清理函数 -----------------
def cleanup():
    ser_control.write(f"ANGLE 0 0 0".encode('utf-8'))
    ser_control.close()
    cv2.destroyAllWindows()
    print("Cleaned up and closed serial/camera.")


# ----------------- 主程序 -----------------
if __name__ == '__main__':
    atexit.register(cleanup)

    ser_control = serial.Serial('/dev/cu.usbserial-0001', 115200, timeout=1)
    ser_control.write(f"ANGLE 0 0 45".encode('utf-8'))

    cap = cv2.VideoCapture(0)
    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 初始机械臂坐标
    angle1, angle2, angle3 = deg2rad(0, 0, 45)
    r, theta, h = fk(angle1, angle2, angle3)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        boxes, frame = detect_boxes_from_frame(frame)
        cv2.imshow('frame', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('m'):  # 按 m 键触发 MOVE
            r, theta, h, dx, dy = move_to_box(ser_control, boxes, frame_w, frame_h, r, theta, h)
            key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

    cap.release()
