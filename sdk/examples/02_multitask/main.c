/**
 * @file main.c
 * @brief NexOS Example 02: Preemptive Multitasking & Message Queue IPC
 */

#include "nexos.h"

#define TAG "MULTITASK"

static nex_queue_handle_t s_msg_queue = NULL;

typedef struct {
    uint32_t seq;
    uint32_t val;
} sample_msg_t;

static void producer_task(void *arg) {
    (void)arg;
    uint32_t counter = 0;
    while (counter < 5) {
        sample_msg_t msg = { .seq = counter, .val = counter * 100 };
        nex_log_info(TAG, "Producer sending seq=%u", counter);
        nex_queue_send(s_msg_queue, &msg, NEX_WAIT_FOREVER);
        counter++;
        nex_task_sleep_ms(200);
    }
}

static void consumer_task(void *arg) {
    (void)arg;
    sample_msg_t msg;
    int received = 0;
    while (received < 5) {
        if (nex_queue_receive(s_msg_queue, &msg, NEX_WAIT_FOREVER) == NEX_OK) {
            nex_log_info(TAG, "Consumer got seq=%u, val=%u", msg.seq, msg.val);
            received++;
        }
    }
}

void app_main(void) {
    nex_log_info(TAG, "Starting Multitasking IPC Demo");

    nex_queue_create(sizeof(sample_msg_t), 4, &s_msg_queue);

    nex_task_create("producer", producer_task, NULL, 5, 2048, NULL);
    nex_task_create("consumer", consumer_task, NULL, 5, 2048, NULL);

    /* Run demo tasks synchronously on host or yield to scheduler */
    producer_task(NULL);
    consumer_task(NULL);

    nex_log_info(TAG, "Multitasking demonstration complete");
}
