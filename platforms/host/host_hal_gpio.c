/**
 * @file host_hal_gpio.c
 * @brief Host PC Platform Hardware Abstraction Layer - Simulated GPIO Implementation
 */

#include "nex_hal_gpio.h"
#include "nex_log.h"
#include <stdio.h>

#define TAG "HOST_GPIO"
#define HOST_MAX_PINS 64

static nex_pin_mode_t s_pin_modes[HOST_MAX_PINS];
static nex_level_t    s_pin_levels[HOST_MAX_PINS];

nex_err_t nex_gpio_init(void) {
    for (int i = 0; i < HOST_MAX_PINS; i++) {
        s_pin_modes[i] = NEX_PIN_INPUT;
        s_pin_levels[i] = NEX_LOW;
    }
    nex_log_info(TAG, "Host virtual GPIO subsystem initialized (64 virtual pins)");
    return NEX_OK;
}

nex_err_t nex_gpio_mode(nex_pin_t pin, nex_pin_mode_t mode) {
    if (pin >= HOST_MAX_PINS) return NEX_ERR_INVALID_ARG;
    s_pin_modes[pin] = mode;
    return NEX_OK;
}

nex_err_t nex_gpio_write(nex_pin_t pin, nex_level_t level) {
    if (pin >= HOST_MAX_PINS) return NEX_ERR_INVALID_ARG;
    if (s_pin_levels[pin] != level) {
        s_pin_levels[pin] = level;
        nex_log_debug(TAG, "PIN [%02u] -> %s", (unsigned int)pin, level == NEX_HIGH ? "HIGH (ON)" : "LOW (OFF)");
    }
    return NEX_OK;
}

nex_level_t nex_gpio_read(nex_pin_t pin) {
    if (pin >= HOST_MAX_PINS) return NEX_LOW;
    return s_pin_levels[pin];
}

nex_err_t nex_gpio_toggle(nex_pin_t pin) {
    if (pin >= HOST_MAX_PINS) return NEX_ERR_INVALID_ARG;
    return nex_gpio_write(pin, s_pin_levels[pin] == NEX_HIGH ? NEX_LOW : NEX_HIGH);
}

nex_err_t nex_gpio_attach_interrupt(nex_pin_t pin, nex_gpio_intr_type_t intr_type, nex_gpio_isr_t isr, void *arg) {
    (void)pin;
    (void)intr_type;
    (void)isr;
    (void)arg;
    return NEX_OK;
}

nex_err_t nex_gpio_detach_interrupt(nex_pin_t pin) {
    (void)pin;
    return NEX_OK;
}
