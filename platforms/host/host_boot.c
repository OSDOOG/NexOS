/**
 * @file host_boot.c
 * @brief Host PC Platform Bootloader & Runtime Main
 */

#include "nex_core.h"
#include "nex_capability.h"
#include "nex_memory.h"
#include "nex_hal_gpio.h"
#include "nex_hal_uart.h"
#include "nex_log.h"
#include <stdio.h>
#include <stdlib.h>

#define TAG "HOST_BOOT"

const char *g_nex_target_name = "host";
const char *g_nex_arch_name = "x86_64";
nex_profile_t g_nex_system_profile = NEX_PROFILE_ADVANCED;

#define HOST_HEAP_SIZE (2 * 1024 * 1024) /* 2 MB heap */
static uint8_t s_host_heap[HOST_HEAP_SIZE];

extern void app_main(void);

void nex_platform_boot(void) {
    /* 1. Register Host capabilities */
    nex_cap_t caps = NEX_CAP_GPIO | NEX_CAP_UART | NEX_CAP_SPI | NEX_CAP_I2C |
                     NEX_CAP_PWM | NEX_CAP_ADC | NEX_CAP_DAC | NEX_CAP_TIMER |
                     NEX_CAP_RTC | NEX_CAP_WIFI | NEX_CAP_FLASH | NEX_CAP_DISPLAY |
                     NEX_CAP_SD | NEX_CAP_USB_DEVICE | NEX_CAP_OTA;
    nex_capability_register(caps);

    /* 2. Initialize memory heap */
    nex_memory_init(s_host_heap, HOST_HEAP_SIZE);

    /* 3. Initialize HAL */
    nex_gpio_init();
    nex_uart_config_t cfg = { .baud_rate = 115200 };
    nex_uart_init(0, &cfg);

    /* 4. Bootstrap Core */
    nex_core_init();

    nex_log_info(TAG, "Host PC simulation platform booted. Entering app_main...");

    /* 5. Launch app_main directly or via task */
    app_main();
}

int main(int argc, char **argv) {
    (void)argc;
    (void)argv;
    nex_platform_boot();
    return 0;
}
