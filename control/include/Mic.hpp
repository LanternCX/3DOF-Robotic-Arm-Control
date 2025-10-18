#pragma once
#include <Arduino.h>

class Mic {
   public:
    Mic(int8_t _i2s_ws, int8_t _i2s_sd, int8_t _i2s_sck, int _buffer_len, i2s_port_t i2s_port);
    
    /**
     * @brief 初始化
     */
    virtual void init();

    /**
     * @brief 读取数据
     * @return
     *    - ESP_OK: Success
     *    - ESP_ERR_INVALID_ARG: Parameter error
     */
    virtual esp_err_t read_data();

    /**
     * @brief 获取读取到的数据
     * @return 读取到的数据
     */
    virtual float get_data();
   private:
    int8_t i2s_ws, i2s_sd, i2s_sck;
    int buffer_len;
    i2s_port_t i2s_port;
    int16_t* read_data_bffer;
    size_t bytes_in;
};