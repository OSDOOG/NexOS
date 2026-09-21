/**
 * @file main.c
 * @brief NexOS Example 01: Universal Hardware-Independent Blinky
 *
 * This application is 100% portable across ESP32-C6, RP2040, ESP8266,
 * Arduino AVR, STM32, and Host Simulator without any source modification!
 */

#include "nexos.h"

#define TAG "BLINKY"
#define LED_PIN 15

void app_main(void) {
    nex_log_info(TAG, "Starting NexOS Blinky Demo");

    nex_gpio_mode(LED_PIN, NEX_PIN_OUTPUT);

    int count = 0;
    while (count < 10) {
        nex_log_info(TAG, "LED ON (count: %d)", count);
        nex_gpio_write(LED_PIN, NEX_HIGH);
        nex_delay_ms(500);

        nex_log_info(TAG, "LED OFF");
        nex_gpio_write(LED_PIN, NEX_LOW);
        nex_delay_ms(500);

        count++;
    }

    nex_log_info(TAG, "Blinky cycle complete. System running idle.");
}
