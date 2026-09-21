/**
 * @file nex_hal_network.h
 * @brief NexOS Hardware Abstraction Layer - Network & WiFi Interface
 */

#ifndef NEX_HAL_NETWORK_H
#define NEX_HAL_NETWORK_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NEX_NET_DISCONNECTED = 0,
    NEX_NET_CONNECTING   = 1,
    NEX_NET_CONNECTED    = 2,
    NEX_NET_GOT_IP       = 3,
    NEX_NET_ERROR        = 4
} nex_net_status_t;

typedef struct {
    char ssid[33];
    char password[64];
    uint8_t channel;
} nex_wifi_config_t;

typedef struct {
    uint8_t ip[4];
    uint8_t netmask[4];
    uint8_t gateway[4];
    uint8_t dns[4];
} nex_ip_info_t;

typedef void (*nex_net_event_cb_t)(nex_net_status_t status, void *arg);

nex_err_t nex_wifi_init(void);
nex_err_t nex_wifi_connect(const nex_wifi_config_t *config);
nex_err_t nex_wifi_disconnect(void);
nex_net_status_t nex_wifi_get_status(void);
nex_err_t nex_wifi_get_ip_info(nex_ip_info_t *info);
nex_err_t nex_wifi_register_event_cb(nex_net_event_cb_t cb, void *arg);

#ifdef __cplusplus
}
#endif

#endif /* NEX_HAL_NETWORK_H */
