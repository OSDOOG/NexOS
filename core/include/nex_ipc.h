/**
 * @file nex_ipc.h
 * @brief NexOS Inter-Process Communication (Ring Buffer, Message Queue)
 */

#ifndef NEX_IPC_H
#define NEX_IPC_H

#include "nex_types.h"
#include "nex_sync.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ========================================================================== */
/* Ring Buffer                                                                */
/* ========================================================================== */

typedef struct {
    uint8_t *buffer;
    size_t size;
    size_t head;
    size_t tail;
    size_t count;
} nex_ringbuf_t;

nex_err_t nex_ringbuf_init(nex_ringbuf_t *rb, uint8_t *storage, size_t size);
size_t nex_ringbuf_write(nex_ringbuf_t *rb, const uint8_t *data, size_t len);
size_t nex_ringbuf_read(nex_ringbuf_t *rb, uint8_t *data, size_t len);
size_t nex_ringbuf_available(const nex_ringbuf_t *rb);
size_t nex_ringbuf_free_space(const nex_ringbuf_t *rb);
void nex_ringbuf_clear(nex_ringbuf_t *rb);

/* ========================================================================== */
/* Message Queue                                                              */
/* ========================================================================== */

typedef struct nex_queue {
    uint8_t *buffer;
    size_t item_size;
    size_t capacity;
    size_t head;
    size_t tail;
    size_t count;
    nex_mutex_handle_t mutex;
    nex_sem_handle_t sem_items;
    nex_sem_handle_t sem_spaces;
} nex_queue_t;

typedef nex_queue_t* nex_queue_handle_t;

nex_err_t nex_queue_create(size_t item_size, size_t capacity, nex_queue_handle_t *handle);
nex_err_t nex_queue_send(nex_queue_handle_t handle, const void *item, nex_time_ms_t timeout_ms);
nex_err_t nex_queue_receive(nex_queue_handle_t handle, void *item, nex_time_ms_t timeout_ms);
size_t nex_queue_count(nex_queue_handle_t handle);
nex_err_t nex_queue_destroy(nex_queue_handle_t handle);

#ifdef __cplusplus
}
#endif

#endif /* NEX_IPC_H */
