/**
 * @file nexos.h
 * @brief NexOS Universal Master SDK Header
 *
 * Include this single header in portable NexOS applications.
 * Exposes all standardized system, kernel, driver, and HAL interfaces.
 */

#ifndef NEXOS_H
#define NEXOS_H

#ifdef __cplusplus
extern "C" {
#endif

/* Core Types & System Info */
#include "../../core/include/nex_types.h"
#include "../../core/include/nex_core.h"
#include "../../core/include/nex_capability.h"

/* Multitasking & Synchronization */
#include "../../core/include/nex_task.h"
#include "../../core/include/nex_scheduler.h"
#include "../../core/include/nex_memory.h"
#include "../../core/include/nex_sync.h"
#include "../../core/include/nex_ipc.h"
#include "../../core/include/nex_timer.h"

/* Device Management & Filesystem */
#include "../../core/include/nex_device.h"
#include "../../core/include/nex_vfs.h"
#include "../../core/include/nex_log.h"
#include "../../core/include/nex_security.h"

/* Hardware Abstraction Layer (HAL) */
#include "../../hal/include/nex_hal_gpio.h"
#include "../../hal/include/nex_hal_uart.h"
#include "../../hal/include/nex_hal_spi.h"
#include "../../hal/include/nex_hal_i2c.h"
#include "../../hal/include/nex_hal_pwm.h"
#include "../../hal/include/nex_hal_adc.h"
#include "../../hal/include/nex_hal_timer.h"
#include "../../hal/include/nex_hal_rtc.h"
#include "../../hal/include/nex_hal_storage.h"
#include "../../hal/include/nex_hal_network.h"
#include "../../hal/include/nex_hal_power.h"

/* Application Logging Shortcut */
void nex_log(const char *msg);

/* Application Entry Point Declaration */
void app_main(void);

#ifdef __cplusplus
}
#endif

#endif /* NEXOS_H */
