/**
 * @file app_format.h
 * @brief NexOS Application Package (.app) Binary Header Specification
 *
 * Fixed 128-byte header preceding the relocatable application binary payload.
 */

#ifndef APP_FORMAT_H
#define APP_FORMAT_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define NEX_APP_MAGIC_BYTES     "\x7FNEXAPP\x01"
#define NEX_APP_MAGIC_LEN       8
#define NEX_APP_FORMAT_VERSION  1
#define NEX_APP_HEADER_SIZE     128

/* Architecture identifiers */
#define NEX_ARCH_ID_RISCV32     1
#define NEX_ARCH_ID_XTENSA      2
#define NEX_ARCH_ID_ARM_M0      3
#define NEX_ARCH_ID_ARM_M4      4
#define NEX_ARCH_ID_AVR         5
#define NEX_ARCH_ID_HOST_X86_64 6

/* Chip identifiers */
#define NEX_CHIP_ID_ESP32C6     1
#define NEX_CHIP_ID_RP2040      2
#define NEX_CHIP_ID_ESP8266     3
#define NEX_CHIP_ID_ESP32       4
#define NEX_CHIP_ID_ESP32S3     5
#define NEX_CHIP_ID_STM32F4     6
#define NEX_CHIP_ID_ATMEGA328P  7
#define NEX_CHIP_ID_HOST        8

/* Permissions Bitmask */
#define NEX_APP_PERM_GPIO       (1U << 0)
#define NEX_APP_PERM_UART       (1U << 1)
#define NEX_APP_PERM_I2C        (1U << 2)
#define NEX_APP_PERM_SPI        (1U << 3)
#define NEX_APP_PERM_STORAGE    (1U << 4)
#define NEX_APP_PERM_NETWORK    (1U << 5)
#define NEX_APP_PERM_DISPLAY    (1U << 6)
#define NEX_APP_PERM_ADC        (1U << 7)

#pragma pack(push, 1)
typedef struct {
    uint8_t  magic[8];              /* 0x00: \x7FNEXAPP\x01 */
    uint16_t format_version;        /* 0x08: Package format version (1) */
    uint16_t abi_version;           /* 0x0A: NexOS ABI version (1) */
    uint16_t target_arch;           /* 0x0C: Target CPU Architecture */
    uint16_t target_chip;           /* 0x0E: Target Microcontroller SoC */
    uint8_t  min_nexos_ver[4];      /* 0x10: [major, minor, patch, 0] */
    char     app_name[32];          /* 0x14: Application name string */
    char     app_version[16];       /* 0x34: Semantic version string */
    uint32_t entry_offset;          /* 0x44: Entry offset from end of header */
    uint32_t code_size;             /* 0x48: Size of executable code (.text) */
    uint32_t data_size;             /* 0x4C: Size of initialized data (.data) */
    uint32_t bss_size;              /* 0x50: Size of zero-initialized BSS (.bss) */
    uint32_t stack_size;            /* 0x54: Stack requirement in bytes */
    uint32_t heap_size;             /* 0x58: Heap requirement in bytes */
    uint32_t permissions;           /* 0x5C: Permissions bitmask */
    uint8_t  checksum[32];          /* 0x60: SHA-256 hash of payload (code+data) */
} nex_app_header_t;
#pragma pack(pop)

#ifdef __cplusplus
}
#endif

#endif /* APP_FORMAT_H */
