/**
 * @file nex_app_loader.c
 * @brief NexOS Kernel Application Loader & Runtime Implementation
 */

#include "nex_app_loader.h"
#include "nex_syscall.h"
#include "nex_memory.h"
#include "nex_task.h"
#include "nex_log.h"
#include "nex_security.h"
#include <string.h>

#define TAG "APP_LOADER"

static nex_loaded_app_t *s_apps_list = NULL;

nex_err_t nex_app_loader_init(void) {
    s_apps_list = NULL;
    nex_log_info(TAG, "Application Loader subsystem initialized");
    return NEX_OK;
}

nex_err_t nex_app_validate_image(const uint8_t *buffer, size_t file_size) {
    if (!buffer || file_size < NEX_APP_HEADER_SIZE) {
        nex_log_error(TAG, "Image size %zu bytes is smaller than header (%d bytes)", file_size, NEX_APP_HEADER_SIZE);
        return NEX_ERR_INVALID_ARG;
    }

    const nex_app_header_t *hdr = (const nex_app_header_t *)buffer;

    /* 1. Magic check */
    if (memcmp(hdr->magic, NEX_APP_MAGIC_BYTES, NEX_APP_MAGIC_LEN) != 0) {
        nex_log_error(TAG, "Invalid magic bytes in application header");
        return NEX_ERR_INVALID_ARG;
    }

    /* 2. Format version check */
    if (hdr->format_version != NEX_APP_FORMAT_VERSION) {
        nex_log_error(TAG, "Unsupported package format version: %u", hdr->format_version);
        return NEX_ERR_NOT_SUPPORTED;
    }

    /* 3. ABI version check */
    if (hdr->abi_version != NEX_ABI_VERSION) {
        nex_log_error(TAG, "ABI version mismatch! Package: %u, Kernel: %u", hdr->abi_version, NEX_ABI_VERSION);
        return NEX_ERR_NOT_SUPPORTED;
    }

    /* 4. Target chip check (Allow ESP32-C6 or Host depending on active target) */
    if (hdr->target_chip != NEX_CHIP_ID_ESP32C6 && hdr->target_chip != NEX_CHIP_ID_HOST) {
        nex_log_warn(TAG, "Warning: Target chip ID %u may be incompatible", hdr->target_chip);
    }

    /* 5. Payload boundary check */
    size_t expected_size = NEX_APP_HEADER_SIZE + hdr->code_size + hdr->data_size;
    if (file_size < expected_size) {
        nex_log_error(TAG, "File truncated! Expected at least %zu bytes, got %zu", expected_size, file_size);
        return NEX_ERR_INVALID_ARG;
    }

    return NEX_OK;
}

static void app_task_entry(void *arg) {
    nex_loaded_app_t *app = (nex_loaded_app_t *)arg;
    if (!app || !app->sram_image) return;

    nex_log_info(TAG, "Executing application '%s' (v%s)...", app->header.app_name, app->header.app_version);

    /* Entry point function pointer: int (*entry)(const nex_syscall_table_t *table) */
    typedef int (*app_entry_fn)(const nex_syscall_table_t *table);
    app_entry_fn entry = (app_entry_fn)(app->sram_image + app->header.entry_offset);

    app->state = NEX_APP_STATE_RUNNING;
    int rc = entry(nex_syscall_get_table());
    app->exit_code = rc;
    app->state = NEX_APP_STATE_STOPPED;

    nex_log_info(TAG, "Application '%s' exited with code %d", app->header.app_name, rc);
}

nex_err_t nex_app_load_image(const uint8_t *buffer, size_t file_size, nex_app_handle_t *app_handle) {
    nex_err_t err = nex_app_validate_image(buffer, file_size);
    if (err != NEX_OK) return err;

    const nex_app_header_t *hdr = (const nex_app_header_t *)buffer;

    /* Calculate required SRAM for text + data + bss */
    uint32_t sram_needed = hdr->code_size + hdr->data_size + hdr->bss_size;
    if (sram_needed == 0) sram_needed = 64; /* Minimal stub */

    uint8_t *sram = (uint8_t *)nex_malloc(sram_needed);
    if (!sram) {
        nex_log_error(TAG, "Insufficient SRAM to allocate %u bytes for app payload", sram_needed);
        return NEX_ERR_NO_MEM;
    }

    /* Copy code + data payload */
    const uint8_t *payload = buffer + NEX_APP_HEADER_SIZE;
    memcpy(sram, payload, hdr->code_size + hdr->data_size);

    /* Zero out BSS section */
    if (hdr->bss_size > 0) {
        memset(sram + hdr->code_size + hdr->data_size, 0, hdr->bss_size);
    }

    nex_loaded_app_t *app = (nex_loaded_app_t *)nex_malloc(sizeof(nex_loaded_app_t));
    if (!app) {
        nex_free(sram);
        return NEX_ERR_NO_MEM;
    }

    memset(app, 0, sizeof(nex_loaded_app_t));
    app->header = *hdr;
    app->state = NEX_APP_STATE_LOADED;
    app->sram_image = sram;
    app->total_allocated = sram_needed;
    app->task = NULL;
    app->exit_code = 0;

    app->next = s_apps_list;
    s_apps_list = app;

    if (app_handle) *app_handle = app;

    nex_log_info(TAG, "Successfully loaded '%s': %u bytes code, %u bytes data, %u bytes BSS into SRAM (%p)",
                 hdr->app_name, hdr->code_size, hdr->data_size, hdr->bss_size, sram);

    return NEX_OK;
}

nex_err_t nex_app_start(nex_app_handle_t app) {
    if (!app || app->state != NEX_APP_STATE_LOADED) {
        return NEX_ERR_INVALID_ARG;
    }

    uint32_t stack = app->header.stack_size;
    if (stack < 1024) stack = 4096;

    nex_err_t err = nex_task_create(app->header.app_name,
                                    app_task_entry,
                                    app,
                                    NEX_TASK_PRIORITY_DEFAULT,
                                    stack,
                                    &app->task);
    if (err != NEX_OK) {
        nex_log_error(TAG, "Failed to create task for '%s': %d", app->header.app_name, err);
        return err;
    }

    return NEX_OK;
}

nex_err_t nex_app_unload(nex_app_handle_t app) {
    if (!app) return NEX_ERR_INVALID_ARG;

    if (app->task && app->state == NEX_APP_STATE_RUNNING) {
        nex_task_terminate(app->task);
    }

    if (app->sram_image) {
        nex_free(app->sram_image);
        app->sram_image = NULL;
    }

    /* Remove from loaded apps list */
    if (s_apps_list == app) {
        s_apps_list = app->next;
    } else {
        nex_loaded_app_t *curr = s_apps_list;
        while (curr && curr->next) {
            if (curr->next == app) {
                curr->next = app->next;
                break;
            }
            curr = curr->next;
        }
    }

    nex_log_info(TAG, "Unloaded application '%s' (reclaimed %u bytes SRAM)", app->header.app_name, app->total_allocated);
    nex_free(app);
    return NEX_OK;
}

void nex_app_list_loaded(void) {
    nex_log_info(TAG, "Loaded Applications in Memory:");
    nex_loaded_app_t *curr = s_apps_list;
    while (curr) {
        nex_log_info(TAG, "  * %-16s [v%-8s] State: %d, SRAM: %u bytes",
                     curr->header.app_name, curr->header.app_version, curr->state, curr->total_allocated);
        curr = curr->next;
    }
}
