/**
 * @file st7789.c
 * @brief NexOS Modular Display Driver: ST7789 IPS LCD (240x240 SPI)
 */

#include "nex_display_driver.h"
#include "nex_device.h"
#include "nex_log.h"

#define TAG "ST7789"

static int32_t st7789_write(nex_device_t *dev, const void *buf, size_t count) {
    (void)dev;
    (void)buf;
    return (int32_t)count;
}

static const nex_driver_ops_t s_st7789_ops = {
    .open = NULL,
    .close = NULL,
    .read = NULL,
    .write = st7789_write,
    .ioctl = NULL
};

nex_err_t nex_st7789_init(uint8_t spi_bus, nex_pin_t dc_pin, nex_pin_t rst_pin, nex_pin_t cs_pin) {
    (void)spi_bus;
    (void)dc_pin;
    (void)rst_pin;
    (void)cs_pin;

    nex_device_handle_t h;
    nex_err_t err = nex_device_register("/dev/lcd0", NEX_DEV_TYPE_DISPLAY, &s_st7789_ops, NULL, &h);
    if (err == NEX_OK) {
        nex_log_info(TAG, "ST7789 240x240 IPS display driver registered at /dev/lcd0");
    }
    return err;
}
