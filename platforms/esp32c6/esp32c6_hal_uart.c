/**
 * @file esp32c6_hal_uart.c
 * @brief ESP32-C6 Platform Hardware Abstraction Layer - UART Implementation
 */

#include "nex_hal_uart.h"
#include <stdio.h>
#include <string.h>

#define ESP32C6_UART0_BASE (0x60000000UL)
#define ESP32C6_UART0_FIFO (*(volatile uint32_t *)(ESP32C6_UART0_BASE + 0x0000))
#define ESP32C6_UART0_STATUS (*(volatile uint32_t *)(ESP32C6_UART0_BASE + 0x001C))

nex_err_t nex_uart_init(uint8_t port, const nex_uart_config_t *config) {
    (void)port;
    (void)config;
    return NEX_OK;
}

nex_err_t nex_uart_write(uint8_t port, const uint8_t *data, size_t len) {
    (void)port;
    if (!data || len == 0) return NEX_ERR_INVALID_ARG;

#if defined(ESP_PLATFORM) || defined(__riscv)
    for (size_t i = 0; i < len; i++) {
        /* Wait while TX FIFO is full */
        while (((ESP32C6_UART0_STATUS >> 16) & 0xFF) >= 120);
        ESP32C6_UART0_FIFO = data[i];
    }
#else
    for (size_t i = 0; i < len; i++) {
        putchar(data[i]);
    }
    fflush(stdout);
#endif
    return NEX_OK;
}

nex_err_t nex_uart_read(uint8_t port, uint8_t *data, size_t len, size_t *received, nex_time_ms_t timeout_ms) {
    (void)port;
    (void)timeout_ms;
    if (!data) return NEX_ERR_INVALID_ARG;
    if (received) *received = 0;
    return NEX_OK;
}

nex_err_t nex_uart_putc(uint8_t port, char c) {
    uint8_t b = (uint8_t)c;
    return nex_uart_write(port, &b, 1);
}

int nex_uart_getc(uint8_t port) {
    (void)port;
    return -1;
}

nex_err_t nex_uart_flush(uint8_t port) {
    (void)port;
    return NEX_OK;
}
