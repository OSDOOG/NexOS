/**
 * @file nex_device.h
 * @brief NexOS Device Manager and Standardized Driver Interface
 */

#ifndef NEX_DEVICE_H
#define NEX_DEVICE_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define NEX_DEVICE_NAME_MAX 32

typedef enum {
    NEX_DEV_TYPE_UNKNOWN   = 0,
    NEX_DEV_TYPE_CHAR      = 1,
    NEX_DEV_TYPE_BLOCK     = 2,
    NEX_DEV_TYPE_NET       = 3,
    NEX_DEV_TYPE_DISPLAY   = 4,
    NEX_DEV_TYPE_BUS       = 5
} nex_device_type_t;

typedef struct nex_device nex_device_t;
typedef nex_device_t* nex_device_handle_t;

typedef struct nex_driver_ops {
    nex_err_t (*open)(nex_device_t *dev, uint32_t flags);
    nex_err_t (*close)(nex_device_t *dev);
    int32_t   (*read)(nex_device_t *dev, void *buf, size_t count);
    int32_t   (*write)(nex_device_t *dev, const void *buf, size_t count);
    nex_err_t (*ioctl)(nex_device_t *dev, uint32_t cmd, void *arg);
} nex_driver_ops_t;

struct nex_device {
    char name[NEX_DEVICE_NAME_MAX];
    nex_device_type_t type;
    const nex_driver_ops_t *ops;
    void *priv_data;
    uint32_t open_count;
    struct nex_device *next;
};

/**
 * @brief Initialize device manager registry.
 */
nex_err_t nex_device_manager_init(void);

/**
 * @brief Register a device driver into the system device tree.
 */
nex_err_t nex_device_register(const char *name,
                              nex_device_type_t type,
                              const nex_driver_ops_t *ops,
                              void *priv_data,
                              nex_device_handle_t *handle);

/**
 * @brief Unregister a device driver.
 */
nex_err_t nex_device_unregister(nex_device_handle_t handle);

/**
 * @brief Open device by name (e.g., "/dev/uart0", "/dev/display0").
 */
nex_err_t nex_device_open(const char *name, uint32_t flags, nex_device_handle_t *handle);

/**
 * @brief Close an opened device handle.
 */
nex_err_t nex_device_close(nex_device_handle_t handle);

/**
 * @brief Read data from device.
 */
int32_t nex_device_read(nex_device_handle_t handle, void *buf, size_t count);

/**
 * @brief Write data to device.
 */
int32_t nex_device_write(nex_device_handle_t handle, const void *buf, size_t count);

/**
 * @brief Send I/O control command to device.
 */
nex_err_t nex_device_ioctl(nex_device_handle_t handle, uint32_t cmd, void *arg);

/**
 * @brief Enumerate registered devices.
 */
void nex_device_list(void);

#ifdef __cplusplus
}
#endif

#endif /* NEX_DEVICE_H */
