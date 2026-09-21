/**
 * @file main.c
 * @brief NexOS Example 04: Interactive System Console Shell
 */

#include "nexos.h"
#include <stdio.h>
#include <string.h>

#define TAG "SHELL"

static void shell_exec_cmd(const char *cmd) {
    if (strcmp(cmd, "help") == 0) {
        nex_log_info(TAG, "Commands: help, info, caps, mem, reboot");
    } else if (strcmp(cmd, "info") == 0) {
        nex_system_info_t info;
        nex_core_get_info(&info);
        nex_log_info(TAG, "Target: %s, Arch: %s, Profile: %d", info.target_name, info.arch_name, info.profile);
    } else if (strcmp(cmd, "caps") == 0) {
        nex_capability_dump();
    } else if (strcmp(cmd, "mem") == 0) {
        nex_mem_stats_t stats;
        nex_memory_get_stats(&stats);
        nex_log_info(TAG, "Memory: total=%u, free=%u, min_free=%u", (unsigned int)stats.total_bytes, (unsigned int)stats.free_bytes, (unsigned int)stats.min_free_bytes);
    } else if (strcmp(cmd, "reboot") == 0) {
        nex_log_warn(TAG, "Rebooting target...");
        nex_power_restart();
    } else {
        nex_log_warn(TAG, "Unknown command: '%s'. Type 'help' for available commands.", cmd);
    }
}

void app_main(void) {
    nex_log_info(TAG, "==================================================");
    nex_log_info(TAG, "       NexOS Interactive Shell v1.0.0 Ready       ");
    nex_log_info(TAG, "==================================================");
    nex_log_info(TAG, "Type 'help', 'info', 'caps', or 'mem' into Serial Monitor and press Send.");

    // Display initial system state
    shell_exec_cmd("info");
    shell_exec_cmd("help");

    char cmd_buf[64];
    size_t cmd_len = 0;

    // Interactive Serial Command Loop
    while (1) {
        uint8_t byte_in = 0;
        size_t rx_count = 0;

        if (nex_uart_read(0, &byte_in, 1, &rx_count, 50) == NEX_OK && rx_count > 0) {
            if (byte_in == '\r' || byte_in == '\n') {
                if (cmd_len > 0) {
                    cmd_buf[cmd_len] = '\0';
                    shell_exec_cmd(cmd_buf);
                    cmd_len = 0;
                }
            } else if (cmd_len < sizeof(cmd_buf) - 1) {
                cmd_buf[cmd_len++] = (char)byte_in;
            }
        }
        nex_delay_ms(10);
    }
}
