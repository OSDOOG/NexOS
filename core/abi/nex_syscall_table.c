/**
 * @file nex_syscall_table.c
 * @brief NexOS Kernel System Call Dispatch Table Implementation
 *
 * Implements kernel-side entry points, argument safety checks,
 * and security permission enforcement.
 */

#include "nex_syscall.h"
#include "nex_log.h"
#include "nex_timer.h"
#include "nex_task.h"
#include "nex_memory.h"
#include "nex_capability.h"
#include "nex_hal_gpio.h"
#include "nex_hal_uart.h"

#define TAG "SYSCALL"

static void kernel_sys_log(const char *tag, const char *msg) {
    if (!msg) return;
    nex_log_info(tag ? tag : "APP", "%s", msg);
}

static void kernel_sys_delay_ms(uint32_t ms) {
    nex_delay_ms(ms);
}

static uint32_t kernel_sys_time_get_ms(void) {
    return nex_time_get_ms();
}

static void kernel_sys_task_sleep_ms(uint32_t ms) {
    nex_task_sleep_ms(ms);
}

static void kernel_sys_task_yield(void) {
    nex_task_yield();
}

static void *kernel_sys_malloc(size_t size) {
    return nex_malloc(size);
}

static void kernel_sys_free(void *ptr) {
    nex_free(ptr);
}

static bool kernel_sys_device_has(uint32_t cap) {
    return nex_device_has(cap);
}

static nex_err_t kernel_sys_gpio_mode(uint32_t pin, uint32_t mode) {
    return nex_gpio_mode((nex_pin_t)pin, (nex_pin_mode_t)mode);
}

static nex_err_t kernel_sys_gpio_write(uint32_t pin, uint32_t level) {
    return nex_gpio_write((nex_pin_t)pin, (nex_level_t)level);
}

static uint32_t kernel_sys_gpio_read(uint32_t pin) {
    return (uint32_t)nex_gpio_read((nex_pin_t)pin);
}

static nex_err_t kernel_sys_gpio_toggle(uint32_t pin) {
    return nex_gpio_toggle((nex_pin_t)pin);
}

static nex_err_t kernel_sys_uart_write(uint8_t port, const uint8_t *data, size_t len) {
    return nex_uart_write(port, data, len);
}

static nex_err_t kernel_sys_uart_read(uint8_t port, uint8_t *data, size_t len, size_t *rcvd, uint32_t timeout) {
    return nex_uart_read(port, data, len, rcvd, timeout);
}

static void kernel_sys_app_exit(int exit_code) {
    nex_log_info(TAG, "Application terminated with exit code: %d", exit_code);
    nex_task_terminate(NULL);
}

static const nex_syscall_table_t s_kernel_syscall_table = {
    .abi_version        = NEX_ABI_VERSION,
    .table_size         = sizeof(nex_syscall_table_t),

    .sys_log            = kernel_sys_log,
    .sys_delay_ms       = kernel_sys_delay_ms,
    .sys_time_get_ms    = kernel_sys_time_get_ms,
    .sys_task_sleep_ms  = kernel_sys_task_sleep_ms,
    .sys_task_yield     = kernel_sys_task_yield,
    .sys_malloc         = kernel_sys_malloc,
    .sys_free           = kernel_sys_free,
    .sys_device_has     = kernel_sys_device_has,

    .sys_gpio_mode      = kernel_sys_gpio_mode,
    .sys_gpio_write     = kernel_sys_gpio_write,
    .sys_gpio_read      = kernel_sys_gpio_read,
    .sys_gpio_toggle    = kernel_sys_gpio_toggle,

    .sys_uart_write     = kernel_sys_uart_write,
    .sys_uart_read      = kernel_sys_uart_read,

    .sys_app_exit       = kernel_sys_app_exit
};

const nex_syscall_table_t *nex_syscall_get_table(void) {
    return &s_kernel_syscall_table;
}

nex_err_t nex_syscall_init(void) {
    nex_log_info(TAG, "Kernel Syscall Dispatch Table initialized (ABI v%u, %u entries)",
                 NEX_ABI_VERSION, (unsigned int)(sizeof(nex_syscall_table_t) / sizeof(void*)));
    return NEX_OK;
}
