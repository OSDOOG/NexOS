/**
 * @file xtensa_arch.c
 * @brief NexOS Architecture Support: Xtensa (ESP32, ESP8266, ESP32-S3)
 */

#include "nex_arch.h"
#include "nex_log.h"
#include <string.h>

#define TAG "ARCH_XTENSA"

typedef struct {
    uint32_t pc;
    uint32_t ps;
    uint32_t a0;
    uint32_t a1;
    uint32_t a2; /* arg */
    uint32_t a3;
    uint32_t a4;
    uint32_t a5;
    uint32_t a6;
    uint32_t a7;
    uint32_t a8;
    uint32_t a9;
    uint32_t a10;
    uint32_t a11;
    uint32_t a12;
    uint32_t a13;
    uint32_t a14;
    uint32_t a15;
} xtensa_stack_frame_t;

void nex_arch_init(void) {
    nex_log_info(TAG, "Initializing Xtensa architecture subsystem");
}

uint32_t nex_arch_interrupt_disable(void) {
#if defined(__XTENSA__)
    uint32_t prev;
    __asm__ volatile ("rsil %0, 15" : "=a"(prev));
    return prev;
#else
    return 0;
#endif
}

void nex_arch_interrupt_restore(uint32_t state) {
#if defined(__XTENSA__)
    __asm__ volatile ("wsr %0, ps; rsync" :: "a"(state));
#else
    (void)state;
#endif
}

void nex_arch_interrupt_enable(void) {
#if defined(__XTENSA__)
    __asm__ volatile ("rsil a2, 0");
#endif
}

void *nex_arch_stack_init(void *stack_top, nex_task_entry_t entry, void *arg) {
    uint8_t *sp = (uint8_t *)stack_top;
    /* 16-byte alignment */
    sp = (uint8_t *)((uintptr_t)sp & ~((uintptr_t)0xF));
    sp -= sizeof(xtensa_stack_frame_t);

    xtensa_stack_frame_t *frame = (xtensa_stack_frame_t *)sp;
    memset(frame, 0, sizeof(xtensa_stack_frame_t));

    frame->pc = (uint32_t)(uintptr_t)entry;
    frame->ps = 0x00040020; /* User mode or WOE bit */
    frame->a2 = (uint32_t)(uintptr_t)arg;

    return sp;
}

void nex_arch_context_switch(nex_task_t *current, nex_task_t *next) {
    (void)current;
    (void)next;
}

void nex_arch_start_first_task(nex_task_t *task) {
    if (!task || !task->entry) return;
    task->state = NEX_TASK_RUNNING;
    task->entry(task->arg);
}

void nex_arch_wait_for_interrupt(void) {
#if defined(__XTENSA__)
    __asm__ volatile ("waiti 0");
#endif
}
