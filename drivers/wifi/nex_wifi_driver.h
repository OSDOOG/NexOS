/**
 * @file nex_wifi_driver.h
 * @brief NexOS Modular WiFi Driver Interface
 */

#ifndef NEX_WIFI_DRIVER_H
#define NEX_WIFI_DRIVER_H

#include "nex_types.h"
#include "nex_hal_network.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    nex_err_t (*init)(void);
    nex_err_t (*connect)(const nex_wifi_config_t *config);
    nex_err_t (*disconnect)(void);
    nex_net_status_t (*get_status)(void);
    nex_err_t (*get_ip)(nex_ip_info_t *info);
} nex_wifi_driver_ops_t;

nex_err_t nex_wifi_driver_register(const char *name, const nex_wifi_driver_ops_t *ops);

#ifdef __cplusplus
}
#endif

#endif /* NEX_WIFI_DRIVER_H */
