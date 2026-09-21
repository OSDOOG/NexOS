/**
 * @file nex_hal_gpio.h
 * @brief NexOS Hardware Abstraction Layer - GPIO Interface
 *
 * Provides a uniform, portable interface for digital general-purpose I/O.
 * Must be implemented by each Platform Support Package (PSP).
 */

#ifndef NEX_HAL_GPIO_H
#define NEX_HAL_GPIO_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NEX_GPIO_INTR_DISABLE = 0,
    NEX_GPIO_INTR_RISING  = 1,
    NEX_GPIO_INTR_FALLING = 2,
    NEX_GPIO_INTR_ANYEDGE = 3,
    NEX_GPIO_INTR_LOW     = 4,
    NEX_GPIO_INTR_HIGH    = 5
} nex_gpio_intr_type_t;

typedef void (*nex_gpio_isr_t)(nex_pin_t pin, void *arg);

/**
 * @brief Initialize the platform GPIO subsystem.
 */
nex_err_t nex_gpio_init(void);

/**
 * @brief Configure direction and pull resistors for a GPIO pin.
 */
nex_err_t nex_gpio_mode(nex_pin_t pin, nex_pin_mode_t mode);

/**
 * @brief Set the output state of a GPIO pin.
 */
nex_err_t nex_gpio_write(nex_pin_t pin, nex_level_t level);

/**
 * @brief Read the logical level of a GPIO pin.
 */
nex_level_t nex_gpio_read(nex_pin_t pin);

/**
 * @brief Toggle the state of an output GPIO pin.
 */
nex_err_t nex_gpio_toggle(nex_pin_t pin);

/**
 * @brief Attach an interrupt handler to a GPIO pin.
 */
nex_err_t nex_gpio_attach_interrupt(nex_pin_t pin, nex_gpio_intr_type_t intr_type, nex_gpio_isr_t isr, void *arg);

/**
 * @brief Detach an interrupt handler from a GPIO pin.
 */
nex_err_t nex_gpio_detach_interrupt(nex_pin_t pin);

#ifdef __cplusplus
}
#endif

#endif /* NEX_HAL_GPIO_H */
