/**
 * @file nex_hal_i2c.h
 * @brief NexOS Hardware Abstraction Layer - I2C Interface
 */

#ifndef NEX_HAL_I2C_H
#define NEX_HAL_I2C_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t speed_hz; /* 100000 (Standard) or 400000 (Fast) */
    nex_pin_t sda_pin;
    nex_pin_t scl_pin;
} nex_i2c_config_t;

nex_err_t nex_i2c_init(uint8_t port, const nex_i2c_config_t *config);
nex_err_t nex_i2c_write(uint8_t port, uint8_t addr, const uint8_t *data, size_t len);
nex_err_t nex_i2c_read(uint8_t port, uint8_t addr, uint8_t *data, size_t len);
nex_err_t nex_i2c_write_reg(uint8_t port, uint8_t addr, uint8_t reg, const uint8_t *data, size_t len);
nex_err_t nex_i2c_read_reg(uint8_t port, uint8_t addr, uint8_t reg, uint8_t *data, size_t len);
nex_err_t nex_i2c_deinit(uint8_t port);

#ifdef __cplusplus
}
#endif

#endif /* NEX_HAL_I2C_H */
