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
    // 维护当前位置（关节角度）
    float angle_j1 = Arm::arm_status.angle_j1;
    float angle_j2 = Arm::arm_status.angle_j2;
    float angle_j3 = Arm::arm_status.angle_j3;

    // 目标角度差
    float angle_det_j1 = j1 - angle_j1;
    float angle_det_j2 = j2 - angle_j2;
    float angle_det_j3 = j3 - angle_j3;

    // 角度差按照减速比转换到步数
    const float steps_per_deg = (3200.0f * Arm::arm_parm.ratio) / 360.0f;
    int32_t step_j1 = static_cast<int32_t>(angle_det_j1 * steps_per_deg);
    int32_t step_j2 = static_cast<int32_t>(angle_det_j2 * steps_per_deg);
    int32_t step_j3 = static_cast<int32_t>(angle_det_j3 * steps_per_deg);

    // 执行相对移动
    stepper_j1.add_position(step_j1, speed, acc, true);
    stepper_j2.add_position(step_j2, speed, acc, true);
    stepper_j3.add_position(step_j3, speed, acc, true);

    // 更新状态
    Arm::arm_status.angle_j1 = j1;
    Arm::arm_status.angle_j2 = j2;
    Arm::arm_status.angle_j3 = j3;

    // 同步启动
    Stepper::sync_all(Arm::serial);
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
    const float L1 = 124.75;
    const float L2 = 190;
    const float L3 = 197;

    float l = std::sqrt(r * r + (h - L1) * (h - L1));
    float alpha = std::atan2(h - L1, r);
    float beta = std::acos((l * l + L2 * L2 - L3 * L3) / (2 * L2 * l));

    float theta1 = theta;
    float theta2 = PI / 2 - (alpha + beta);
    float theta3 = std::acos((l * l - L2 * L2 - L3 * L3) / (2 * L2 * L3)) - (alpha + beta);

    set_joint_angle(theta1, theta2, theta3, speed, acc);
}