/**
 * @file riscv_arch.c
 * @brief NexOS Architecture Support: RISC-V 32-bit (RV32IMC / ESP32-C6)
 */

#include "nex_arch.h"
#include "nex_log.h"
#include <string.h>

#define TAG "ARCH_RISCV"

/* RISC-V 32-bit Register Stack Frame (32 registers + mepc + mstatus) */
typedef struct {
    uint32_t mepc;
    uint32_t mstatus;
    uint32_t ra;      /* x1 */
    uint32_t t0;      /* x5 */
    uint32_t t1;      /* x6 */
    uint32_t t2;      /* x7 */
    uint32_t s0_fp;   /* x8 */
    uint32_t s1;      /* x9 */
    uint32_t a0;      /* x10 (arg) */
    uint32_t a1;      /* x11 */
    uint32_t a2;      /* x12 */
    uint32_t a3;      /* x13 */
    uint32_t a4;      /* x14 */
    uint32_t a5;      /* x15 */
    uint32_t a6;      /* x16 */
    uint32_t a7;      /* x17 */
    uint32_t s2;      /* x18 */
    uint32_t s3;      /* x19 */
    uint32_t s4;      /* x20 */
    uint32_t s5;      /* x21 */
    uint32_t s6;      /* x22 */
    uint32_t s7;      /* x23 */
    uint32_t s8;      /* x24 */
    uint32_t s9;      /* x25 */
    uint32_t s10;     /* x26 */
    uint32_t s11;     /* x27 */
    uint32_t t3;      /* x28 */
    uint32_t t4;      /* x29 */
    uint32_t t5;      /* x30 */
    uint32_t t6;      /* x31 */
} riscv_stack_frame_t;

void nex_arch_init(void) {
    nex_log_info(TAG, "Initializing RISC-V 32-bit architecture subsystem");
}

uint32_t nex_arch_interrupt_disable(void) {
#if defined(__riscv)
    uint32_t status;
    __asm__ volatile ("csrrci %0, mstatus, 8" : "=r"(status));
    return status;
#else
    return 0;
#endif
}

void nex_arch_interrupt_restore(uint32_t state) {
#if defined(__riscv)
    __asm__ volatile ("csrw mstatus, %0" :: "r"(state));
#else
    (void)state;
#endif
}

void nex_arch_interrupt_enable(void) {
#if defined(__riscv)
    __asm__ volatile ("csrsi mstatus, 8");
#endif
}

void *nex_arch_stack_init(void *stack_top, nex_task_entry_t entry, void *arg) {
    uint8_t *sp = (uint8_t *)stack_top;
    /* 16-byte alignment as per RISC-V ABI */
    sp = (uint8_t *)((uintptr_t)sp & ~((uintptr_t)0xF));
    sp -= sizeof(riscv_stack_frame_t);

    riscv_stack_frame_t *frame = (riscv_stack_frame_t *)sp;
    memset(frame, 0, sizeof(riscv_stack_frame_t));

    frame->mepc = (uint32_t)(uintptr_t)entry;
    frame->mstatus = 0x00001880; /* MPP=Machine mode, MPIE=1 */
    frame->a0 = (uint32_t)(uintptr_t)arg;
    frame->ra = 0; /* Task exit trap */

    return sp;
}

void nex_arch_context_switch(nex_task_t *current, nex_task_t *next) {
    (void)current;
    (void)next;
    /* Dispatched by platform trap/interrupt handler or ecall */
}

void nex_arch_start_first_task(nex_task_t *task) {
    if (!task || !task->entry) return;
    task->state = NEX_TASK_RUNNING;
    task->entry(task->arg);
}

void nex_arch_wait_for_interrupt(void) {
#if defined(__riscv)
    __asm__ volatile ("wfi");
#endif
}
