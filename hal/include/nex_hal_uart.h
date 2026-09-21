/**
 * @file nex_hal_uart.h
 * @brief NexOS Hardware Abstraction Layer - UART Interface
 */

#ifndef NEX_HAL_UART_H
#define NEX_HAL_UART_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NEX_UART_PARITY_NONE = 0,
    NEX_UART_PARITY_EVEN = 1,
    NEX_UART_PARITY_ODD  = 2
} nex_uart_parity_t;

typedef enum {
    NEX_UART_STOP_1 = 1,
    NEX_UART_STOP_2 = 2
} nex_uart_stop_bits_t;

typedef struct {
    uint32_t baud_rate;
    uint8_t data_bits;
    nex_uart_parity_t parity;
    nex_uart_stop_bits_t stop_bits;
    nex_pin_t tx_pin;
    nex_pin_t rx_pin;
} nex_uart_config_t;

nex_err_t nex_uart_init(uint8_t port, const nex_uart_config_t *config);
nex_err_t nex_uart_write(uint8_t port, const uint8_t *data, size_t len);
nex_err_t nex_uart_read(uint8_t port, uint8_t *data, size_t len, size_t *received, nex_time_ms_t timeout_ms);
nex_err_t nex_uart_putc(uint8_t port, char c);
int       nex_uart_getc(uint8_t port);
nex_err_t nex_uart_flush(uint8_t port);

#ifdef __cplusplus
}
#endif

#endif /* NEX_HAL_UART_H */
