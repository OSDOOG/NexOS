/**
 * @file avr_arch.c
 * @brief NexOS Architecture Support: AVR 8-bit (Arduino ATmega328P)
 */

#include "nex_arch.h"
#include "nex_log.h"
#include <string.h>

#define TAG "ARCH_AVR"

/* AVR 8-bit Register Context */
typedef struct {
    uint8_t  sreg;
    uint8_t  r0;
    uint8_t  r1;  /* Zero register */
    uint8_t  r2_r31[30];
    uint16_t pc;
} avr_stack_frame_t;

void nex_arch_init(void) {
    nex_log_info(TAG, "Initializing AVR 8-bit architecture subsystem");
}

uint32_t nex_arch_interrupt_disable(void) {
#if defined(__AVR__)
    uint8_t sreg = SREG;
    cli();
    return sreg;
#else
    return 0;
#endif
}

void nex_arch_interrupt_restore(uint32_t state) {
#if defined(__AVR__)
    SREG = (uint8_t)state;
#else
    (void)state;
#endif
}

void nex_arch_interrupt_enable(void) {
#if defined(__AVR__)
    sei();
#endif
}

void *nex_arch_stack_init(void *stack_top, nex_task_entry_t entry, void *arg) {
    uint8_t *sp = (uint8_t *)stack_top;
    (void)arg;

    /* Push return address (2 bytes for ATmega328P) */
    uint16_t pc = (uint16_t)(uintptr_t)entry;
    *sp-- = (uint8_t)(pc & 0xFF);
    *sp-- = (uint8_t)((pc >> 8) & 0xFF);

    /* Push registers and SREG */
    for (int i = 0; i < 33; i++) {
        *sp-- = 0x00;
    }

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
#if defined(__AVR__)
    __asm__ volatile ("sleep");
#endif
}
