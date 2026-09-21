/**
 * @file host_hal_timer.c
 * @brief Host PC Platform Hardware Abstraction Layer - SysTick & High Resolution Timer
 */

#include "nex_hal_timer.h"
#include <time.h>
#include <stdint.h>

#if defined(_WIN32)
#include <windows.h>
#else
#include <unistd.h>
#endif

static nex_hal_timer_isr_t s_timer_isr = NULL;
static void *s_timer_arg = NULL;

nex_err_t nex_hal_systick_init(uint32_t tick_rate_hz, nex_hal_timer_isr_t isr, void *arg) {
    (void)tick_rate_hz;
    s_timer_isr = isr;
    s_timer_arg = arg;
    return NEX_OK;
}

uint64_t nex_hal_get_cycles(void) {
#if defined(_WIN32)
    LARGE_INTEGER count;
    QueryPerformanceCounter(&count);
    return (uint64_t)count.QuadPart;
#else
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ((uint64_t)ts.tv_sec * 1000000000ULL) + ts.tv_nsec;
#endif
}

void nex_hal_delay_us(uint32_t us) {
#if defined(_WIN32)
    Sleep((us + 999) / 1000);
#else
    usleep(us);
#endif
}
