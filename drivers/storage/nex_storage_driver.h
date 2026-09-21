/**
 * @file nex_storage_driver.h
 * @brief NexOS Modular Storage Driver Interface
 */

#ifndef NEX_STORAGE_DRIVER_H
#define NEX_STORAGE_DRIVER_H

#include "nex_types.h"
#include "nex_hal_storage.h"

#ifdef __cplusplus
extern "C" {
#endif

nex_err_t nex_spi_flash_init(void);
nex_err_t nex_sd_spi_init(uint8_t spi_bus, nex_pin_t cs_pin);

#ifdef __cplusplus
}
#endif

#endif /* NEX_STORAGE_DRIVER_H */
