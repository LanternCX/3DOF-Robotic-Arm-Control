import math
import serial
import threading

L1 = 124.75
L2 = 190
L3 = 197


def ik(r_, theta_, h_):
    l = math.sqrt(r_ * r_ + (h_ - L1) * (h_ - L1))
    alpha = math.atan2(h_ - L1, r_)
    beta = math.acos((l * l + L2 * L2 - L3 * L3) / (2 * L2 * l))

    _theta1 = theta_
    _theta2 = math.pi / 2 - (alpha + beta)
    _theta3 = math.acos((l * l - L2 * L2 - L3 * L3) / (2 * L2 * L3)) - (alpha + beta)
    return _theta1, _theta2, _theta3


def fk(theta1_, theta2_, theta3_):
    r1 = L2 * math.sin(theta2_)
    # alpha + beta
    alpha = (math.pi / 2) - theta2_
    r2 = L3 * math.sin(math.pi - theta2_ - (theta3_ + alpha))
    h1 = L2 * math.cos(theta2_)
    h2 = L3 * math.cos(math.pi - theta2_ - (theta3_ + alpha))

    _r = r1 + r2
    _h = L1 + h1 - h2
    _theta = theta1_
    return _r, _theta, _h

ser_xiaozhi = serial.Serial('/tmp/ttyV0', 115200, timeout=1)

ser_control = serial.Serial('/dev/cu.usbserial-0001', 115200, timeout=1)

if __name__ == '__main__':
    while True:
        data = ser_xiaozhi.readline().decode('utf-8').strip()
        tokens = data.split()
        if tokens:
            print("Serial Read:", tokens)
            if tokens[0] == "ik":
                print("IK: ", tokens[1], tokens[2], tokens[3])
                temp = ik(float(tokens[1]), math.radians(float(tokens[2])), float(tokens[3]))
                result = (round(math.degrees(temp[0])), round(math.degrees(temp[1])), round(math.degrees(temp[2])))
                print("IK-Result: ", result)
                msg = f"{result[0]} {result[1]} {result[2]}"
                ser_xiaozhi.write((msg + "\n").encode('utf-8'))
                cmd = f"ANGLE {result[0]} {result[1]} {result[2]}"
                print(f"Serial-USB: {cmd}")
                ser_control.write((cmd+"\n").encode('utf-8'))
            if tokens[0] == "fk":
                print("FK: ", tokens[1], tokens[2], tokens[3])
                temp = fk(math.radians(float(tokens[1])), math.radians(float(tokens[2])), math.radians(float(tokens[3])))
                result = (round(temp[0], 1), round(math.degrees(temp[1]), 1), round(temp[2], 1))
                print("FK-Result: ", result)
                msg = f"{result[0]} {result[1]} {result[2]}"
                ser_xiaozhi.write((msg + "\n").encode('utf-8'))
                cmd = f"ANGLE {tokens[1]} {tokens[2]} {tokens[3]}"
                print(f"Serial-USB: {cmd}")
                ser_control.write((cmd + "\n").encode('utf-8'))
