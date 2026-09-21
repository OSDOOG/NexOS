/**
 * @file nex_device.c
 * @brief NexOS Device Manager and VFS Device Tree Implementation
 */

#include "nex_device.h"
#include "nex_memory.h"
#include "nex_log.h"
#include <string.h>

#define TAG "DEV_MGR"

static nex_device_t *s_device_list = NULL;

nex_err_t nex_device_manager_init(void) {
    s_device_list = NULL;
    nex_log_info(TAG, "Device Manager initialized");
    return NEX_OK;
}

nex_err_t nex_device_register(const char *name,
                              nex_device_type_t type,
                              const nex_driver_ops_t *ops,
                              void *priv_data,
                              nex_device_handle_t *handle) {
    if (!name || !ops) return NEX_ERR_INVALID_ARG;

    /* Check for duplicate name */
    nex_device_t *curr = s_device_list;
    while (curr) {
        if (strcmp(curr->name, name) == 0) {
            return NEX_ERR_ALREADY_EXISTS;
        }
        curr = curr->next;
    }

    nex_device_t *dev = (nex_device_t *)nex_malloc(sizeof(nex_device_t));
    if (!dev) return NEX_ERR_NO_MEM;

    strncpy(dev->name, name, NEX_DEVICE_NAME_MAX - 1);
    dev->name[NEX_DEVICE_NAME_MAX - 1] = '\0';
    dev->type = type;
    dev->ops = ops;
    dev->priv_data = priv_data;
    dev->open_count = 0;
    dev->next = s_device_list;
    s_device_list = dev;

    if (handle) *handle = dev;
    nex_log_info(TAG, "Registered device '%s' (type=%d)", dev->name, type);
    return NEX_OK;
}

nex_err_t nex_device_unregister(nex_device_handle_t handle) {
    if (!handle) return NEX_ERR_INVALID_ARG;
    if (handle->open_count > 0) return NEX_ERR_BUSY;

    if (s_device_list == handle) {
        s_device_list = handle->next;
    } else {
        nex_device_t *curr = s_device_list;
        while (curr && curr->next) {
            if (curr->next == handle) {
                curr->next = handle->next;
                break;
            }
            curr = curr->next;
        }
    }

    nex_free(handle);
    return NEX_OK;
}

nex_err_t nex_device_open(const char *name, uint32_t flags, nex_device_handle_t *handle) {
    if (!name || !handle) return NEX_ERR_INVALID_ARG;

    nex_device_t *curr = s_device_list;
    while (curr) {
        if (strcmp(curr->name, name) == 0) {
            if (curr->ops && curr->ops->open) {
                nex_err_t err = curr->ops->open(curr, flags);
                if (err != NEX_OK) return err;
            }
            curr->open_count++;
            *handle = curr;
            return NEX_OK;
        }
        curr = curr->next;
    }
    return NEX_ERR_NOT_FOUND;
}

nex_err_t nex_device_close(nex_device_handle_t handle) {
    if (!handle || handle->open_count == 0) return NEX_ERR_INVALID_ARG;

    if (handle->ops && handle->ops->close) {
        nex_err_t err = handle->ops->close(handle);
        if (err != NEX_OK) return err;
    }
    handle->open_count--;
    return NEX_OK;
}

int32_t nex_device_read(nex_device_handle_t handle, void *buf, size_t count) {
    if (!handle || !buf || !handle->ops || !handle->ops->read) return NEX_ERR_INVALID_ARG;
    return handle->ops->read(handle, buf, count);
}

int32_t nex_device_write(nex_device_handle_t handle, const void *buf, size_t count) {
    if (!handle || !buf || !handle->ops || !handle->ops->write) return NEX_ERR_INVALID_ARG;
    return handle->ops->write(handle, buf, count);
}

nex_err_t nex_device_ioctl(nex_device_handle_t handle, uint32_t cmd, void *arg) {
    if (!handle || !handle->ops || !handle->ops->ioctl) return NEX_ERR_NOT_SUPPORTED;
    return handle->ops->ioctl(handle, cmd, arg);
}

void nex_device_list(void) {
    nex_log_info(TAG, "Registered Devices:");
    nex_device_t *curr = s_device_list;
    while (curr) {
        nex_log_info(TAG, "  -> %s (opens: %u)", curr->name, (unsigned int)curr->open_count);
        curr = curr->next;
    }
}
