/**
 * @file nex_display_driver.h
 * @brief NexOS Modular Display Driver Interface
 */

#ifndef NEX_DISPLAY_DRIVER_H
#define NEX_DISPLAY_DRIVER_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint16_t width;
    uint16_t height;
    uint8_t  bpp;
} nex_display_info_t;

nex_err_t nex_ssd1306_init(uint8_t i2c_port, uint8_t i2c_addr);
nex_err_t nex_st7789_init(uint8_t spi_bus, nex_pin_t dc_pin, nex_pin_t rst_pin, nex_pin_t cs_pin);

#ifdef __cplusplus
}
#endif

#endif /* NEX_DISPLAY_DRIVER_H */
