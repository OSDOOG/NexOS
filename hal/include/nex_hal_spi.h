/**
 * @file nex_hal_spi.h
 * @brief NexOS Hardware Abstraction Layer - SPI Interface
 */

#ifndef NEX_HAL_SPI_H
#define NEX_HAL_SPI_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NEX_SPI_MODE0 = 0, /* CPOL=0, CPHA=0 */
    NEX_SPI_MODE1 = 1, /* CPOL=0, CPHA=1 */
    NEX_SPI_MODE2 = 2, /* CPOL=1, CPHA=0 */
    NEX_SPI_MODE3 = 3  /* CPOL=1, CPHA=1 */
} nex_spi_mode_t;

typedef struct {
    uint32_t clock_speed_hz;
    nex_spi_mode_t mode;
    bool msb_first;
    nex_pin_t sclk_pin;
    nex_pin_t mosi_pin;
    nex_pin_t miso_pin;
    nex_pin_t cs_pin;
} nex_spi_config_t;

nex_err_t nex_spi_init(uint8_t bus, const nex_spi_config_t *config);
nex_err_t nex_spi_transfer(uint8_t bus, const uint8_t *tx_buf, uint8_t *rx_buf, size_t len);
nex_err_t nex_spi_write(uint8_t bus, const uint8_t *tx_buf, size_t len);
nex_err_t nex_spi_read(uint8_t bus, uint8_t *rx_buf, size_t len);
nex_err_t nex_spi_deinit(uint8_t bus);

#ifdef __cplusplus
}
#endif

#endif /* NEX_HAL_SPI_H */
