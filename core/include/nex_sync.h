/**
 * @file nex_sync.h
 * @brief NexOS Synchronization Primitives (Mutex, Semaphore, Event Flags)
 */

#ifndef NEX_SYNC_H
#define NEX_SYNC_H

#include "nex_types.h"
#include "nex_task.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ========================================================================== */
/* Mutex                                                                      */
/* ========================================================================== */

typedef struct nex_mutex {
    bool locked;
    nex_task_handle_t owner;
    uint32_t recursion_count;
    nex_task_t *wait_list;
} nex_mutex_t;

typedef nex_mutex_t* nex_mutex_handle_t;

nex_err_t nex_mutex_create(nex_mutex_handle_t *handle);
nex_err_t nex_mutex_lock(nex_mutex_handle_t handle, nex_time_ms_t timeout_ms);
nex_err_t nex_mutex_unlock(nex_mutex_handle_t handle);
nex_err_t nex_mutex_destroy(nex_mutex_handle_t handle);

/* ========================================================================== */
/* Semaphore                                                                  */
/* ========================================================================== */

typedef struct nex_sem {
    uint32_t count;
    uint32_t max_count;
    nex_task_t *wait_list;
} nex_sem_t;

typedef nex_sem_t* nex_sem_handle_t;

nex_err_t nex_sem_create(uint32_t init_count, uint32_t max_count, nex_sem_handle_t *handle);
nex_err_t nex_sem_wait(nex_sem_handle_t handle, nex_time_ms_t timeout_ms);
nex_err_t nex_sem_post(nex_sem_handle_t handle);
nex_err_t nex_sem_destroy(nex_sem_handle_t handle);

/* ========================================================================== */
/* Event Flags                                                                */
/* ========================================================================== */

typedef struct nex_event_group {
    uint32_t flags;
    nex_task_t *wait_list;
} nex_event_group_t;

typedef nex_event_group_t* nex_event_group_handle_t;

#define NEX_EVENT_WAIT_ANY  (0x00)
#define NEX_EVENT_WAIT_ALL  (0x01)
#define NEX_EVENT_CLEAR_ON_EXIT (0x02)

nex_err_t nex_event_group_create(nex_event_group_handle_t *handle);
nex_err_t nex_event_group_set_bits(nex_event_group_handle_t handle, uint32_t bits);
nex_err_t nex_event_group_clear_bits(nex_event_group_handle_t handle, uint32_t bits);
nex_err_t nex_event_group_wait_bits(nex_event_group_handle_t handle,
                                    uint32_t bits_to_wait,
                                    uint32_t wait_mode,
                                    uint32_t *ret_bits,
                                    nex_time_ms_t timeout_ms);
nex_err_t nex_event_group_destroy(nex_event_group_handle_t handle);

#ifdef __cplusplus
}
#endif

#endif /* NEX_SYNC_H */
