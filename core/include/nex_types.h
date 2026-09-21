/**
 * @file nex_types.h
 * @brief NexOS Universal Types, Error Codes, and System Definitions
 *
 * This header defines hardware-independent primitives and error codes.
 * NexOS Core MUST NOT include any vendor or architecture-specific types.
 */

#ifndef NEX_TYPES_H
#define NEX_TYPES_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ========================================================================== */
/* Status and Error Codes                                                     */
/* ========================================================================== */

typedef int32_t nex_err_t;

#define NEX_OK                  (0)
#define NEX_FAIL                (-1)
#define NEX_ERR_INVALID_ARG     (-2)
#define NEX_ERR_NO_MEM          (-3)
#define NEX_ERR_TIMEOUT         (-4)
#define NEX_ERR_NOT_FOUND       (-5)
#define NEX_ERR_NOT_SUPPORTED   (-6)
#define NEX_ERR_BUSY            (-7)
#define NEX_ERR_ALREADY_EXISTS  (-8)
#define NEX_ERR_IO              (-9)
#define NEX_ERR_OVERFLOW        (-10)
#define NEX_ERR_UNDERFLOW       (-11)
#define NEX_ERR_PERMISSION      (-12)
#define NEX_ERR_NOT_INITIALIZED (-13)
#define NEX_ERR_CRC             (-14)

/* ========================================================================== */
/* Operating System Profiles                                                  */
/* ========================================================================== */

typedef enum {
    NEX_PROFILE_MICRO     = 1, /* For extremely constrained MCUs (AVR, <16KB RAM) */
    NEX_PROFILE_STANDARD  = 2, /* For general MCUs (ESP8266, RP2040, 64-256KB RAM) */
    NEX_PROFILE_ADVANCED  = 3  /* For capable MCUs (ESP32-C6, STM32F4, >256KB RAM) */
} nex_profile_t;

/* ========================================================================== */
/* Hardware Capability Bitmasks                                               */
/* ========================================================================== */

typedef uint32_t nex_cap_t;

#define NEX_CAP_NONE            (0x00000000U)
#define NEX_CAP_GPIO            (1U << 0)
#define NEX_CAP_UART            (1U << 1)
#define NEX_CAP_SPI             (1U << 2)
#define NEX_CAP_I2C             (1U << 3)
#define NEX_CAP_PWM             (1U << 4)
#define NEX_CAP_ADC             (1U << 5)
#define NEX_CAP_DAC             (1U << 6)
#define NEX_CAP_TIMER           (1U << 7)
#define NEX_CAP_RTC             (1U << 8)
#define NEX_CAP_WIFI            (1U << 9)
#define NEX_CAP_BLUETOOTH       (1U << 10)
#define NEX_CAP_BLE             (1U << 11)
#define NEX_CAP_ZIGBEE          (1U << 12)
#define NEX_CAP_THREAD          (1U << 13)
#define NEX_CAP_ETHERNET        (1U << 14)
#define NEX_CAP_USB_DEVICE      (1U << 15)
#define NEX_CAP_USB_HOST        (1U << 16)
#define NEX_CAP_SD              (1U << 17)
#define NEX_CAP_FLASH           (1U << 18)
#define NEX_CAP_DISPLAY         (1U << 19)
#define NEX_CAP_CRYPTO_ACCEL    (1U << 20)
#define NEX_CAP_SECURE_BOOT     (1U << 21)
#define NEX_CAP_OTA             (1U << 22)
#define NEX_CAP_DEEP_SLEEP      (1U << 23)

/* ========================================================================== */
/* Logic Levels & Pin Modes                                                   */
/* ========================================================================== */

typedef enum {
    NEX_LOW  = 0,
    NEX_HIGH = 1
} nex_level_t;

typedef enum {
    NEX_PIN_INPUT            = 0,
    NEX_PIN_OUTPUT           = 1,
    NEX_PIN_INPUT_PULLUP     = 2,
    NEX_PIN_INPUT_PULLDOWN   = 3,
    NEX_PIN_OUTPUT_OPENDRAIN = 4
} nex_pin_mode_t;

typedef uint32_t nex_pin_t;

/* ========================================================================== */
/* Time Constants and Types                                                   */
/* ========================================================================== */

typedef uint32_t nex_time_ms_t;
typedef uint64_t nex_time_us_t;
typedef uint32_t nex_tick_t;

#define NEX_WAIT_FOREVER        (0xFFFFFFFFU)
#define NEX_NO_WAIT             (0x00000000U)

#ifdef __cplusplus
}
#endif

#endif /* NEX_TYPES_H */
