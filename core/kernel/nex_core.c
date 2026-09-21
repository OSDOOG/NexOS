/**
 * @file nex_core.c
 * @brief NexOS Kernel Initialization, State Machine, and Panic Handler
 */

#include "nex_core.h"
#include "nex_scheduler.h"
#include "nex_memory.h"
#include "nex_timer.h"
#include "nex_capability.h"
#include "nex_device.h"
#include "nex_vfs.h"
#include "nex_log.h"
#include "nex_security.h"
#include "nex_arch.h"
#include <stdio.h>

#define TAG "CORE"

static nex_kernel_state_t s_kernel_state = NEX_STATE_UNINITIALIZED;

/* Target metadata supplied by Platform Support Package */
extern const char *g_nex_target_name;
extern const char *g_nex_arch_name;
extern nex_profile_t g_nex_system_profile;

nex_err_t nex_core_init(void) {
    s_kernel_state = NEX_STATE_INITIALIZING;

    /* 1. Logging subsystem */
    nex_log_init();
    nex_log_info(TAG, "========================================");
    nex_log_info(TAG, "   NexOS v%s Multi-Target RTOS", NEXOS_VERSION_STRING);
    nex_log_info(TAG, "========================================");

    /* 2. Architecture layer */
    nex_arch_init();

    /* 3. Device Manager */
    nex_device_manager_init();

    /* 4. Virtual Filesystem */
    nex_vfs_init();

    /* 5. Security */
    nex_security_init();

    /* 6. Software Timers */
    nex_timer_subsys_init();

    /* 7. Scheduler */
    nex_scheduler_init();

    /* Capability dump */
    nex_capability_dump();

    s_kernel_state = NEX_STATE_RUNNING;
    nex_log_info(TAG, "NexOS Core initialized successfully");
    return NEX_OK;
}

void nex_core_start(void) {
    nex_log_info(TAG, "Starting NexOS Scheduler dispatch loop...");
    nex_scheduler_start();
}

nex_kernel_state_t nex_core_get_state(void) {
    return s_kernel_state;
}

nex_err_t nex_core_get_info(nex_system_info_t *info) {
    if (!info) return NEX_ERR_INVALID_ARG;

    info->target_name = g_nex_target_name ? g_nex_target_name : "generic";
    info->arch_name = g_nex_arch_name ? g_nex_arch_name : "generic";
    info->profile = g_nex_system_profile;

    nex_mem_stats_t mem_stats;
    nex_memory_get_stats(&mem_stats);
    info->total_memory = mem_stats.total_bytes;
    info->free_memory = mem_stats.free_bytes;
    info->capabilities = nex_capability_get_all();

    return NEX_OK;
}

void nex_core_panic(const char *message, const char *file, int line) {
    s_kernel_state = NEX_STATE_PANIC;
    nex_arch_interrupt_disable();

    nex_log_error(TAG, "!!!!!!!!!!!!!!!! SYSTEM PANIC !!!!!!!!!!!!!!!!");
    nex_log_error(TAG, "Reason: %s", message ? message : "Unknown error");
    nex_log_error(TAG, "Location: %s:%d", file ? file : "unknown", line);
    nex_log_error(TAG, "Halting execution.");

    while (1) {
        nex_arch_wait_for_interrupt();
    }
}
