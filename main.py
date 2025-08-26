import pygame
import time
import serial

pygame.init()
pygame.joystick.init()

joystick_count = pygame.joystick.get_count()
if joystick_count == 0:
    print("Unable to find any controller！")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Connect to controller: {joystick.get_name()}")

ser = serial.Serial('COM11', 115200, timeout=1)

control_val = {
    "A": 0,
    "B": 0,
    "X": 0,
    "Y": 0,
    "LEFT_SHOULDER": 0,
    "RIGHT_SHOULDER": 0,
    "LEFT_THUMB": 0,
    "RIGHT_THUMB": 0,
    "LEFT_TRIGGER": 0.0,
    "RIGHT_TRIGGER": 0.0,
    "LEFT_JOYSTICK_X": 0.0,
    "LEFT_JOYSTICK_Y": 0.0,
    "RIGHT_JOYSTICK_X": 0.0,
    "RIGHT_JOYSTICK_Y": 0.0
}

handle_map = {
    0: "LEFT_JOYSTICK_X",
    1: "LEFT_JOYSTICK_Y",
    2: "RIGHT_JOYSTICK_X",
    3: "RIGHT_JOYSTICK_Y",
    4: "RIGHT_TRIGGER",
    5: "LEFT_TRIGGER"
}

# main loop
try:
    while True:
        # Handle Controller Event
        for event in pygame.event.get():
            # Trigger and Joystick event
            if event.type == pygame.JOYAXISMOTION:
                for axis in range(joystick.get_numaxes()):
                    axis_value = joystick.get_axis(axis)
                    # print(f"Handle {axis} value: {axis_value:.2f}")
                    if axis in handle_map:
                        control_val[handle_map[axis]] = axis_value

        # print(f"x_speed: {control_val['LEFT_JOYSTICK_Y']}, y_speed：{control_val['RIGHT_JOYSTICK_X']}")

        command = "CONTROL " + str(int(control_val['RIGHT_JOYSTICK_X'] * 10)) + ' ' + str(int(control_val['LEFT_JOYSTICK_Y'] * 10))
        ser.write((command + "\n").encode())
        print("Tx: " + command)

        # if ser.in_waiting:
        #     line = ser.readline().decode(errors='ignore').strip()
        #     if line:
        #         print("Rx：", line)

        time.sleep(0.01)

except KeyboardInterrupt:
    print("Keyboard interrupt")
finally:
    pygame.quit()
