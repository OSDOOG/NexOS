/**
 * @file esp32c6_hal_timer.c
 * @brief ESP32-C6 Platform Hardware Abstraction Layer - SysTick & Timer
 */

#include "nex_hal_timer.h"
#include <stdint.h>

#define ESP32C6_SYSTIMER_BASE   (0x60023000UL)
#define ESP32C6_SYSTIMER_UNIT0_VALUE_LO (*(volatile uint32_t *)(ESP32C6_SYSTIMER_BASE + 0x0040))
#define ESP32C6_SYSTIMER_UNIT0_VALUE_HI (*(volatile uint32_t *)(ESP32C6_SYSTIMER_BASE + 0x0044))

static nex_hal_timer_isr_t s_timer_isr = NULL;
static void *s_timer_arg = NULL;
static uint64_t s_simulated_cycles = 0;

nex_err_t nex_hal_systick_init(uint32_t tick_rate_hz, nex_hal_timer_isr_t isr, void *arg) {
    (void)tick_rate_hz;
    s_timer_isr = isr;
    s_timer_arg = arg;
    return NEX_OK;
}

uint64_t nex_hal_get_cycles(void) {
#if defined(ESP_PLATFORM) || defined(__riscv)
    uint32_t hi = ESP32C6_SYSTIMER_UNIT0_VALUE_HI;
    uint32_t lo = ESP32C6_SYSTIMER_UNIT0_VALUE_LO;
    return (((uint64_t)hi) << 32) | lo;
#else
    s_simulated_cycles += 160000;
    return s_simulated_cycles;
#endif
}

void nex_hal_delay_us(uint32_t us) {
#if defined(__riscv)
    /* 160MHz clock -> 160 cycles per microsecond */
    uint64_t start = nex_hal_get_cycles();
    uint64_t cycles = (uint64_t)us * 160;
    while ((nex_hal_get_cycles() - start) < cycles);
#else
    (void)us;
#endif
}
