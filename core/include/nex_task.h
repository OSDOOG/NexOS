/**
 * @file nex_task.h
 * @brief NexOS Task Control Block (TCB) and Task Lifecycle Management
 */

#ifndef NEX_TASK_H
#define NEX_TASK_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define NEX_TASK_MAX_NAME_LEN 16
#define NEX_TASK_PRIORITY_LOWEST  0
#define NEX_TASK_PRIORITY_DEFAULT 4
#define NEX_TASK_PRIORITY_HIGHEST 7
#define NEX_TASK_MAX_PRIORITIES   8

typedef enum {
    NEX_TASK_READY     = 0,
    NEX_TASK_RUNNING   = 1,
    NEX_TASK_BLOCKED   = 2,
    NEX_TASK_SUSPENDED = 3,
    NEX_TASK_TERMINATED= 4
} nex_task_state_t;

typedef void (*nex_task_entry_t)(void *arg);

typedef struct nex_task {
    uint32_t id;
    char name[NEX_TASK_MAX_NAME_LEN];
    nex_task_state_t state;
    uint8_t priority;
    nex_task_entry_t entry;
    void *arg;
    uint8_t *stack_base;
    uint32_t stack_size;
    void *sp;                     /* Stack pointer for architecture context */
    nex_tick_t wake_tick;         /* Sleep / delay wake tick */
    struct nex_task *next;
    struct nex_task *prev;
} nex_task_t;

typedef nex_task_t* nex_task_handle_t;

/**
 * @brief Create a new task.
 * @param name Task descriptive name.
 * @param entry Function entry point.
 * @param arg User argument passed to entry.
 * @param priority Task priority (0 = lowest, 7 = highest).
 * @param stack_size Stack allocation size in bytes.
 * @param handle Optional pointer to receive task handle.
 * @return NEX_OK on success.
 */
nex_err_t nex_task_create(const char *name,
                          nex_task_entry_t entry,
                          void *arg,
                          uint8_t priority,
                          uint32_t stack_size,
                          nex_task_handle_t *handle);

/**
 * @brief Terminate a task.
 * @param handle Task handle, or NULL to terminate current task.
 */
nex_err_t nex_task_terminate(nex_task_handle_t handle);

/**
 * @brief Suspend task execution.
 */
nex_err_t nex_task_suspend(nex_task_handle_t handle);

/**
 * @brief Resume a suspended task.
 */
nex_err_t nex_task_resume(nex_task_handle_t handle);

/**
 * @brief Get currently executing task.
 */
nex_task_handle_t nex_task_get_current(void);

/**
 * @brief Sleep current task for specified milliseconds.
 */
void nex_task_sleep_ms(nex_time_ms_t ms);

/**
 * @brief Yield execution to next ready task.
 */
void nex_task_yield(void);

#ifdef __cplusplus
}
#endif

#endif /* NEX_TASK_H */
