#include <Arduino.h>

#include "Stepper.hpp"
#include "Utils.hpp"
#include "Arm.hpp"
#include "Debug.hpp"

Arm::ArmParam arm_pargram = {1, 2, 3, 1, 1, 1, 20.0};
Arm arm(Serial1, arm_pargram);

void serial_on_msg() {
  static bool enable = 1;
  String input = Serial.readStringUntil('\n');
  input.trim();
  std::vector<String> tokens = split(input, ' ');
  if (tokens[0] == "SPEED") {
    int j1 = tokens[1].toInt();
    int j2 = tokens[2].toInt();
    int j3 = tokens[3].toInt();

    j1 = clip(j1, -50, 50);
    j2 = clip(j2, -50, 50);
    j3 = clip(j3, -50, 50);

    Serial.println("J1: " + String(j1) + " J2: " + String(j2) + " J3: " + String(j3));

    arm.set_joint_speed(j1, j2, j3);
  }

  if (tokens[0] == "ANGLE") {
    int j1 = tokens[2].toInt();
    int j2 = tokens[3].toInt();
    int j3 = tokens[1].toInt();

    j1 = clip(-j1, -70, 70);
    j2 = clip(j2, -70, 70);
    j3 = clip(j3, -70, 70);

    Serial.println("J1: " + String(j1) + " J2: " + String(j2) + " J3: " + String(j3));

    arm.set_joint_angle(j1, j2, j3);
  }
}

void loop_run() {
  // 串口协议处理
  if (Serial.available()) {
    serial_on_msg();
  }
  delay(1);
}

void loop_test() {

}

void setup_run() {
  Serial.begin(115200);
  Serial1.begin(115200, SERIAL_8N1, 25, 26);

  Serial.println("Hello, World!");
  
  delay(2000);
}

void setup_test() {
  Serial.begin(115200);
  std::vector<int> a = {1, 2, 3};
  debug(a);
}

void setup() {
  // setup_run();
  setup_run();
}

void loop() {
  // loop_run();
  loop_run();
}