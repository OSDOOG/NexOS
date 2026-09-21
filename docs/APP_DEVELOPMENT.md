# คู่มือการพัฒนาแอปพลิเคชัน NexOS (Application Development Guide)

## 1. การเขียนแอปพลิเคชันแรกของคุณ

แอปพลิเคชัน NexOS จะเรียกใช้ Header `<nexos.h>` และเริ่มต้นการทำงานที่ฟังก์ชัน `app_main(void)`:

```c
#include <nexos.h>

#define TAG "APP"

void app_main(void) {
    nex_log_info(TAG, "แอปพลิเคชันเริ่มต้นทำงานแล้ว!");

    /* ตรวจสอบการรองรับฮาร์ดแวร์ก่อนเรียกใช้งาน */
    if (nex_device_has(NEX_CAP_GPIO)) {
        nex_gpio_mode(15, NEX_PIN_OUTPUT);
        nex_gpio_write(15, NEX_HIGH);
    }

    while (1) {
        nex_delay_ms(1000);
    }
}
```

---

## 2. การสร้าง Task มัลติทาสก์และการส่งข้อมูลผ่านคิว (Queues)

```c
#include <nexos.h>

static nex_queue_handle_t q;

static void worker(void *arg) {
    int val = 42;
    nex_queue_send(q, &val, NEX_WAIT_FOREVER);
}

void app_main(void) {
    /* สร้างคิวขนาด 10 ช่อง สำหรับเก็บข้อมูล int */
    nex_queue_create(sizeof(int), 10, &q);

    /* สร้าง Task แยกสำหรับทำงานเบื้องหลัง */
    nex_task_create("worker", worker, NULL, 5, 2048, NULL);

    int received;
    nex_queue_receive(q, &received, NEX_WAIT_FOREVER);
    nex_log_info("APP", "ได้รับข้อมูลจาก Task: %d", received);
}
```

---

## 3. การตรวจสอบขีดความสามารถของฮาร์ดแวร์ก่อนใช้งาน (Capabilities)

อย่าทึกทักเอาเองว่าบอร์ดไมโครคอนโทรลเลอร์ทุกตัวจะมีฮาร์ดแวร์ครบ ให้ใช้คำสั่งป้องกันเสมอ:

```c
if (nex_device_has(NEX_CAP_WIFI)) {
    nex_wifi_init();
}

if (nex_device_has(NEX_CAP_DISPLAY)) {
    nex_ssd1306_init(0, 0x3C);
}
```
โค้ดลักษณะนี้จะช่วยให้แอปพลิเคชันสามารถนำไปรันบนชิปตัวใดก็ได้โดยไม่เกิดแครชหรือค้าง
