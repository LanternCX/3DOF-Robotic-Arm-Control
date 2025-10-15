#pragma once

#include <Arduino.h>
#include "Stepper.hpp"

class Arm {
    public:
        /**
         * @param 机械臂参数
         */
        typedef struct {
            /**
             * @brief 电机串口地址
             */
            int _addr_j1, _addr_j2, _addr_j3;
            
            /**
             * @brief 机械臂参数，用于运动学逆解
             */
            int L1, L2, L3;

            /**
             * @brief 减速箱减速比
             */
            float ratio;
        } ArmParam;

        typedef struct {
            /**
             * @brief 关节角度
             */
           float angle_j1, angle_j2, angle_j3; 
        } ArmStatus;

        /**
         * @brief 云台构造函数
         * @param _serial 云台串口
         * @param _addr_x 水平轴电机地址
         * @param _addr_y 垂直轴电机地址
         */
        Arm(HardwareSerial& _serial, ArmParam _arm_param);
        
        /**
         * @brief 云台初始化
         */
        virtual void init();

        /**
         * @brief 设置关节角度
         * @param j1 关节 1 角度
         * @param j2 关节 2 角度
         * @param j3 关节 3 角度         
         * @param speed 到位速度（单位 rpm，正为 CCW，负为 CW，范围 ±5000）
         * @param acc 加速度（0~255），0 表示直接启动，默认 0
         */
        virtual void set_joint_angle(float j1, float j2, float j3, uint16_t speed = 30, uint8_t acc = 0);

        /**
         * @brief 设置关节速度
         * @param j1 关节 1 速度
         * @param j2 关节 2 速度
         * @param j3 关节 3 速度
         * @param acc 加速度（0~255），0 表示直接启动，默认 0
         */
        virtual void set_joint_speed(int16_t j1, int16_t j2, int16_t j3, uint8_t acc = 0);

        /**
         * @brief 移动到柱面坐标为 (r, theta, h) 的点
         * @param theta 柱面坐标角度
         * @param r 柱面坐标半径
         * @param h 柱面坐标高度
         * @param speed 速度
         * @param acc 加速度
         */
        virtual void move_to(float theta, float r, float h, uint16_t speed = 30, uint8_t acc = 0);

    private:
        ArmParam arm_parm;
        ArmStatus arm_status;
        Stepper stepper_j1;
        Stepper stepper_j2;
        Stepper stepper_j3;

        /**
         * @brief 转换角度到步数
         * @param angle 角度
         */
        static int32_t degree_to_step(float angle);

        HardwareSerial& serial;
};