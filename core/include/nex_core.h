/**
 * @file nex_core.h
 * @brief NexOS Kernel State, Versioning, and Lifecycle Management
 */

#ifndef NEX_CORE_H
#define NEX_CORE_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define NEXOS_VERSION_MAJOR 1
#define NEXOS_VERSION_MINOR 0
#define NEXOS_VERSION_PATCH 0
#define NEXOS_VERSION_STRING "1.0.0"

typedef enum {
    NEX_STATE_UNINITIALIZED = 0,
    NEX_STATE_INITIALIZING  = 1,
    NEX_STATE_RUNNING       = 2,
    NEX_STATE_SUSPENDED     = 3,
    NEX_STATE_PANIC         = 4
} nex_kernel_state_t;

typedef struct {
    const char *target_name;
    const char *arch_name;
    nex_profile_t profile;
    uint32_t total_memory;
    uint32_t free_memory;
    nex_cap_t capabilities;
} nex_system_info_t;

/**
 * @brief Initialize NexOS Core kernel subsystems.
 * @return NEX_OK on success, error code otherwise.
 */
nex_err_t nex_core_init(void);

/**
 * @brief Start the NexOS kernel scheduler and enter operational state.
 * @note This function normally does not return.
 */
void nex_core_start(void);

/**
 * @brief Get the current kernel state.
 */
nex_kernel_state_t nex_core_get_state(void);

/**
 * @brief Retrieve system information and runtime metrics.
 */
nex_err_t nex_core_get_info(nex_system_info_t *info);

/**
 * @brief Trigger a system panic and display diagnostic details.
 */
void nex_core_panic(const char *message, const char *file, int line);

#define NEX_PANIC(msg) nex_core_panic((msg), __FILE__, __LINE__)

#ifdef __cplusplus
}
#endif

#endif /* NEX_CORE_H */
