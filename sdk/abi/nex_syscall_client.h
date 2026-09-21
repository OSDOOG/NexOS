/**
 * @file nex_syscall_client.h
 * @brief NexOS Application-side Syscall Binding Interface
 */

#ifndef NEX_SYSCALL_CLIENT_H
#define NEX_SYSCALL_CLIENT_H

#include "../../core/include/nex_syscall.h"

#ifdef __cplusplus
extern "C" {
#endif

extern const nex_syscall_table_t *g_nex_syscall_table;

/**
 * @brief Application entry trampoline invoked by Kernel Application Loader.
 * @param table Pointer to kernel system call dispatch table.
 * @return Application return code.
 */
int _nex_app_start(const nex_syscall_table_t *table);

/**
 * @brief User application main entry point.
 */
void app_main(void);

#ifdef __cplusplus
}
#endif

#endif /* NEX_SYSCALL_CLIENT_H */
