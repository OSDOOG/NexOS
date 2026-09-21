/**
 * @file nex_capability.h
 * @brief NexOS Hardware Capability Discovery and Query System
 */

#ifndef NEX_CAPABILITY_H
#define NEX_CAPABILITY_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Register platform capabilities at boot.
 * @param caps Bitmask of supported hardware capabilities.
 */
void nex_capability_register(nex_cap_t caps);

/**
 * @brief Query if target hardware supports specific capability bitmask.
 * @param cap Capability flag(s) to verify (e.g. NEX_CAP_WIFI).
 * @return true if ALL queried capabilities are supported, false otherwise.
 */
bool nex_device_has(nex_cap_t cap);

/**
 * @brief Get complete capability bitmask for current target.
 */
nex_cap_t nex_capability_get_all(void);

/**
 * @brief Return human-readable name of capability.
 */
const char *nex_capability_name(nex_cap_t single_cap);

/**
 * @brief Print capability diagnostic report to system log.
 */
void nex_capability_dump(void);

#ifdef __cplusplus
}
#endif

#endif /* NEX_CAPABILITY_H */
