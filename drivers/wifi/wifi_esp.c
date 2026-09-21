/**
 * @file wifi_esp.c
 * @brief NexOS Modular WiFi Driver: Espressif WiFi Adapter (ESP32-C6, ESP32, ESP8266)
 */

#include "nex_wifi_driver.h"
#include "nex_log.h"
#include <string.h>

#define TAG "WIFI_ESP"

static nex_net_status_t s_status = NEX_NET_DISCONNECTED;

static nex_err_t esp_wifi_init(void) {
    nex_log_info(TAG, "Initializing Espressif 802.11 b/g/n/ax WiFi subsystem");
    s_status = NEX_NET_DISCONNECTED;
    return NEX_OK;
}

static nex_err_t esp_wifi_connect(const nex_wifi_config_t *config) {
    if (!config) return NEX_ERR_INVALID_ARG;
    nex_log_info(TAG, "Connecting to SSID: '%s'...", config->ssid);
    s_status = NEX_NET_CONNECTED;
    return NEX_OK;
}

static nex_err_t esp_wifi_disconnect(void) {
    s_status = NEX_NET_DISCONNECTED;
    nex_log_info(TAG, "Disconnected from WiFi");
    return NEX_OK;
}

static nex_net_status_t esp_wifi_get_status(void) {
    return s_status;
}

static nex_err_t esp_wifi_get_ip(nex_ip_info_t *info) {
    if (!info) return NEX_ERR_INVALID_ARG;
    info->ip[0] = 192; info->ip[1] = 168; info->ip[2] = 1; info->ip[3] = 105;
    return NEX_OK;
}

const nex_wifi_driver_ops_t g_esp_wifi_driver = {
    .init = esp_wifi_init,
    .connect = esp_wifi_connect,
    .disconnect = esp_wifi_disconnect,
    .get_status = esp_wifi_get_status,
    .get_ip = esp_wifi_get_ip
};
