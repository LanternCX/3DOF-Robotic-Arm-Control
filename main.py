import cv2
import serial
import atexit
from utils.math import deg2rad
from control.kinematics import fk
from control.motion import move_to_box
from vision.detection import detect_boxes_from_frame
from utils.logger import get_logger

logger = get_logger("main")

def cleanup(ser):
    try:
        ser.write(b"ANGLE 0 0 0")
        ser.close()
        cv2.destroyAllWindows()
        logger.info("Cleaned up and closed serial/camera.")
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")

if __name__ == "__main__":
    ser = serial.Serial('/dev/cu.usbserial-0001', 115200, timeout=1)
    atexit.register(cleanup, ser)
    ser.write(b"ANGLE 0 0 45")

    cap = cv2.VideoCapture(0)
    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    angle1, angle2, angle3 = deg2rad(0, 0, 45)
    r, theta, h = fk(angle1, angle2, angle3)

    logger.info("Robot arm system initialized.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        boxes, frame = detect_boxes_from_frame(frame)
        cv2.imshow('frame', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('m'):
            r, theta, h, dx, dy = move_to_box(ser, boxes, frame_w, frame_h, r, theta, h)

        if key == ord('q'):
            break

    cap.release()
