/**
 * @file nex_ipc.c
 * @brief NexOS Inter-Process Communication Implementation (Ring Buffer & Message Queue)
 */

#include "nex_ipc.h"
#include "nex_memory.h"
#include "nex_arch.h"
#include "nex_timer.h"
#include <string.h>

/* ========================================================================== */
/* Ring Buffer                                                                */
/* ========================================================================== */

nex_err_t nex_ringbuf_init(nex_ringbuf_t *rb, uint8_t *storage, size_t size) {
    if (!rb || !storage || size == 0) return NEX_ERR_INVALID_ARG;
    rb->buffer = storage;
    rb->size = size;
    rb->head = 0;
    rb->tail = 0;
    rb->count = 0;
    return NEX_OK;
}

size_t nex_ringbuf_write(nex_ringbuf_t *rb, const uint8_t *data, size_t len) {
    if (!rb || !data || len == 0) return 0;
    uint32_t isr = nex_arch_interrupt_disable();

    size_t written = 0;
    while (written < len && rb->count < rb->size) {
        rb->buffer[rb->head] = data[written++];
        rb->head = (rb->head + 1) % rb->size;
        rb->count++;
    }

    nex_arch_interrupt_restore(isr);
    return written;
}

size_t nex_ringbuf_read(nex_ringbuf_t *rb, uint8_t *data, size_t len) {
    if (!rb || !data || len == 0) return 0;
    uint32_t isr = nex_arch_interrupt_disable();

    size_t read_bytes = 0;
    while (read_bytes < len && rb->count > 0) {
        data[read_bytes++] = rb->buffer[rb->tail];
        rb->tail = (rb->tail + 1) % rb->size;
        rb->count--;
    }

    nex_arch_interrupt_restore(isr);
    return read_bytes;
}

size_t nex_ringbuf_available(const nex_ringbuf_t *rb) {
    return rb ? rb->count : 0;
}

size_t nex_ringbuf_free_space(const nex_ringbuf_t *rb) {
    return rb ? (rb->size - rb->count) : 0;
}

void nex_ringbuf_clear(nex_ringbuf_t *rb) {
    if (!rb) return;
    uint32_t isr = nex_arch_interrupt_disable();
    rb->head = 0;
    rb->tail = 0;
    rb->count = 0;
    nex_arch_interrupt_restore(isr);
}

/* ========================================================================== */
/* Message Queue                                                              */
/* ========================================================================== */

nex_err_t nex_queue_create(size_t item_size, size_t capacity, nex_queue_handle_t *handle) {
    if (!handle || item_size == 0 || capacity == 0) return NEX_ERR_INVALID_ARG;

    nex_queue_t *q = (nex_queue_t *)nex_malloc(sizeof(nex_queue_t));
    if (!q) return NEX_ERR_NO_MEM;

    q->buffer = (uint8_t *)nex_malloc(item_size * capacity);
    if (!q->buffer) {
        nex_free(q);
        return NEX_ERR_NO_MEM;
    }

    q->item_size = item_size;
    q->capacity = capacity;
    q->head = 0;
    q->tail = 0;
    q->count = 0;

    nex_mutex_create(&q->mutex);
    nex_sem_create(0, (uint32_t)capacity, &q->sem_items);
    nex_sem_create((uint32_t)capacity, (uint32_t)capacity, &q->sem_spaces);

    *handle = q;
    return NEX_OK;
}

nex_err_t nex_queue_send(nex_queue_handle_t handle, const void *item, nex_time_ms_t timeout_ms) {
    if (!handle || !item) return NEX_ERR_INVALID_ARG;

    nex_err_t err = nex_sem_wait(handle->sem_spaces, timeout_ms);
    if (err != NEX_OK) return err;

    nex_mutex_lock(handle->mutex, NEX_WAIT_FOREVER);
    memcpy(handle->buffer + (handle->head * handle->item_size), item, handle->item_size);
    handle->head = (handle->head + 1) % handle->capacity;
    handle->count++;
    nex_mutex_unlock(handle->mutex);

    nex_sem_post(handle->sem_items);
    return NEX_OK;
}

nex_err_t nex_queue_receive(nex_queue_handle_t handle, void *item, nex_time_ms_t timeout_ms) {
    if (!handle || !item) return NEX_ERR_INVALID_ARG;

    nex_err_t err = nex_sem_wait(handle->sem_items, timeout_ms);
    if (err != NEX_OK) return err;

    nex_mutex_lock(handle->mutex, NEX_WAIT_FOREVER);
    memcpy(item, handle->buffer + (handle->tail * handle->item_size), handle->item_size);
    handle->tail = (handle->tail + 1) % handle->capacity;
    handle->count--;
    nex_mutex_unlock(handle->mutex);

    nex_sem_post(handle->sem_spaces);
    return NEX_OK;
}

size_t nex_queue_count(nex_queue_handle_t handle) {
    return handle ? handle->count : 0;
}

nex_err_t nex_queue_destroy(nex_queue_handle_t handle) {
    if (!handle) return NEX_ERR_INVALID_ARG;
    nex_mutex_destroy(handle->mutex);
    nex_sem_destroy(handle->sem_items);
    nex_sem_destroy(handle->sem_spaces);
    if (handle->buffer) nex_free(handle->buffer);
    nex_free(handle);
    return NEX_OK;
}
