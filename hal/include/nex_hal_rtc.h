/**
 * @file nex_hal_rtc.h
 * @brief NexOS Hardware Abstraction Layer - RTC Interface
 */

#ifndef NEX_HAL_RTC_H
#define NEX_HAL_RTC_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint16_t year;
    uint8_t  month;
    uint8_t  day;
    uint8_t  hour;
    uint8_t  minute;
    uint8_t  second;
} nex_datetime_t;

nex_err_t nex_rtc_init(void);
nex_err_t nex_rtc_set_time(const nex_datetime_t *dt);
nex_err_t nex_rtc_get_time(nex_datetime_t *dt);

#ifdef __cplusplus
}
#endif

#endif /* NEX_HAL_RTC_H */
