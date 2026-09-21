/**
 * @file nex_hal_timer.h
 * @brief NexOS Hardware Abstraction Layer - Hardware Timer & SysTick
 */

#ifndef NEX_HAL_TIMER_H
#define NEX_HAL_TIMER_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*nex_hal_timer_isr_t)(void *arg);

/**
 * @brief Initialize hardware system tick timer.
 * @param tick_rate_hz Desired tick frequency (e.g., 1000 for 1ms tick).
 * @param isr Callback executed on each timer interrupt.
 */
nex_err_t nex_hal_systick_init(uint32_t tick_rate_hz, nex_hal_timer_isr_t isr, void *arg);

/**
 * @brief Get high-resolution hardware cycle count or microsecond counter.
 */
uint64_t  nex_hal_get_cycles(void);

/**
 * @brief High-precision hardware delay in microseconds.
 */
void      nex_hal_delay_us(uint32_t us);

#ifdef __cplusplus
}
#endif

#endif /* NEX_HAL_TIMER_H */
