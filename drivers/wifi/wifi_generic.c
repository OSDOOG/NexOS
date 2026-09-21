/**
 * @file wifi_generic.c
 * @brief NexOS Modular WiFi Driver: Generic / Host Simulation Adapter
 */

#include "nex_wifi_driver.h"
#include "nex_log.h"
#include <string.h>

#define TAG "WIFI_HOST"

static nex_net_status_t s_host_status = NEX_NET_DISCONNECTED;
static nex_ip_info_t s_host_ip = {
    .ip = {192, 168, 0, 100},
    .netmask = {255, 255, 255, 0},
    .gateway = {192, 168, 0, 1},
    .dns = {8, 8, 8, 8}
};

static nex_err_t host_wifi_init(void) {
    nex_log_info(TAG, "Host virtual network adapter initialized");
    return NEX_OK;
}

static nex_err_t host_wifi_connect(const nex_wifi_config_t *config) {
    if (!config) return NEX_ERR_INVALID_ARG;
    nex_log_info(TAG, "Host virtual WiFi attached to SSID: '%s'", config->ssid);
    s_host_status = NEX_NET_GOT_IP;
    return NEX_OK;
}

static nex_err_t host_wifi_disconnect(void) {
    s_host_status = NEX_NET_DISCONNECTED;
    nex_log_info(TAG, "Host virtual WiFi detached");
    return NEX_OK;
}

static nex_net_status_t host_wifi_get_status(void) {
    return s_host_status;
}

static nex_err_t host_wifi_get_ip(nex_ip_info_t *info) {
    if (!info) return NEX_ERR_INVALID_ARG;
    *info = s_host_ip;
    return NEX_OK;
}

const nex_wifi_driver_ops_t g_host_wifi_driver = {
    .init = host_wifi_init,
    .connect = host_wifi_connect,
    .disconnect = host_wifi_disconnect,
    .get_status = host_wifi_get_status,
    .get_ip = host_wifi_get_ip
};

nex_err_t nex_wifi_init(void) {
    return g_host_wifi_driver.init();
}

nex_err_t nex_wifi_connect(const nex_wifi_config_t *config) {
    return g_host_wifi_driver.connect(config);
}

nex_err_t nex_wifi_disconnect(void) {
    return g_host_wifi_driver.disconnect();
}

nex_net_status_t nex_wifi_get_status(void) {
    return g_host_wifi_driver.get_status();
}

nex_err_t nex_wifi_get_ip_info(nex_ip_info_t *info) {
    return g_host_wifi_driver.get_ip(info);
}

nex_err_t nex_wifi_register_event_cb(nex_net_event_cb_t cb, void *arg) {
    (void)cb;
    (void)arg;
    return NEX_OK;
}
