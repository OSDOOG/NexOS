/**
 * @file nex_memory.h
 * @brief NexOS Heap & Slab Memory Allocator
 */

#ifndef NEX_MEMORY_H
#define NEX_MEMORY_H

#include "nex_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t total_bytes;
    uint32_t free_bytes;
    uint32_t min_free_bytes;
    uint32_t allocated_blocks;
} nex_mem_stats_t;

/**
 * @brief Initialize memory manager with a dedicated heap region.
 */
nex_err_t nex_memory_init(void *heap_start, size_t heap_size);

/**
 * @brief Allocate memory from kernel heap.
 */
void *nex_malloc(size_t size);

/**
 * @brief Free allocated memory.
 */
void nex_free(void *ptr);

/**
 * @brief Allocate cleared memory.
 */
void *nex_calloc(size_t nmemb, size_t size);

/**
 * @brief Reallocate memory buffer.
 */
void *nex_realloc(void *ptr, size_t new_size);

/**
 * @brief Retrieve heap statistics.
 */
void nex_memory_get_stats(nex_mem_stats_t *stats);

#ifdef __cplusplus
}
#endif

#endif /* NEX_MEMORY_H */
