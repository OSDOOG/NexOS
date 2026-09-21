/**
 * @file nex_hal_power.h
 * @brief NexOS Hardware Abstraction Layer - Power & Reset Management
 */

#ifndef NEX_HAL_POWER_H
#define NEX_HAL_POWER_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NEX_RESET_UNKNOWN      = 0,
    NEX_RESET_POWERON      = 1,
    NEX_RESET_SOFTWARE     = 2,
    NEX_RESET_WATCHDOG     = 3,
    NEX_RESET_DEEPSLEEP    = 4,
    NEX_RESET_BROWNOUT     = 5
} nex_reset_reason_t;

typedef enum {
    NEX_SLEEP_LIGHT        = 1,
    NEX_SLEEP_DEEP         = 2
} nex_sleep_mode_t;

void nex_power_restart(void);
nex_reset_reason_t nex_power_get_reset_reason(void);
nex_err_t nex_power_sleep(nex_sleep_mode_t mode, nex_time_ms_t duration_ms);

#ifdef __cplusplus
}
#endif

#endif /* NEX_HAL_POWER_H */
