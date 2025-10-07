#include <Arduino.h>
#include <driver/i2s.h>

#include "Mic.hpp"

Mic::Mic(int8_t _i2s_ws, int8_t _i2s_sd, int8_t _i2s_sck, int _buffer_len, i2s_port_t _i2s_port)
    : i2s_ws(_i2s_ws), i2s_sd(_i2s_ws), i2s_sck(_i2s_sck), 
    buffer_len(buffer_len), i2s_port(_i2s_port) {
    read_data_bffer = new int16_t[buffer_len];
}

void Mic::init() {
    const i2s_config_t i2s_config = {
        .mode = i2s_mode_t(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = 44100,
        .bits_per_sample = i2s_bits_per_sample_t(16),
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = i2s_comm_format_t(I2S_COMM_FORMAT_STAND_I2S),
        .intr_alloc_flags = 0,
        .dma_buf_count = 8,
        .dma_buf_len = buffer_len,
        .use_apll = false
    };
    i2s_driver_install(i2s_port, &i2s_config, 0, NULL);

    // Set I2S pin configuration
    const i2s_pin_config_t pin_config = {
        .bck_io_num = i2s_sck,
        .ws_io_num = i2s_ws,
        .data_out_num = -1,
        .data_in_num = i2s_sd
    };
    i2s_set_pin(i2s_port, &pin_config);

    i2s_start(i2s_port);
    delay(500);
}


esp_err_t Mic::read_data() {
    bytes_in = 0;
    esp_err_t result = i2s_read(i2s_port, &read_data_bffer, buffer_len, &bytes_in, portMAX_DELAY);
    return result;
}

float Mic::get_data() {
    // Read I2S data buffer
    int16_t samples_read = bytes_in / 8;
    if (samples_read > 0) {
        float mean = 0;
        for (int16_t i = 0; i < samples_read; ++i) {
            mean += (read_data_bffer[i]);
        }
        // Average the data reading
        mean /= samples_read;
        return mean;
    }
}
