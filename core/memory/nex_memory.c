/**
 * @file nex_memory.c
 * @brief NexOS Kernel Heap & Memory Allocator Implementation
 */

#include "nex_memory.h"
#include "nex_log.h"
#include <string.h>

#define TAG "MEMORY"

#define NEX_MEM_ALIGN       (sizeof(void*))
#define NEX_MEM_ALIGN_UP(x) (((x) + (NEX_MEM_ALIGN - 1)) & ~(NEX_MEM_ALIGN - 1))

typedef struct mem_block {
    size_t size;             /* Block payload size */
    bool is_free;            /* Free flag */
    struct mem_block *next;  /* Next block in heap */
} mem_block_t;

#define BLOCK_HEADER_SIZE NEX_MEM_ALIGN_UP(sizeof(mem_block_t))

static uint8_t *s_heap_start = NULL;
static size_t   s_heap_size = 0;
static mem_block_t *s_first_block = NULL;
static nex_mem_stats_t s_stats = {0};

nex_err_t nex_memory_init(void *heap_start, size_t heap_size) {
    if (!heap_start || heap_size < (BLOCK_HEADER_SIZE * 2)) {
        return NEX_ERR_INVALID_ARG;
    }

    s_heap_start = (uint8_t *)heap_start;
    s_heap_size = heap_size;

    s_first_block = (mem_block_t *)s_heap_start;
    s_first_block->size = heap_size - BLOCK_HEADER_SIZE;
    s_first_block->is_free = true;
    s_first_block->next = NULL;

    s_stats.total_bytes = (uint32_t)heap_size;
    s_stats.free_bytes = (uint32_t)s_first_block->size;
    s_stats.min_free_bytes = s_stats.free_bytes;
    s_stats.allocated_blocks = 0;

    nex_log_info(TAG, "Heap initialized: %u bytes total", (unsigned int)heap_size);
    return NEX_OK;
}

void *nex_malloc(size_t size) {
    if (size == 0 || !s_first_block) {
        return NULL;
    }

    size_t aligned_size = NEX_MEM_ALIGN_UP(size);
    mem_block_t *curr = s_first_block;

    while (curr) {
        if (curr->is_free && curr->size >= aligned_size) {
            /* Check if block can be split */
            if (curr->size >= (aligned_size + BLOCK_HEADER_SIZE + 16)) {
                mem_block_t *new_block = (mem_block_t *)((uint8_t *)curr + BLOCK_HEADER_SIZE + aligned_size);
                new_block->size = curr->size - aligned_size - BLOCK_HEADER_SIZE;
                new_block->is_free = true;
                new_block->next = curr->next;

                curr->size = aligned_size;
                curr->next = new_block;
            }

            curr->is_free = false;
            s_stats.free_bytes -= (uint32_t)curr->size;
            s_stats.allocated_blocks++;
            if (s_stats.free_bytes < s_stats.min_free_bytes) {
                s_stats.min_free_bytes = s_stats.free_bytes;
            }

            return (void *)((uint8_t *)curr + BLOCK_HEADER_SIZE);
        }
        curr = curr->next;
    }

    nex_log_error(TAG, "Out of memory! Requested %u bytes, %u free", (unsigned int)size, s_stats.free_bytes);
    return NULL;
}

void nex_free(void *ptr) {
    if (!ptr || !s_first_block) return;

    mem_block_t *block = (mem_block_t *)((uint8_t *)ptr - BLOCK_HEADER_SIZE);
    if ((uint8_t *)block < s_heap_start || (uint8_t *)block >= (s_heap_start + s_heap_size)) {
        nex_log_error(TAG, "Invalid free pointer: %p", ptr);
        return;
    }

    block->is_free = true;
    s_stats.free_bytes += (uint32_t)block->size;
    if (s_stats.allocated_blocks > 0) {
        s_stats.allocated_blocks--;
    }

    /* Coalesce consecutive free blocks */
    mem_block_t *curr = s_first_block;
    while (curr && curr->next) {
        if (curr->is_free && curr->next->is_free) {
            curr->size += BLOCK_HEADER_SIZE + curr->next->size;
            curr->next = curr->next->next;
        } else {
            curr = curr->next;
        }
    }
}

void *nex_calloc(size_t nmemb, size_t size) {
    size_t total = nmemb * size;
    void *p = nex_malloc(total);
    if (p) {
        memset(p, 0, total);
    }
    return p;
}

void *nex_realloc(void *ptr, size_t new_size) {
    if (!ptr) return nex_malloc(new_size);
    if (new_size == 0) {
        nex_free(ptr);
        return NULL;
    }

    mem_block_t *block = (mem_block_t *)((uint8_t *)ptr - BLOCK_HEADER_SIZE);
    if (block->size >= new_size) {
        return ptr;
    }

    void *new_p = nex_malloc(new_size);
    if (new_p) {
        memcpy(new_p, ptr, block->size);
        nex_free(ptr);
    }
    return new_p;
}

void nex_memory_get_stats(nex_mem_stats_t *stats) {
    if (stats) {
        *stats = s_stats;
    }
}
