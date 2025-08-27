#include <Arduino.h>

#include "Stepper.hpp"
#include "Utils.hpp"
#include "Arm.hpp"

Arm arm(Serial1, {1, 2, 3, 1, 1, 1});

void serial_on_msg() {
  static bool enable = 1;
  String input = Serial.readStringUntil('\n');
  input.trim();
  std::vector<String> tokens = split(input, ' ');
  if (tokens[0] == "SPEED") {
    int j1 = tokens[1].toInt();
    int j2 = tokens[2].toInt();
    int j3 = tokens[3].toInt();

    j1 = clip(j1, -30, 30);
    j2 = clip(j2, -30, 30);
    j3 = clip(j3, -30, 30);

    Serial.println("J1: " + String(j1) + " J2: " + String(j2) + " J3: " + String(j3));

    arm.set_joint_speed(j1, j2, j3);
  }
}

void setup() {
  Serial.begin(115200);
  Serial1.begin(115200, SERIAL_8N1, 25, 26);

  Serial.println("Hello, World!");
  
  delay(2000);
}

void loop() {
  // 串口协议处理
  if (Serial.available()) {
    serial_on_msg();
  }
  delay(1);
}