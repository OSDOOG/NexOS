/**
 * @file nex_scheduler.c
 * @brief NexOS Multi-Priority Preemptive & Cooperative Scheduler Implementation
 */

#include "nex_scheduler.h"
#include "nex_arch.h"
#include "nex_memory.h"
#include "nex_timer.h"
#include "nex_log.h"
#include <string.h>

#define TAG "SCHED"

extern void nex_task_set_current_internal(nex_task_handle_t task);

static nex_task_t *s_ready_queues[NEX_TASK_MAX_PRIORITIES] = {NULL};
static nex_task_t *s_blocked_list = NULL;
static nex_task_t *s_idle_task = NULL;
static bool s_scheduler_running = false;
static uint32_t s_lock_nesting = 0;

static void idle_task_fn(void *arg) {
    (void)arg;
    while (1) {
        nex_arch_wait_for_interrupt();
    }
}

nex_err_t nex_scheduler_init(void) {
    for (int i = 0; i < NEX_TASK_MAX_PRIORITIES; i++) {
        s_ready_queues[i] = NULL;
    }
    s_blocked_list = NULL;
    s_scheduler_running = false;
    s_lock_nesting = 0;

    /* Create system idle task at lowest priority 0 */
    nex_err_t err = nex_task_create("idle", idle_task_fn, NULL, NEX_TASK_PRIORITY_LOWEST, 512, &s_idle_task);
    if (err != NEX_OK) {
        nex_log_error(TAG, "Failed to create idle task: %d", err);
        return err;
    }

    nex_log_info(TAG, "Scheduler subsystem initialized");
    return NEX_OK;
}

void nex_scheduler_start(void) {
    nex_task_t *first = nex_scheduler_select_next();
    if (!first) {
        first = s_idle_task;
    }
    s_scheduler_running = true;
    nex_task_set_current_internal(first);
    nex_log_info(TAG, "Scheduler starting with task '%s'", first->name);
    nex_arch_start_first_task(first);
}

void nex_scheduler_add_ready(nex_task_t *task) {
    if (!task) return;
    uint32_t isr = nex_arch_interrupt_disable();
    uint8_t prio = task->priority;

    task->state = NEX_TASK_READY;
    task->next = NULL;

    if (!s_ready_queues[prio]) {
        s_ready_queues[prio] = task;
        task->prev = NULL;
    } else {
        nex_task_t *curr = s_ready_queues[prio];
        while (curr->next) {
            curr = curr->next;
        }
        curr->next = task;
        task->prev = curr;
    }

    nex_arch_interrupt_restore(isr);
}

void nex_scheduler_remove_ready(nex_task_t *task) {
    if (!task) return;
    uint32_t isr = nex_arch_interrupt_disable();
    uint8_t prio = task->priority;

    if (task->prev) {
        task->prev->next = task->next;
    } else if (s_ready_queues[prio] == task) {
        s_ready_queues[prio] = task->next;
    }

    if (task->next) {
        task->next->prev = task->prev;
    }

    task->next = NULL;
    task->prev = NULL;

    nex_arch_interrupt_restore(isr);
}

nex_task_t *nex_scheduler_select_next(void) {
    /* Search from highest priority down to 0 */
    for (int p = NEX_TASK_MAX_PRIORITIES - 1; p >= 0; p--) {
        if (s_ready_queues[p]) {
            return s_ready_queues[p];
        }
    }
    return s_idle_task;
}

void nex_scheduler_tick(void) {
    /* Periodic tick handler */
    nex_tick_t now = nex_time_get_ms();
    nex_timer_process_ticks(now);

    /* Round robin ready tasks if not locked */
    if (s_scheduler_running && s_lock_nesting == 0) {
        nex_task_t *curr = nex_task_get_current();
        if (curr && curr != s_idle_task) {
            /* Rotate round-robin queue */
            uint8_t p = curr->priority;
            if (s_ready_queues[p] && s_ready_queues[p]->next) {
                nex_scheduler_remove_ready(curr);
                nex_scheduler_add_ready(curr);
                nex_task_yield();
            }
        }
    }
}

bool nex_scheduler_is_running(void) {
    return s_scheduler_running;
}

void nex_scheduler_lock(void) {
    s_lock_nesting++;
}

void nex_scheduler_unlock(void) {
    if (s_lock_nesting > 0) {
        s_lock_nesting--;
    }
}
