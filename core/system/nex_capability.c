/**
 * @file nex_capability.c
 * @brief NexOS Hardware Capability Discovery and Query Implementation
 */

#include "nex_capability.h"
#include "nex_log.h"
#include <stdio.h>

#define TAG "CAPABILITY"

static nex_cap_t s_platform_capabilities = NEX_CAP_NONE;

void nex_capability_register(nex_cap_t caps) {
    s_platform_capabilities |= caps;
}

bool nex_device_has(nex_cap_t cap) {
    return (s_platform_capabilities & cap) == cap;
}

nex_cap_t nex_capability_get_all(void) {
    return s_platform_capabilities;
}

const char *nex_capability_name(nex_cap_t single_cap) {
    switch (single_cap) {
        case NEX_CAP_GPIO:         return "GPIO";
        case NEX_CAP_UART:         return "UART";
        case NEX_CAP_SPI:          return "SPI";
        case NEX_CAP_I2C:          return "I2C";
        case NEX_CAP_PWM:          return "PWM";
        case NEX_CAP_ADC:          return "ADC";
        case NEX_CAP_DAC:          return "DAC";
        case NEX_CAP_TIMER:        return "TIMER";
        case NEX_CAP_RTC:          return "RTC";
        case NEX_CAP_WIFI:         return "WiFi";
        case NEX_CAP_BLUETOOTH:    return "Bluetooth";
        case NEX_CAP_BLE:          return "BLE";
        case NEX_CAP_ZIGBEE:       return "Zigbee 802.15.4";
        case NEX_CAP_THREAD:       return "Thread";
        case NEX_CAP_ETHERNET:     return "Ethernet";
        case NEX_CAP_USB_DEVICE:   return "USB Device";
        case NEX_CAP_USB_HOST:     return "USB Host";
        case NEX_CAP_SD:           return "SD Card";
        case NEX_CAP_FLASH:        return "SPI Flash";
        case NEX_CAP_DISPLAY:      return "Display";
        case NEX_CAP_CRYPTO_ACCEL: return "Crypto Accelerator";
        case NEX_CAP_SECURE_BOOT:  return "Secure Boot";
        case NEX_CAP_OTA:          return "Over-The-Air Update";
        case NEX_CAP_DEEP_SLEEP:   return "Deep Sleep";
        default:                   return "Unknown";
    }
}

void nex_capability_dump(void) {
    nex_log_info(TAG, "Hardware Capabilities Active: 0x%08X", (unsigned int)s_platform_capabilities);
    for (uint32_t i = 0; i < 24; i++) {
        uint32_t bit = (1U << i);
        if (s_platform_capabilities & bit) {
            nex_log_info(TAG, "  [+] %s", nex_capability_name(bit));
        }
    }
}
