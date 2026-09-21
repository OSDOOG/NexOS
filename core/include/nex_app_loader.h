/**
 * @file nex_app_loader.h
 * @brief NexOS Kernel Application Loader and Lifecycle Manager
 *
 * Responsible for discovering, validating, loading, and executing
 * .app packages from MicroSD / storage into ESP32-C6 SRAM.
 */

#ifndef NEX_APP_LOADER_H
#define NEX_APP_LOADER_H

#include "nex_types.h"
#include "nex_task.h"
#include "../../tools/nexpack/app_format.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NEX_APP_STATE_UNLOADED  = 0,
    NEX_APP_STATE_LOADED    = 1,
    NEX_APP_STATE_RUNNING   = 2,
    NEX_APP_STATE_STOPPED   = 3,
    NEX_APP_STATE_ERROR     = 4
} nex_app_state_t;

typedef struct nex_loaded_app {
    nex_app_header_t header;
    nex_app_state_t state;
    uint8_t *sram_image;        /* Allocated SRAM memory region */
    uint32_t total_allocated;   /* Total bytes allocated */
    nex_task_handle_t task;     /* Task executing the application */
    int exit_code;
    struct nex_loaded_app *next;
} nex_loaded_app_t;

typedef nex_loaded_app_t* nex_app_handle_t;

/**
 * @brief Initialize the application loader subsystem.
 */
nex_err_t nex_app_loader_init(void);

/**
 * @brief Validate an .app file header and payload without loading.
 * @param buffer In-memory file content buffer.
 * @param file_size Total size of file in bytes.
 * @return NEX_OK if valid, error code otherwise.
 */
nex_err_t nex_app_validate_image(const uint8_t *buffer, size_t file_size);

/**
 * @brief Load an .app file from memory/storage into execution SRAM.
 * @param buffer File content.
 * @param file_size File size.
 * @param app_handle Pointer to receive loaded application handle.
 */
nex_err_t nex_app_load_image(const uint8_t *buffer, size_t file_size, nex_app_handle_t *app_handle);

/**
 * @brief Start execution of a loaded application in an isolated task.
 */
nex_err_t nex_app_start(nex_app_handle_t app);

/**
 * @brief Terminate and unload an application, reclaiming SRAM.
 */
nex_err_t nex_app_unload(nex_app_handle_t app);

/**
 * @brief List all currently loaded/running applications.
 */
void nex_app_list_loaded(void);

#ifdef __cplusplus
}
#endif

#endif /* NEX_APP_LOADER_H */
