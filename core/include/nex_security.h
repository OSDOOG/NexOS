/**
 * @file nex_security.h
 * @brief NexOS Modular Security and Application Verification Subsystem
 */

#ifndef NEX_SECURITY_H
#define NEX_SECURITY_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NEX_PERM_NONE      = 0x00,
    NEX_PERM_GPIO      = (1U << 0),
    NEX_PERM_NETWORK   = (1U << 1),
    NEX_PERM_STORAGE   = (1U << 2),
    NEX_PERM_SYSTEM    = (1U << 3),
    NEX_PERM_ALL       = 0xFFFFFFFFU
} nex_permission_t;

typedef struct {
    uint32_t magic;
    uint32_t version;
    uint32_t payload_size;
    uint32_t crc32;
    uint8_t signature[64];
    uint32_t required_permissions;
} nex_app_header_t;

nex_err_t nex_security_init(void);
nex_err_t nex_security_verify_payload(const uint8_t *data, size_t len, uint32_t expected_crc);
bool nex_security_check_permission(uint32_t app_id, nex_permission_t requested_perm);
uint32_t nex_crc32(const uint8_t *data, size_t length);

#ifdef __cplusplus
}
#endif

#endif /* NEX_SECURITY_H */
