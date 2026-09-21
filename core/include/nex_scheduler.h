/**
 * @file nex_scheduler.h
 * @brief NexOS Priority-Based Multi-Task Scheduler
 */

#ifndef NEX_SCHEDULER_H
#define NEX_SCHEDULER_H

#include "nex_types.h"
#include "nex_task.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Initialize the scheduler subsystems and idle task.
 */
nex_err_t nex_scheduler_init(void);

/**
 * @brief Start the scheduler and dispatch highest priority ready task.
 */
void nex_scheduler_start(void);

/**
 * @brief Enqueue task into ready list according to priority.
 */
void nex_scheduler_add_ready(nex_task_t *task);

/**
 * @brief Remove task from ready list.
 */
void nex_scheduler_remove_ready(nex_task_t *task);

/**
 * @brief Select next task to run.
 */
nex_task_t *nex_scheduler_select_next(void);

/**
 * @brief Called on each system timer tick. Updates delay counters.
 */
void nex_scheduler_tick(void);

/**
 * @brief Check if scheduler is currently running.
 */
bool nex_scheduler_is_running(void);

/**
 * @brief Lock scheduler (disables preemption, interrupts remain enabled).
 */
void nex_scheduler_lock(void);

/**
 * @brief Unlock scheduler.
 */
void nex_scheduler_unlock(void);

#ifdef __cplusplus
}
#endif

#endif /* NEX_SCHEDULER_H */
