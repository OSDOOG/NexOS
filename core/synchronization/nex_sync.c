/**
 * @file nex_sync.c
 * @brief NexOS Synchronization Primitives Implementation
 */

#include "nex_sync.h"
#include "nex_memory.h"
#include "nex_arch.h"
#include "nex_scheduler.h"
#include "nex_timer.h"
#include <string.h>

/* ========================================================================== */
/* Mutex                                                                      */
/* ========================================================================== */

nex_err_t nex_mutex_create(nex_mutex_handle_t *handle) {
    if (!handle) return NEX_ERR_INVALID_ARG;
    nex_mutex_t *m = (nex_mutex_t *)nex_malloc(sizeof(nex_mutex_t));
    if (!m) return NEX_ERR_NO_MEM;

    m->locked = false;
    m->owner = NULL;
    m->recursion_count = 0;
    m->wait_list = NULL;

    *handle = m;
    return NEX_OK;
}

nex_err_t nex_mutex_lock(nex_mutex_handle_t handle, nex_time_ms_t timeout_ms) {
    if (!handle) return NEX_ERR_INVALID_ARG;
    nex_task_handle_t current = nex_task_get_current();

    uint32_t start = nex_time_get_ms();

    while (1) {
        uint32_t isr = nex_arch_interrupt_disable();
        if (!handle->locked) {
            handle->locked = true;
            handle->owner = current;
            handle->recursion_count = 1;
            nex_arch_interrupt_restore(isr);
            return NEX_OK;
        } else if (handle->owner == current) {
            handle->recursion_count++;
            nex_arch_interrupt_restore(isr);
            return NEX_OK;
        }
        nex_arch_interrupt_restore(isr);

        if (timeout_ms != NEX_WAIT_FOREVER) {
            if ((nex_time_get_ms() - start) >= timeout_ms) {
                return NEX_ERR_TIMEOUT;
            }
        }
        nex_task_sleep_ms(1);
    }
}

nex_err_t nex_mutex_unlock(nex_mutex_handle_t handle) {
    if (!handle) return NEX_ERR_INVALID_ARG;
    nex_task_handle_t current = nex_task_get_current();

    uint32_t isr = nex_arch_interrupt_disable();
    if (!handle->locked || handle->owner != current) {
        nex_arch_interrupt_restore(isr);
        return NEX_ERR_PERMISSION;
    }

    handle->recursion_count--;
    if (handle->recursion_count == 0) {
        handle->locked = false;
        handle->owner = NULL;
    }
    nex_arch_interrupt_restore(isr);
    return NEX_OK;
}

nex_err_t nex_mutex_destroy(nex_mutex_handle_t handle) {
    if (!handle) return NEX_ERR_INVALID_ARG;
    nex_free(handle);
    return NEX_OK;
}

/* ========================================================================== */
/* Semaphore                                                                  */
/* ========================================================================== */

nex_err_t nex_sem_create(uint32_t init_count, uint32_t max_count, nex_sem_handle_t *handle) {
    if (!handle || init_count > max_count || max_count == 0) return NEX_ERR_INVALID_ARG;
    nex_sem_t *s = (nex_sem_t *)nex_malloc(sizeof(nex_sem_t));
    if (!s) return NEX_ERR_NO_MEM;

    s->count = init_count;
    s->max_count = max_count;
    s->wait_list = NULL;

    *handle = s;
    return NEX_OK;
}

nex_err_t nex_sem_wait(nex_sem_handle_t handle, nex_time_ms_t timeout_ms) {
    if (!handle) return NEX_ERR_INVALID_ARG;

    uint32_t start = nex_time_get_ms();

    while (1) {
        uint32_t isr = nex_arch_interrupt_disable();
        if (handle->count > 0) {
            handle->count--;
            nex_arch_interrupt_restore(isr);
            return NEX_OK;
        }
        nex_arch_interrupt_restore(isr);

        if (timeout_ms != NEX_WAIT_FOREVER) {
            if ((nex_time_get_ms() - start) >= timeout_ms) {
                return NEX_ERR_TIMEOUT;
            }
        }
        nex_task_sleep_ms(1);
    }
}

nex_err_t nex_sem_post(nex_sem_handle_t handle) {
    if (!handle) return NEX_ERR_INVALID_ARG;
    uint32_t isr = nex_arch_interrupt_disable();
    if (handle->count < handle->max_count) {
        handle->count++;
        nex_arch_interrupt_restore(isr);
        return NEX_OK;
    }
    nex_arch_interrupt_restore(isr);
    return NEX_ERR_OVERFLOW;
}

nex_err_t nex_sem_destroy(nex_sem_handle_t handle) {
    if (!handle) return NEX_ERR_INVALID_ARG;
    nex_free(handle);
    return NEX_OK;
}

/* ========================================================================== */
/* Event Flags                                                                */
/* ========================================================================== */

nex_err_t nex_event_group_create(nex_event_group_handle_t *handle) {
    if (!handle) return NEX_ERR_INVALID_ARG;
    nex_event_group_t *eg = (nex_event_group_t *)nex_malloc(sizeof(nex_event_group_t));
    if (!eg) return NEX_ERR_NO_MEM;

    eg->flags = 0;
    eg->wait_list = NULL;

    *handle = eg;
    return NEX_OK;
}

nex_err_t nex_event_group_set_bits(nex_event_group_handle_t handle, uint32_t bits) {
    if (!handle) return NEX_ERR_INVALID_ARG;
    uint32_t isr = nex_arch_interrupt_disable();
    handle->flags |= bits;
    nex_arch_interrupt_restore(isr);
    return NEX_OK;
}

nex_err_t nex_event_group_clear_bits(nex_event_group_handle_t handle, uint32_t bits) {
    if (!handle) return NEX_ERR_INVALID_ARG;
    uint32_t isr = nex_arch_interrupt_disable();
    handle->flags &= ~bits;
    nex_arch_interrupt_restore(isr);
    return NEX_OK;
}

nex_err_t nex_event_group_wait_bits(nex_event_group_handle_t handle,
                                    uint32_t bits_to_wait,
                                    uint32_t wait_mode,
                                    uint32_t *ret_bits,
                                    nex_time_ms_t timeout_ms) {
    if (!handle || bits_to_wait == 0) return NEX_ERR_INVALID_ARG;
    uint32_t start = nex_time_get_ms();

    while (1) {
        uint32_t isr = nex_arch_interrupt_disable();
        bool condition_met = false;
        if (wait_mode & NEX_EVENT_WAIT_ALL) {
            condition_met = ((handle->flags & bits_to_wait) == bits_to_wait);
        } else {
            condition_met = ((handle->flags & bits_to_wait) != 0);
        }

        if (condition_met) {
            uint32_t current = handle->flags;
            if (wait_mode & NEX_EVENT_CLEAR_ON_EXIT) {
                handle->flags &= ~bits_to_wait;
            }
            nex_arch_interrupt_restore(isr);
            if (ret_bits) *ret_bits = current;
            return NEX_OK;
        }
        nex_arch_interrupt_restore(isr);

        if (timeout_ms != NEX_WAIT_FOREVER) {
            if ((nex_time_get_ms() - start) >= timeout_ms) {
                return NEX_ERR_TIMEOUT;
            }
        }
        nex_task_sleep_ms(1);
    }
}

nex_err_t nex_event_group_destroy(nex_event_group_handle_t handle) {
    if (!handle) return NEX_ERR_INVALID_ARG;
    nex_free(handle);
    return NEX_OK;
}
