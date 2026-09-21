/**
 * @file arm_arch.c
 * @brief NexOS Architecture Support: ARM Cortex-M (RP2040, STM32, nRF52)
 */

#include "nex_arch.h"
#include "nex_log.h"
#include <string.h>

#define TAG "ARCH_ARM"

typedef struct {
    /* Saved manually (software context) */
    uint32_t r4;
    uint32_t r5;
    uint32_t r6;
    uint32_t r7;
    uint32_t r8;
    uint32_t r9;
    uint32_t r10;
    uint32_t r11;
    /* Hardware auto-stacked frame */
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;
    uint32_t pc;
    uint32_t xpsr;
} arm_cortex_stack_frame_t;

void nex_arch_init(void) {
    nex_log_info(TAG, "Initializing ARM Cortex-M architecture subsystem");
}

uint32_t nex_arch_interrupt_disable(void) {
#if defined(__arm__)
    uint32_t result;
    __asm__ volatile ("mrs %0, primask\n cpsid i" : "=r" (result) :: "memory");
    return result;
#else
    return 0;
#endif
}

void nex_arch_interrupt_restore(uint32_t state) {
#if defined(__arm__)
    __asm__ volatile ("msr primask, %0" :: "r" (state) : "memory");
#else
    (void)state;
#endif
}

void nex_arch_interrupt_enable(void) {
#if defined(__arm__)
    __asm__ volatile ("cpsie i" : : : "memory");
#endif
}

void *nex_arch_stack_init(void *stack_top, nex_task_entry_t entry, void *arg) {
    uint8_t *sp = (uint8_t *)stack_top;
    /* 8-byte stack alignment for ARM AAPCS */
    sp = (uint8_t *)((uintptr_t)sp & ~((uintptr_t)0x7));
    sp -= sizeof(arm_cortex_stack_frame_t);

    arm_cortex_stack_frame_t *frame = (arm_cortex_stack_frame_t *)sp;
    memset(frame, 0, sizeof(arm_cortex_stack_frame_t));

    frame->r0 = (uint32_t)(uintptr_t)arg;
    frame->pc = (uint32_t)(uintptr_t)entry;
    frame->xpsr = 0x01000000; /* Thumb mode bit */
    frame->lr = 0xFFFFFFFD;   /* Return to Thread mode, use PSP */

    return sp;
}

void nex_arch_context_switch(nex_task_t *current, nex_task_t *next) {
    (void)current;
    (void)next;
    /* Trigger PendSV */
}

void nex_arch_start_first_task(nex_task_t *task) {
    if (!task || !task->entry) return;
    task->state = NEX_TASK_RUNNING;
    task->entry(task->arg);
}

void nex_arch_wait_for_interrupt(void) {
#if defined(__arm__)
    __asm__ volatile ("wfi");
#endif
}
