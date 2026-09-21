/**
 * @file host_arch.c
 * @brief NexOS Architecture Support: Host PC Simulation (Windows / Linux x86_64)
 */

#include "nex_arch.h"
#include "nex_log.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TAG "ARCH_HOST"

static volatile uint32_t s_interrupt_nesting = 0;

void nex_arch_init(void) {
    nex_log_info(TAG, "Initializing Host x86_64 simulation architecture");
}

uint32_t nex_arch_interrupt_disable(void) {
    uint32_t prev = s_interrupt_nesting;
    s_interrupt_nesting++;
    return prev;
}

void nex_arch_interrupt_restore(uint32_t state) {
    s_interrupt_nesting = state;
}

void nex_arch_interrupt_enable(void) {
    s_interrupt_nesting = 0;
}

void *nex_arch_stack_init(void *stack_top, nex_task_entry_t entry, void *arg) {
    (void)stack_top;
    (void)entry;
    (void)arg;
    return stack_top;
}

void nex_arch_context_switch(nex_task_t *current, nex_task_t *next) {
    (void)current;
    if (next && next->entry) {
        next->state = NEX_TASK_RUNNING;
    }
}

void nex_arch_start_first_task(nex_task_t *task) {
    if (!task || !task->entry) return;
    task->state = NEX_TASK_RUNNING;
    task->entry(task->arg);
}

void nex_arch_wait_for_interrupt(void) {
    /* Host simulation idle yield */
}
