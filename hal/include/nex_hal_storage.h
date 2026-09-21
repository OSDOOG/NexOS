/**
 * @file nex_hal_storage.h
 * @brief NexOS Hardware Abstraction Layer - Flash and Block Storage Interface
 */

#ifndef NEX_HAL_STORAGE_H
#define NEX_HAL_STORAGE_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t total_size;
    uint32_t block_size;
    uint32_t sector_size;
    uint32_t page_size;
} nex_storage_geometry_t;

typedef struct nex_storage_driver {
    nex_err_t (*init)(void *ctx);
    nex_err_t (*read)(void *ctx, uint32_t address, void *buf, size_t size);
    nex_err_t (*write)(void *ctx, uint32_t address, const void *buf, size_t size);
    nex_err_t (*erase_sector)(void *ctx, uint32_t sector_address);
    nex_err_t (*get_geometry)(void *ctx, nex_storage_geometry_t *geom);
} nex_storage_driver_t;

nex_err_t nex_storage_init(const nex_storage_driver_t *driver, void *ctx);
nex_err_t nex_storage_read(uint32_t address, void *buf, size_t size);
nex_err_t nex_storage_write(uint32_t address, const void *buf, size_t size);
nex_err_t nex_storage_erase(uint32_t address, size_t size);

#ifdef __cplusplus
}
#endif

#endif /* NEX_HAL_STORAGE_H */
