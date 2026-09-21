/**
 * @file nex_timer.h
 * @brief NexOS Software Timer & Tick Subsystem
 */

#ifndef NEX_TIMER_H
#define NEX_TIMER_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct nex_timer nex_timer_t;
typedef nex_timer_t* nex_timer_handle_t;
typedef void (*nex_timer_cb_t)(nex_timer_handle_t timer, void *arg);

typedef enum {
    NEX_TIMER_ONE_SHOT = 0,
    NEX_TIMER_PERIODIC = 1
} nex_timer_mode_t;

struct nex_timer {
    char name[16];
    nex_timer_mode_t mode;
    nex_time_ms_t period_ms;
    nex_tick_t target_tick;
    nex_timer_cb_t callback;
    void *arg;
    bool active;
    struct nex_timer *next;
};

/**
 * @brief Initialize software timer engine.
 */
nex_err_t nex_timer_subsys_init(void);

/**
 * @brief Create a software timer.
 */
nex_err_t nex_timer_create(const char *name,
                           nex_time_ms_t period_ms,
                           nex_timer_mode_t mode,
                           nex_timer_cb_t callback,
                           void *arg,
                           nex_timer_handle_t *handle);

/**
 * @brief Start or restart timer.
 */
nex_err_t nex_timer_start(nex_timer_handle_t handle);

/**
 * @brief Stop an active timer.
 */
nex_err_t nex_timer_stop(nex_timer_handle_t handle);

/**
 * @brief Destroy a timer.
 */
nex_err_t nex_timer_destroy(nex_timer_handle_t handle);

/**
 * @brief Process expired timers on system tick.
 */
void nex_timer_process_ticks(nex_tick_t current_tick);

/**
 * @brief Get elapsed milliseconds since system boot.
 */
nex_time_ms_t nex_time_get_ms(void);

/**
 * @brief Blocking delay in milliseconds.
 */
void nex_delay_ms(nex_time_ms_t ms);

/**
 * @brief Blocking delay in microseconds.
 */
void nex_delay_us(nex_time_us_t us);

#ifdef __cplusplus
}
#endif

#endif /* NEX_TIMER_H */
