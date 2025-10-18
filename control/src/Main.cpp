#include <Arduino.h>
#include <ESP32Servo.h>


#include "Stepper.hpp"
#include "Utils.hpp"
#include "Arm.hpp"
#include "Debug.hpp"

#define SERVO_PIN  18

// LEDC 通道配置
#define SERVO_CHANNEL   0       // 通道编号（0~15）
#define SERVO_FREQ      330      // 舵机 PWM 频率：330Hz（周期3.03ms）
#define SERVO_RESOLUTION 16     // 分辨率：16位（0~65535）步长为1/65535


#define SERVO_MIN_PULSE_US  500   // 0度脉宽（0.5ms）
#define SERVO_MAX_PULSE_US  2500  // 180度脉宽（2.5ms）
#define SERVO_MAX_ANGLE     180.0 // 最大角度


Arm::ArmParam arm_pargram = {1, 2, 3, 1, 1, 1, 20.0};
Arm arm(Serial1, arm_pargram);

Servo servo;

// 将角度映射为占空比值
uint32_t angleToDuty(float angle) {
  // 限制角度范围
  if (angle < 0) angle = 0;
  if (angle > SERVO_MAX_ANGLE) angle = SERVO_MAX_ANGLE;

  // 根据角度计算脉宽（微秒）
  float pulseWidth = SERVO_MIN_PULSE_US + (SERVO_MAX_PULSE_US - SERVO_MIN_PULSE_US) * (angle / SERVO_MAX_ANGLE);

  // 将脉宽映射为 LEDC 的占空比值，1/330 = 0.00303s = 3030微秒
  uint32_t duty = (uint32_t)((pulseWidth / 3030.0) * ((1 << SERVO_RESOLUTION) - 1)); 

  return duty;
}

/**
 * @brief 打开夹抓
 * 
 */
void claw_open() {

  float startAngle = 1;     // 起始角度（闭合）
  float endAngle = 90;      // 目标角度（张开）
  float step = 2;           // 每次增加的角度
  int delayTime = 15;       // 每步之间的延时（毫秒）

  for (float angle = startAngle; angle <= endAngle; angle += step) 
  {
    uint32_t duty = angleToDuty(angle);                  // 计算对应占空比
    ledcWrite(SERVO_CHANNEL, duty);                      // 输出PWM信号
    delay(delayTime);                                    // 延时控制转动速度
  }

}

/**
 * @brief 闭合爪子
 * 
 */
void claw_close() {

  float startAngle = 90;     // 起始角度（张开）
  float endAngle = 1;      // 目标角度（闭合）
  float step = 2;           // 每次增加的角度（步进越小动作越平滑）
  int delayTime = 40;       // 每步之间的延时（毫秒）

  for (float angle = startAngle; angle >= endAngle; angle -= step) 
  {
    uint32_t duty = angleToDuty(angle);                  // 计算对应占空比
    ledcWrite(SERVO_CHANNEL, duty);                      // 输出PWM信号
    delay(delayTime);                                    // 延时控制转动速度
  }

}

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
    j3 = clip(j3, -180, 180);

    Serial.println("J1: " + String(j1) + " J2: " + String(j2) + " J3: " + String(j3));

    arm.set_joint_angle(j1, j2, j3);
  }

  if (tokens[0] == "CATCH") {
    // Serial.printf("Catch:\n%s\n",);
    if (tokens[1] == "ON") {
      Serial.println("ON");
      claw_open();
    }
    if (tokens[1] == "OFF") {
      Serial.println("OFF");
      claw_close();
    }
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

  ledcSetup(SERVO_CHANNEL, SERVO_FREQ, SERVO_RESOLUTION);
  ledcAttachPin(SERVO_PIN, SERVO_CHANNEL);

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