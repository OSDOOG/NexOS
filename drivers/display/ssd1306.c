/**
 * @file ssd1306.c
 * @brief NexOS Modular Display Driver: SSD1306 OLED (128x64 I2C)
 */

#include "nex_display_driver.h"
#include "nex_device.h"
#include "nex_log.h"
#include <string.h>

#define TAG "SSD1306"

static uint8_t s_framebuffer[1024]; /* 128 * 64 / 8 */

static int32_t ssd1306_write(nex_device_t *dev, const void *buf, size_t count) {
    (void)dev;
    if (count > sizeof(s_framebuffer)) count = sizeof(s_framebuffer);
    memcpy(s_framebuffer, buf, count);
    return (int32_t)count;
}

static const nex_driver_ops_t s_ssd1306_ops = {
    .open = NULL,
    .close = NULL,
    .read = NULL,
    .write = ssd1306_write,
    .ioctl = NULL
};

nex_err_t nex_ssd1306_init(uint8_t i2c_port, uint8_t i2c_addr) {
    (void)i2c_port;
    (void)i2c_addr;
    memset(s_framebuffer, 0, sizeof(s_framebuffer));

    nex_device_handle_t h;
    nex_err_t err = nex_device_register("/dev/display0", NEX_DEV_TYPE_DISPLAY, &s_ssd1306_ops, NULL, &h);
    if (err == NEX_OK) {
        nex_log_info(TAG, "SSD1306 128x64 OLED driver registered at /dev/display0");
    }
    return err;
}
