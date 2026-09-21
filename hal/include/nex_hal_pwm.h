/**
 * @file nex_hal_pwm.h
 * @brief NexOS Hardware Abstraction Layer - PWM Interface
 */

#ifndef NEX_HAL_PWM_H
#define NEX_HAL_PWM_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

nex_err_t nex_pwm_init(uint8_t channel, nex_pin_t pin, uint32_t freq_hz);
nex_err_t nex_pwm_set_duty(uint8_t channel, uint8_t duty_percent);
nex_err_t nex_pwm_start(uint8_t channel);
nex_err_t nex_pwm_stop(uint8_t channel);

#ifdef __cplusplus
}
#endif

#endif /* NEX_HAL_PWM_H */
