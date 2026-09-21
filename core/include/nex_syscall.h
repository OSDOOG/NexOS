/**
 * @file nex_syscall.h
 * @brief NexOS System Call Interface and Kernel Dispatch Vector (ABI v1)
 *
 * Defines the standard syscall numbers, signatures, and dispatch table.
 * All NexOS applications communicate with the kernel exclusively through
 * this hardware-independent syscall vector.
 */

#ifndef NEX_SYSCALL_H
#define NEX_SYSCALL_H

#include "nex_types.h"
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define NEX_ABI_VERSION 1

/* ========================================================================== */
/* System Call Numbers                                                        */
/* ========================================================================== */

#define SYS_LOG                 1
#define SYS_DELAY_MS            2
#define SYS_TIME_GET_MS         3
#define SYS_TASK_SLEEP_MS       4
#define SYS_TASK_YIELD          5
#define SYS_MALLOC              6
#define SYS_FREE                7
#define SYS_DEVICE_HAS          8

/* GPIO Syscalls (Guarded by NEX_PERM_GPIO) */
#define SYS_GPIO_MODE           10
#define SYS_GPIO_WRITE          11
#define SYS_GPIO_READ           12
#define SYS_GPIO_TOGGLE         13

/* UART Syscalls (Guarded by NEX_PERM_UART) */
#define SYS_UART_WRITE          20
#define SYS_UART_READ           21
#define SYS_UART_PUTC           22
#define SYS_UART_GETC           23

/* I2C Syscalls (Guarded by NEX_PERM_I2C) */
#define SYS_I2C_WRITE           30
#define SYS_I2C_READ            31

/* SPI Syscalls (Guarded by NEX_PERM_SPI) */
#define SYS_SPI_TRANSFER        40

/* Storage Syscalls (Guarded by NEX_PERM_STORAGE) */
#define SYS_STORAGE_READ        50
#define SYS_STORAGE_WRITE       51

/* Network Syscalls (Guarded by NEX_PERM_NETWORK) */
#define SYS_NET_CONNECT         60
#define SYS_NET_DISCONNECT      61
#define SYS_NET_STATUS          62

/* Application Lifecycle */
#define SYS_APP_EXIT            100

/* ========================================================================== */
/* Kernel Syscall Dispatch Table Structure                                    */
/* ========================================================================== */

typedef struct {
    uint32_t abi_version;
    uint32_t table_size;

    /* System / Utility */
    void        (*sys_log)(const char *tag, const char *msg);
    void        (*sys_delay_ms)(uint32_t ms);
    uint32_t    (*sys_time_get_ms)(void);
    void        (*sys_task_sleep_ms)(uint32_t ms);
    void        (*sys_task_yield)(void);
    void*       (*sys_malloc)(size_t size);
    void        (*sys_free)(void *ptr);
    bool        (*sys_device_has)(uint32_t cap);

    /* GPIO */
    nex_err_t   (*sys_gpio_mode)(uint32_t pin, uint32_t mode);
    nex_err_t   (*sys_gpio_write)(uint32_t pin, uint32_t level);
    uint32_t    (*sys_gpio_read)(uint32_t pin);
    nex_err_t   (*sys_gpio_toggle)(uint32_t pin);

    /* UART */
    nex_err_t   (*sys_uart_write)(uint8_t port, const uint8_t *data, size_t len);
    nex_err_t   (*sys_uart_read)(uint8_t port, uint8_t *data, size_t len, size_t *rcvd, uint32_t timeout);

    /* App exit */
    void        (*sys_app_exit)(int exit_code);
} nex_syscall_table_t;

/**
 * @brief Retrieve the kernel system call dispatch table.
 */
const nex_syscall_table_t *nex_syscall_get_table(void);

/**
 * @brief Initialize the kernel syscall subsystem.
 */
nex_err_t nex_syscall_init(void);

#ifdef __cplusplus
}
#endif

#endif /* NEX_SYSCALL_H */
