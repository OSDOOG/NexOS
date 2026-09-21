/**
 * @file nex_timer.c
 * @brief NexOS Software Timer & Timing Implementation
 */

#include "nex_timer.h"
#include "nex_memory.h"
#include "nex_arch.h"
#include "nex_hal_timer.h"
#include "nex_task.h"
#include "nex_log.h"
#include <string.h>

#define TAG "TIMER"

static nex_timer_t *s_active_timers = NULL;
static volatile nex_time_ms_t s_system_ticks = 0;

/* Tick callback invoked by HAL SysTick ISR */
static void on_hal_systick(void *arg) {
    (void)arg;
    s_system_ticks++;
}

nex_err_t nex_timer_subsys_init(void) {
    s_active_timers = NULL;
    s_system_ticks = 0;
    /* Initialize HAL hardware SysTick at 1000Hz (1ms period) */
    nex_hal_systick_init(1000, on_hal_systick, NULL);
    nex_log_info(TAG, "Timer subsystem initialized (1000Hz SysTick)");
    return NEX_OK;
}

nex_err_t nex_timer_create(const char *name,
                           nex_time_ms_t period_ms,
                           nex_timer_mode_t mode,
                           nex_timer_cb_t callback,
                           void *arg,
                           nex_timer_handle_t *handle) {
    if (!callback || period_ms == 0 || !handle) return NEX_ERR_INVALID_ARG;

    nex_timer_t *t = (nex_timer_t *)nex_malloc(sizeof(nex_timer_t));
    if (!t) return NEX_ERR_NO_MEM;

    strncpy(t->name, name ? name : "tmr", 15);
    t->name[15] = '\0';
    t->period_ms = period_ms;
    t->mode = mode;
    t->callback = callback;
    t->arg = arg;
    t->active = false;
    t->target_tick = 0;
    t->next = NULL;

    *handle = t;
    return NEX_OK;
}

nex_err_t nex_timer_start(nex_timer_handle_t handle) {
    if (!handle) return NEX_ERR_INVALID_ARG;
    uint32_t isr = nex_arch_interrupt_disable();

    handle->target_tick = s_system_ticks + handle->period_ms;
    handle->active = true;

    /* Insert into active list */
    handle->next = s_active_timers;
    s_active_timers = handle;

    nex_arch_interrupt_restore(isr);
    return NEX_OK;
}

nex_err_t nex_timer_stop(nex_timer_handle_t handle) {
    if (!handle) return NEX_ERR_INVALID_ARG;
    uint32_t isr = nex_arch_interrupt_disable();

    handle->active = false;
    if (s_active_timers == handle) {
        s_active_timers = handle->next;
    } else {
        nex_timer_t *curr = s_active_timers;
        while (curr && curr->next) {
            if (curr->next == handle) {
                curr->next = handle->next;
                break;
            }
            curr = curr->next;
        }
    }

    nex_arch_interrupt_restore(isr);
    return NEX_OK;
}

nex_err_t nex_timer_destroy(nex_timer_handle_t handle) {
    if (!handle) return NEX_ERR_INVALID_ARG;
    nex_timer_stop(handle);
    nex_free(handle);
    return NEX_OK;
}

void nex_timer_process_ticks(nex_tick_t current_tick) {
    nex_timer_t *curr = s_active_timers;
    while (curr) {
        nex_timer_t *next = curr->next;
        if (curr->active && current_tick >= curr->target_tick) {
            if (curr->mode == NEX_TIMER_PERIODIC) {
                curr->target_tick = current_tick + curr->period_ms;
            } else {
                nex_timer_stop(curr);
            }
            if (curr->callback) {
                curr->callback(curr, curr->arg);
            }
        }
        curr = next;
    }
}

nex_time_ms_t nex_time_get_ms(void) {
    return s_system_ticks;
}

void nex_delay_ms(nex_time_ms_t ms) {
    if (nex_task_get_current()) {
        nex_task_sleep_ms(ms);
    } else {
        /* Busy wait if scheduler is not yet running */
        nex_time_ms_t start = s_system_ticks;
        while ((s_system_ticks - start) < ms) {
            nex_arch_wait_for_interrupt();
        }
    }
}

void nex_delay_us(nex_time_us_t us) {
    nex_hal_delay_us((uint32_t)us);
}
