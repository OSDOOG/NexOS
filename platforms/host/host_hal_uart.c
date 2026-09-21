/**
 * @file host_hal_uart.c
 * @brief Host PC Platform Hardware Abstraction Layer - UART / Console Implementation
 */

#include "nex_hal_uart.h"
#include <stdio.h>
#include <string.h>

nex_err_t nex_uart_init(uint8_t port, const nex_uart_config_t *config) {
    (void)port;
    (void)config;
    return NEX_OK;
}

nex_err_t nex_uart_write(uint8_t port, const uint8_t *data, size_t len) {
    (void)port;
    if (!data || len == 0) return NEX_ERR_INVALID_ARG;

    for (size_t i = 0; i < len; i++) {
        putchar(data[i]);
    }
    fflush(stdout);
    return NEX_OK;
}

nex_err_t nex_uart_read(uint8_t port, uint8_t *data, size_t len, size_t *received, nex_time_ms_t timeout_ms) {
    (void)port;
    (void)timeout_ms;
    if (!data || len == 0) return NEX_ERR_INVALID_ARG;
    if (received) *received = 0;
    return NEX_OK;
}

nex_err_t nex_uart_putc(uint8_t port, char c) {
    uint8_t b = (uint8_t)c;
    return nex_uart_write(port, &b, 1);
}

int nex_uart_getc(uint8_t port) {
    (void)port;
    return getchar();
}

nex_err_t nex_uart_flush(uint8_t port) {
    (void)port;
    fflush(stdout);
    return NEX_OK;
}
