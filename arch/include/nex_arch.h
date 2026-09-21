/**
 * @file nex_arch.h
 * @brief NexOS CPU Architecture Interface
 *
 * Defines CPU primitives, stack frame layouts, and context switching operations
 * for RISC-V, Xtensa, ARM Cortex-M, AVR, and Host simulators.
 */

#ifndef NEX_ARCH_H
#define NEX_ARCH_H

#include "nex_types.h"
#include "nex_task.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Initialize architecture-specific CPU features (e.g. traps, vectors).
 */
void nex_arch_init(void);

/**
 * @brief Disable interrupts globally and return previous state.
 */
uint32_t nex_arch_interrupt_disable(void);

/**
 * @brief Restore global interrupts from previously saved state.
 */
void nex_arch_interrupt_restore(uint32_t state);

/**
 * @brief Enable interrupts globally.
 */
void nex_arch_interrupt_enable(void);

/**
 * @brief Initialize task stack frame for context restoration.
 * @param stack_top Top of task stack memory.
 * @param entry Task entry function.
 * @param arg Argument passed to entry.
 * @return Updated stack pointer (sp) pointing to initial saved context.
 */
void *nex_arch_stack_init(void *stack_top, nex_task_entry_t entry, void *arg);

/**
 * @brief Trigger architecture context switch from current task to next.
 */
void nex_arch_context_switch(nex_task_t *current, nex_task_t *next);

/**
 * @brief Start first task on system boot.
 */
void nex_arch_start_first_task(nex_task_t *task);

/**
 * @brief Put CPU into low-power wait-for-interrupt state.
 */
void nex_arch_wait_for_interrupt(void);

#ifdef __cplusplus
}
#endif

#endif /* NEX_ARCH_H */
