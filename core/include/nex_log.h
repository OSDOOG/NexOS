/**
 * @file nex_log.h
 * @brief NexOS Unified Multi-Sink Logging Interface
 */

#ifndef NEX_LOG_H
#define NEX_LOG_H

#include "nex_types.h"
#include <stdarg.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    NEX_LOG_LEVEL_NONE  = 0,
    NEX_LOG_LEVEL_ERROR = 1,
    NEX_LOG_LEVEL_WARN  = 2,
    NEX_LOG_LEVEL_INFO  = 3,
    NEX_LOG_LEVEL_DEBUG = 4
} nex_log_level_t;

typedef void (*nex_log_sink_fn_t)(nex_log_level_t level, const char *tag, const char *msg);

void nex_log_init(void);
void nex_log_set_level(nex_log_level_t level);
nex_log_level_t nex_log_get_level(void);
void nex_log_add_sink(nex_log_sink_fn_t sink);

void nex_log_write(nex_log_level_t level, const char *tag, const char *fmt, ...);
void nex_log_write_va(nex_log_level_t level, const char *tag, const char *fmt, va_list args);

#define nex_log_error(tag, ...) nex_log_write(NEX_LOG_LEVEL_ERROR, tag, __VA_ARGS__)
#define nex_log_warn(tag, ...)  nex_log_write(NEX_LOG_LEVEL_WARN,  tag, __VA_ARGS__)
#define nex_log_info(tag, ...)  nex_log_write(NEX_LOG_LEVEL_INFO,  tag, __VA_ARGS__)
#define nex_log_debug(tag, ...) nex_log_write(NEX_LOG_LEVEL_DEBUG, tag, __VA_ARGS__)

#ifdef __cplusplus
}
#endif

#endif /* NEX_LOG_H */
