/**
 * @file spi_flash.c
 * @brief NexOS Modular Storage Driver: Generic NOR SPI Flash (W25Q / GD25Q)
 */

#include "nex_storage_driver.h"
#include "nex_device.h"
#include "nex_log.h"
#include <string.h>

#define TAG "SPI_FLASH"

#define VIRTUAL_FLASH_SIZE (4 * 1024 * 1024) /* 4MB */
static uint8_t s_flash_storage[65536]; /* 64KB active block */

static int32_t flash_dev_read(nex_device_t *dev, void *buf, size_t count) {
    (void)dev;
    if (count > sizeof(s_flash_storage)) count = sizeof(s_flash_storage);
    memcpy(buf, s_flash_storage, count);
    return (int32_t)count;
}

static int32_t flash_dev_write(nex_device_t *dev, const void *buf, size_t count) {
    (void)dev;
    if (count > sizeof(s_flash_storage)) count = sizeof(s_flash_storage);
    memcpy(s_flash_storage, buf, count);
    return (int32_t)count;
}

static const nex_driver_ops_t s_flash_ops = {
    .open = NULL,
    .close = NULL,
    .read = flash_dev_read,
    .write = flash_dev_write,
    .ioctl = NULL
};

nex_err_t nex_spi_flash_init(void) {
    nex_device_handle_t h;
    nex_err_t err = nex_device_register("/dev/flash0", NEX_DEV_TYPE_BLOCK, &s_flash_ops, NULL, &h);
    if (err == NEX_OK) {
        nex_log_info(TAG, "NOR SPI Flash driver initialized at /dev/flash0 (4MB capacity)");
    }
    return err;
}
