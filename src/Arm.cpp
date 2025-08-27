#include "Arm.hpp"

Arm::Arm(HardwareSerial& _serial, ArmParam _arm_param)
    : serial(_serial), 
    stepper_j1(_serial, arm_parm._addr_j1), 
    stepper_j2(_serial, arm_parm._addr_j2),
    stepper_j3(_serial, arm_parm._addr_j3),
    arm_parm(_arm_param) {}

void Arm::init() {
    stepper_j1.init();
    stepper_j2.init();
    stepper_j3.init();
}

/**
 * @brief 转换角度到步数
 */
int32_t Arm::degree_to_step(float angle) {
    return static_cast<int32_t>((angle) * 3200.0f / 360.0f + 0.5f);
}

/**
 * @brief 设置关节角度
 */
void Arm::set_joint_angle(float j1, float j2, float j3, uint16_t speed, uint8_t acc) {

}

/**
 * @brief 设置关节速度
 */
void Arm::set_joint_speed(int16_t j1, int16_t j2, int16_t j3, uint8_t acc){
    stepper_j1.set_speed(j1, acc, true);
    stepper_j2.set_speed(j2, acc, true);
    stepper_j3.set_speed(j3, acc, true);
    Stepper::sync_all(Arm::serial);
}

/**
 * @brief 逆解出关节位置
 */
void Arm::move_to(float theta, float r, float h, uint16_t speed, uint8_t acc) {

}