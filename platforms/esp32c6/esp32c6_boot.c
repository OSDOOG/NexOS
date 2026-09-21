/**
 * @file esp32c6_boot.c
 * @brief ESP32-C6 Platform Bootloader & Initialization Sequence
 */

#include "nex_core.h"
#include "nex_capability.h"
#include "nex_memory.h"
#include "nex_hal_gpio.h"
#include "nex_hal_uart.h"
#include "nex_log.h"

#define TAG "ESP32C6_BOOT"

/* Target metadata symbols */
const char *g_nex_target_name = "esp32-c6";
const char *g_nex_arch_name = "riscv32";
nex_profile_t g_nex_system_profile = NEX_PROFILE_ADVANCED;

/* Platform dedicated heap pool (128 KB for default pool) */
#define ESP32C6_HEAP_SIZE (128 * 1024)
static uint8_t s_esp32c6_heap[ESP32C6_HEAP_SIZE];

extern void app_main(void);

/**
 * @brief ESP32-C6 Entry Point
 */
void nex_platform_boot(void) {
    /* 1. Register ESP32-C6 platform capabilities */
    nex_cap_t caps = NEX_CAP_GPIO | NEX_CAP_UART | NEX_CAP_SPI | NEX_CAP_I2C |
                     NEX_CAP_PWM | NEX_CAP_ADC | NEX_CAP_TIMER | NEX_CAP_RTC |
                     NEX_CAP_WIFI | NEX_CAP_BLE | NEX_CAP_ZIGBEE | NEX_CAP_THREAD |
                     NEX_CAP_FLASH | NEX_CAP_CRYPTO_ACCEL | NEX_CAP_SECURE_BOOT |
                     NEX_CAP_OTA | NEX_CAP_DEEP_SLEEP;
    nex_capability_register(caps);

    /* 2. Initialize memory heap */
    nex_memory_init(s_esp32c6_heap, ESP32C6_HEAP_SIZE);

    /* 3. Initialize low-level HAL peripherals */
    nex_gpio_init();
    nex_uart_config_t uart_cfg = {
        .baud_rate = 115200,
        .data_bits = 8,
        .parity = NEX_UART_PARITY_NONE,
        .stop_bits = NEX_UART_STOP_1,
        .tx_pin = 16,
        .rx_pin = 17
    };
    nex_uart_init(0, &uart_cfg);

    /* 4. Bootstrap NexOS Core */
    nex_core_init();

    nex_log_info(TAG, "ESP32-C6 platform bootstrap complete. Launching application...");

    /* 5. Create main application task */
    nex_task_create("app_main", (nex_task_entry_t)app_main, NULL, NEX_TASK_PRIORITY_DEFAULT, 4096, NULL);

    /* 6. Start NexOS scheduler */
    nex_core_start();
}
