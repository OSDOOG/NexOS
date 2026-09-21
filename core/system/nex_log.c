/**
 * @file nex_log.c
 * @brief NexOS Unified Logging Subsystem
 */

#include "nex_log.h"
#include "nex_timer.h"
#include "nex_hal_uart.h"
#include <stdio.h>
#include <string.h>

#define MAX_SINKS 4
#define LOG_BUFFER_SIZE 256

static nex_log_level_t s_current_level = NEX_LOG_LEVEL_DEBUG;
static nex_log_sink_fn_t s_sinks[MAX_SINKS];
static size_t s_sink_count = 0;

/* Default sink: Outputs via HAL UART port 0 */
static void default_uart_sink(nex_log_level_t level, const char *tag, const char *msg) {
    const char *lvl_str = "INFO";
    switch (level) {
        case NEX_LOG_LEVEL_ERROR: lvl_str = "ERR "; break;
        case NEX_LOG_LEVEL_WARN:  lvl_str = "WARN"; break;
        case NEX_LOG_LEVEL_INFO:  lvl_str = "INFO"; break;
        case NEX_LOG_LEVEL_DEBUG: lvl_str = "DBUG"; break;
        default: break;
    }

    char line[320];
    uint32_t ms = nex_time_get_ms();
    int len = snprintf(line, sizeof(line), "[%7u ms] [%s] %s: %s\r\n", ms, lvl_str, tag ? tag : "SYS", msg);
    if (len > 0) {
        nex_uart_write(0, (const uint8_t *)line, (size_t)len);
    }
}

void nex_log_init(void) {
    s_sink_count = 0;
    nex_log_add_sink(default_uart_sink);
}

void nex_log_set_level(nex_log_level_t level) {
    s_current_level = level;
}

nex_log_level_t nex_log_get_level(void) {
    return s_current_level;
}

void nex_log_add_sink(nex_log_sink_fn_t sink) {
    if (sink && s_sink_count < MAX_SINKS) {
        s_sinks[s_sink_count++] = sink;
    }
}

void nex_log_write_va(nex_log_level_t level, const char *tag, const char *fmt, va_list args) {
    if (level > s_current_level || level == NEX_LOG_LEVEL_NONE) {
        return;
    }

    char buf[LOG_BUFFER_SIZE];
    vsnprintf(buf, sizeof(buf), fmt, args);

    for (size_t i = 0; i < s_sink_count; i++) {
        if (s_sinks[i]) {
            s_sinks[i](level, tag, buf);
        }
    }
}

void nex_log_write(nex_log_level_t level, const char *tag, const char *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    nex_log_write_va(level, tag, fmt, args);
    va_end(args);
}
