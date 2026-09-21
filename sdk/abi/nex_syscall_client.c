/**
 * @file nex_syscall_client.c
 * @brief Application-side System Call Dispatchers and Wrappers
 */

#include "nex_syscall_client.h"
#include <stdio.h>

const nex_syscall_table_t *g_nex_syscall_table = NULL;

/* User Application Entry Point Trampoline */
int _nex_app_start(const nex_syscall_table_t *table) {
    if (!table || table->abi_version != NEX_ABI_VERSION) {
        return -1;
    }
    g_nex_syscall_table = table;

    /* Invoke user app_main */
    app_main();

    if (g_nex_syscall_table && g_nex_syscall_table->sys_app_exit) {
        g_nex_syscall_table->sys_app_exit(0);
    }
    return 0;
}

/* User-facing SDK functions mapped via syscall table */

void nex_log(const char *msg) {
    if (g_nex_syscall_table && g_nex_syscall_table->sys_log) {
        g_nex_syscall_table->sys_log("APP", msg);
    }
}

void nex_log_app(const char *tag, const char *msg) {
    if (g_nex_syscall_table && g_nex_syscall_table->sys_log) {
        g_nex_syscall_table->sys_log(tag, msg);
    }
}

void nex_delay_ms_app(uint32_t ms) {
    if (g_nex_syscall_table && g_nex_syscall_table->sys_delay_ms) {
        g_nex_syscall_table->sys_delay_ms(ms);
    }
}

uint32_t nex_time_get_ms_app(void) {
    if (g_nex_syscall_table && g_nex_syscall_table->sys_time_get_ms) {
        return g_nex_syscall_table->sys_time_get_ms();
    }
    return 0;
}

void *nex_malloc_app(size_t size) {
    if (g_nex_syscall_table && g_nex_syscall_table->sys_malloc) {
        return g_nex_syscall_table->sys_malloc(size);
    }
    return NULL;
}

void nex_free_app(void *ptr) {
    if (g_nex_syscall_table && g_nex_syscall_table->sys_free) {
        g_nex_syscall_table->sys_free(ptr);
    }
}

nex_err_t nex_gpio_mode_app(uint32_t pin, uint32_t mode) {
    if (g_nex_syscall_table && g_nex_syscall_table->sys_gpio_mode) {
        return g_nex_syscall_table->sys_gpio_mode(pin, mode);
    }
    return NEX_ERR_NOT_INITIALIZED;
}

nex_err_t nex_gpio_write_app(uint32_t pin, uint32_t level) {
    if (g_nex_syscall_table && g_nex_syscall_table->sys_gpio_write) {
        return g_nex_syscall_table->sys_gpio_write(pin, level);
    }
    return NEX_ERR_NOT_INITIALIZED;
}

/* Standard aliases for unified app API */
nex_err_t nex_gpio_mode(nex_pin_t pin, nex_pin_mode_t mode) {
    return nex_gpio_mode_app((uint32_t)pin, (uint32_t)mode);
}

nex_err_t nex_gpio_write(nex_pin_t pin, nex_level_t level) {
    return nex_gpio_write_app((uint32_t)pin, (uint32_t)level);
}

void nex_delay_ms(nex_time_ms_t ms) {
    nex_delay_ms_app((uint32_t)ms);
}

bool nex_device_has(nex_cap_t cap) {
    if (g_nex_syscall_table && g_nex_syscall_table->sys_device_has) {
        return g_nex_syscall_table->sys_device_has((uint32_t)cap);
    }
    return false;
}

