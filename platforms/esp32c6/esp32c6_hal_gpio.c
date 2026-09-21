/**
 * @file esp32c6_hal_gpio.c
 * @brief ESP32-C6 Platform Hardware Abstraction Layer - GPIO Implementation
 *
 * Hardware register operations are strictly confined within this platform file.
 */

#include "nex_hal_gpio.h"
#include "nex_log.h"

#define TAG "ESP32C6_GPIO"

/* ESP32-C6 GPIO Register Base */
#define ESP32C6_GPIO_BASE       (0x60091000UL)
#define ESP32C6_GPIO_OUT_REG    (*(volatile uint32_t *)(ESP32C6_GPIO_BASE + 0x0004))
#define ESP32C6_GPIO_OUT_W1TS   (*(volatile uint32_t *)(ESP32C6_GPIO_BASE + 0x0008))
#define ESP32C6_GPIO_OUT_W1TC   (*(volatile uint32_t *)(ESP32C6_GPIO_BASE + 0x000C))
#define ESP32C6_GPIO_ENABLE_REG (*(volatile uint32_t *)(ESP32C6_GPIO_BASE + 0x0020))
#define ESP32C6_GPIO_ENABLE_W1TS(*(volatile uint32_t *)(ESP32C6_GPIO_BASE + 0x0024))
#define ESP32C6_GPIO_ENABLE_W1TC(*(volatile uint32_t *)(ESP32C6_GPIO_BASE + 0x0028))
#define ESP32C6_GPIO_IN_REG     (*(volatile uint32_t *)(ESP32C6_GPIO_BASE + 0x003C))

#define ESP32C6_MAX_PINS        (31)

static uint32_t s_pin_output_state = 0;

nex_err_t nex_gpio_init(void) {
    nex_log_info(TAG, "ESP32-C6 GPIO subsystem initialized");
    return NEX_OK;
}

nex_err_t nex_gpio_mode(nex_pin_t pin, nex_pin_mode_t mode) {
    if (pin >= ESP32C6_MAX_PINS) return NEX_ERR_INVALID_ARG;

#if defined(ESP_PLATFORM) || defined(__riscv)
    if (mode == NEX_PIN_OUTPUT || mode == NEX_PIN_OUTPUT_OPENDRAIN) {
        ESP32C6_GPIO_ENABLE_W1TS = (1UL << pin);
    } else {
        ESP32C6_GPIO_ENABLE_W1TC = (1UL << pin);
    }
#endif
    return NEX_OK;
}

nex_err_t nex_gpio_write(nex_pin_t pin, nex_level_t level) {
    if (pin >= ESP32C6_MAX_PINS) return NEX_ERR_INVALID_ARG;

    if (level == NEX_HIGH) {
        s_pin_output_state |= (1UL << pin);
#if defined(ESP_PLATFORM) || defined(__riscv)
        ESP32C6_GPIO_OUT_W1TS = (1UL << pin);
#endif
    } else {
        s_pin_output_state &= ~(1UL << pin);
#if defined(ESP_PLATFORM) || defined(__riscv)
        ESP32C6_GPIO_OUT_W1TC = (1UL << pin);
#endif
    }
    return NEX_OK;
}

nex_level_t nex_gpio_read(nex_pin_t pin) {
    if (pin >= ESP32C6_MAX_PINS) return NEX_LOW;

#if defined(ESP_PLATFORM) || defined(__riscv)
    return (ESP32C6_GPIO_IN_REG & (1UL << pin)) ? NEX_HIGH : NEX_LOW;
#else
    return (s_pin_output_state & (1UL << pin)) ? NEX_HIGH : NEX_LOW;
#endif
}

nex_err_t nex_gpio_toggle(nex_pin_t pin) {
    if (pin >= ESP32C6_MAX_PINS) return NEX_ERR_INVALID_ARG;
    nex_level_t cur = nex_gpio_read(pin);
    return nex_gpio_write(pin, cur == NEX_HIGH ? NEX_LOW : NEX_HIGH);
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
