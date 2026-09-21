/**
 * @file nex_hal_adc.h
 * @brief NexOS Hardware Abstraction Layer - ADC Interface
 */

#ifndef NEX_HAL_ADC_H
#define NEX_HAL_ADC_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NEX_ADC_RES_8BIT  = 8,
    NEX_ADC_RES_10BIT = 10,
    NEX_ADC_RES_12BIT = 12
} nex_adc_res_t;

nex_err_t nex_adc_init(uint8_t channel, nex_adc_res_t resolution);
uint32_t  nex_adc_read_raw(uint8_t channel);
uint32_t  nex_adc_read_voltage_mv(uint8_t channel);

#ifdef __cplusplus
}
#endif

#endif /* NEX_HAL_ADC_H */
