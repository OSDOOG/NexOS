/**
 * @file main.c
 * @brief NexOS Example 03: Dynamic Hardware Capability Sensing & Telemetry
 *
 * Demonstrates nex_device_has(NEX_CAP_*) runtime capability checks
 * and graceful feature adaptation.
 */

#include "nexos.h"

#define TAG "SENSOR_MON"

void app_main(void) {
    nex_log_info(TAG, "Starting Sensor Monitor & Capability Inspector");

    /* 1. Check for ADC capability */
    if (nex_device_has(NEX_CAP_ADC)) {
        nex_log_info(TAG, "Target supports ADC! Reading analog sensor...");
        nex_adc_init(0, NEX_ADC_RES_12BIT);
        uint32_t mv = nex_adc_read_voltage_mv(0);
        nex_log_info(TAG, "Sensor Voltage: %u mV", (unsigned int)mv);
    } else {
        nex_log_warn(TAG, "Target DOES NOT support ADC. Using simulated values.");
    }

    /* 2. Check for WiFi capability */
    if (nex_device_has(NEX_CAP_WIFI)) {
        nex_log_info(TAG, "Target supports WiFi! Initializing telemetry network...");
        nex_wifi_init();
        nex_wifi_config_t cfg = { .ssid = "NexOS_Mesh", .password = "nexos2026" };
        nex_wifi_connect(&cfg);
    } else {
        nex_log_info(TAG, "No WiFi hardware on target. Storing telemetry locally.");
    }

    /* 3. Check for Display capability */
    if (nex_device_has(NEX_CAP_DISPLAY)) {
        nex_log_info(TAG, "Target supports Display! Updating screen...");
    } else {
        nex_log_info(TAG, "No display hardware attached.");
    }

    nex_log_info(TAG, "Capability inspection completed successfully.");
}
