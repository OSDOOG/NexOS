/**
 * @file wifi_cyw43.c
 * @brief NexOS Modular WiFi Driver: CYW43439 Adapter (Raspberry Pi Pico W)
 */

#include "nex_wifi_driver.h"
#include "nex_log.h"

#define TAG "WIFI_CYW43"

static nex_net_status_t s_status = NEX_NET_DISCONNECTED;

static nex_err_t cyw43_wifi_init(void) {
    nex_log_info(TAG, "Initializing Infineon CYW43439 SPI Wireless Bus");
    return NEX_OK;
}

static nex_err_t cyw43_wifi_connect(const nex_wifi_config_t *config) {
    if (!config) return NEX_ERR_INVALID_ARG;
    nex_log_info(TAG, "Pico W joining AP: '%s'", config->ssid);
    s_status = NEX_NET_CONNECTED;
    return NEX_OK;
}

static nex_err_t cyw43_wifi_disconnect(void) {
    s_status = NEX_NET_DISCONNECTED;
    return NEX_OK;
}

static nex_net_status_t cyw43_wifi_get_status(void) {
    return s_status;
}

static nex_err_t cyw43_wifi_get_ip(nex_ip_info_t *info) {
    if (!info) return NEX_ERR_INVALID_ARG;
    info->ip[0] = 192; info->ip[1] = 168; info->ip[2] = 1; info->ip[3] = 42;
    return NEX_OK;
}

const nex_wifi_driver_ops_t g_cyw43_wifi_driver = {
    .init = cyw43_wifi_init,
    .connect = cyw43_wifi_connect,
    .disconnect = cyw43_wifi_disconnect,
    .get_status = cyw43_wifi_get_status,
    .get_ip = cyw43_wifi_get_ip
};
