/**
 * @file nex_task.c
 * @brief NexOS Task Control Block and Task Management Implementation
 */

#include "nex_task.h"
#include "nex_scheduler.h"
#include "nex_memory.h"
#include "nex_arch.h"
#include "nex_log.h"
#include <string.h>

#define TAG "TASK"

static uint32_t s_next_task_id = 1;
static nex_task_t *s_current_task = NULL;

nex_err_t nex_task_create(const char *name,
                          nex_task_entry_t entry,
                          void *arg,
                          uint8_t priority,
                          uint32_t stack_size,
                          nex_task_handle_t *handle) {
    if (!entry || stack_size < 128) {
        return NEX_ERR_INVALID_ARG;
    }

    if (priority >= NEX_TASK_MAX_PRIORITIES) {
        priority = NEX_TASK_MAX_PRIORITIES - 1;
    }

    nex_task_t *task = (nex_task_t *)nex_malloc(sizeof(nex_task_t));
    if (!task) {
        return NEX_ERR_NO_MEM;
    }

    uint8_t *stack = (uint8_t *)nex_malloc(stack_size);
    if (!stack) {
        nex_free(task);
        return NEX_ERR_NO_MEM;
    }

    memset(task, 0, sizeof(nex_task_t));
    task->id = s_next_task_id++;
    strncpy(task->name, name ? name : "task", NEX_TASK_MAX_NAME_LEN - 1);
    task->name[NEX_TASK_MAX_NAME_LEN - 1] = '\0';
    task->state = NEX_TASK_READY;
    task->priority = priority;
    task->entry = entry;
    task->arg = arg;
    task->stack_base = stack;
    task->stack_size = stack_size;

    void *stack_top = stack + stack_size;
    task->sp = nex_arch_stack_init(stack_top, entry, arg);

    nex_scheduler_add_ready(task);

    if (handle) {
        *handle = task;
    }

    nex_log_debug(TAG, "Created task '%s' (id=%u, prio=%u, stack=%u)", task->name, (unsigned int)task->id, priority, (unsigned int)stack_size);
    return NEX_OK;
}

nex_err_t nex_task_terminate(nex_task_handle_t handle) {
    nex_task_t *task = handle ? handle : s_current_task;
    if (!task) {
        return NEX_ERR_NOT_FOUND;
    }

    nex_scheduler_remove_ready(task);
    task->state = NEX_TASK_TERMINATED;

    if (task->stack_base) {
        nex_free(task->stack_base);
    }
    nex_free(task);

    if (task == s_current_task) {
        s_current_task = NULL;
        nex_task_yield();
    }
    return NEX_OK;
}

nex_err_t nex_task_suspend(nex_task_handle_t handle) {
    nex_task_t *task = handle ? handle : s_current_task;
    if (!task) return NEX_ERR_NOT_FOUND;

    nex_scheduler_remove_ready(task);
    task->state = NEX_TASK_SUSPENDED;

    if (task == s_current_task) {
        nex_task_yield();
    }
    return NEX_OK;
}

nex_err_t nex_task_resume(nex_task_handle_t handle) {
    if (!handle || handle->state != NEX_TASK_SUSPENDED) {
        return NEX_ERR_INVALID_ARG;
    }
    handle->state = NEX_TASK_READY;
    nex_scheduler_add_ready(handle);
    return NEX_OK;
}

nex_task_handle_t nex_task_get_current(void) {
    return s_current_task;
}

void nex_task_set_current_internal(nex_task_handle_t task) {
    s_current_task = task;
}

void nex_task_sleep_ms(nex_time_ms_t ms) {
    if (!s_current_task) return;
    nex_time_ms_t current = nex_time_get_ms();
    s_current_task->wake_tick = current + ms;
    s_current_task->state = NEX_TASK_BLOCKED;
    nex_scheduler_remove_ready(s_current_task);
    nex_task_yield();
}

void nex_task_yield(void) {
    if (nex_scheduler_is_running()) {
        nex_task_t *next = nex_scheduler_select_next();
        if (next && next != s_current_task) {
            nex_task_t *curr = s_current_task;
            s_current_task = next;
            nex_arch_context_switch(curr, next);
        }
    }
}
