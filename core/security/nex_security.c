/**
 * @file nex_security.c
 * @brief NexOS Modular Security and Application Verification Implementation
 */

#include "nex_security.h"
#include "nex_log.h"
#include <string.h>

#define TAG "SECURITY"

uint32_t nex_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 1) {
                crc = (crc >> 1) ^ 0xEDB88320U;
            } else {
                crc >>= 1;
            }
        }
    }
    return ~crc;
}

nex_err_t nex_security_init(void) {
    nex_log_info(TAG, "Security subsystem initialized");
    return NEX_OK;
}

nex_err_t nex_security_verify_payload(const uint8_t *data, size_t len, uint32_t expected_crc) {
    if (!data || len == 0) return NEX_ERR_INVALID_ARG;
    uint32_t calc = nex_crc32(data, len);
    if (calc != expected_crc) {
        nex_log_error(TAG, "Payload CRC mismatch! Expected: 0x%08X, Computed: 0x%08X", (unsigned int)expected_crc, (unsigned int)calc);
        return NEX_ERR_CRC;
    }
    nex_log_info(TAG, "Payload verification succeeded (CRC: 0x%08X)", (unsigned int)calc);
    return NEX_OK;
}

bool nex_security_check_permission(uint32_t app_id, nex_permission_t requested_perm) {
    (void)app_id;
    (void)requested_perm;
    /* Default open sandbox policy, easily configurable */
    return true;
}
