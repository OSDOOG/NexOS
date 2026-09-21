# คู่มือการพอร์ต: วิธีการเพิ่มแพลตฟอร์มเป้าหมายใหม่ลงใน NexOS (Porting Guide)

การเพิ่มชิปไมโครคอนโทรลเลอร์หรือบอร์ดเป้าหมายใหม่ลงใน NexOS **ไม่จำเป็นต้องแก้ไขโค้ดใดๆ ในโฟลเดอร์ `core/` เลยแม้แต่บรรทัดเดียว**
โดยให้ปฏิบัติตามกระบวนการมาตรฐาน 10 ขั้นตอนนี้:

---

## ขั้นตอนที่ 1: กำหนดสถาปัตยกรรม CPU (Define CPU Architecture)

หากสถาปัตยกรรม CPU ของชิปเป้าหมายได้รับการรองรับอยู่แล้ว (RISC-V, Xtensa, ARM Cortex-M, AVR) สามารถข้ามไปยังขั้นตอนที่ 2 ได้ทันที
หากยังไม่รองรับ ให้สร้างโฟลเดอร์ใหม่ภายใต้ `arch/<new_arch>/`:
- อิมพลีเมนต์ฟังก์ชัน `nex_arch_init()`
- อิมพลีเมนต์ฟังก์ชัน `nex_arch_interrupt_disable()` และ `nex_arch_interrupt_restore()`
- อิมพลีเมนต์ฟังก์ชัน `nex_arch_stack_init()` สำหรับจัดโครงสร้าง Context Stack Frame
- อิมพลีเมนต์ฟังก์ชัน `nex_arch_context_switch()`

---

## ขั้นตอนที่ 2: สร้างไฟล์นิยามแพลตฟอร์มเป้าหมาย (Create Target Definition)

สร้างไฟล์ `targets/<target_id>/target.json`:

```json
{
    "name": "my-target",
    "display_name": "ชื่อบอร์ดของผู้ผลิต",
    "architecture": "arm",
    "cpu": "cortex-m4",
    "clock_mhz": 120,
    "ram_bytes": 131072,
    "flash_bytes": 524288,
    "profile": "standard",
    "toolchain": {
        "prefix": "arm-none-eabi-",
        "compiler": "arm-none-eabi-gcc",
        "cflags": "-mcpu=cortex-m4 -mthumb -O2 -ffunction-sections -fdata-sections",
        "ldflags": "-T platforms/my-target/linker/target.ld -Wl,--gc-sections"
    },
    "output_format": "bin",
    "flash_tool": "openocd",
    "flash_args": "-f board.cfg -c 'program {output_file} verify reset exit'",
    "capabilities": ["GPIO", "UART", "SPI", "I2C", "TIMER"]
}
```

---

## ขั้นตอนที่ 3: อิมพลีเมนต์ Platform Support Package (PSP)

สร้างโฟลเดอร์ `platforms/<target_id>/`:
1. `platforms/<target_id>/platform.json`: ข้อมูลเมทาดาตาของแพลตฟอร์ม
2. `platforms/<target_id>/<target_id>_hal_gpio.c`: ฟังก์ชันควบคุมการอ่าน เขียน และตั้งค่าโหมดพิน GPIO
3. `platforms/<target_id>/<target_id>_hal_uart.c`: ฟังก์ชันรับ-ส่งข้อมูลผ่านพอร์ตซีเรียล UART
4. `platforms/<target_id>/<target_id>_hal_timer.c`: ตัวนับเวลา SysTick Interrupt ความถี่ 1000 Hz
5. `platforms/<target_id>/<target_id>_boot.c`: ลำดับการบูตระบบและการเข้าสู่เคอร์เนล

---

## ขั้นตอนที่ 4: เพิ่มการตั้งค่า Linker Script

กำหนดแผนผังหน่วยความจำ (Memory Map) และเซกชันต่างๆ ใน `platforms/<target_id>/linker/<target_id>.ld`:
- กำหนดขอบเขต `MEMORY` (พื้นที่ Flash, RAM, เวกเตอร์ตารางอินเทอร์รัปต์)
- กำหนด Entry Symbol ชี้ไปที่ `nex_platform_boot`

---

## ขั้นตอนที่ 5: อิมพลีเมนต์ลำดับการบูตของแพลตฟอร์ม (Platform Boot Sequence)

ในไฟล์ `platforms/<target_id>/<target_id>_boot.c`:
```c
#include <nexos.h>

const char *g_nex_target_name = "my-target";
const char *g_nex_arch_name = "arm-cortex-m4";
nex_profile_t g_nex_system_profile = NEX_PROFILE_STANDARD;

#define PLATFORM_HEAP_SIZE (64 * 1024)
static uint8_t s_heap[PLATFORM_HEAP_SIZE];

extern void app_main(void);

void nex_platform_boot(void) {
    /* 1. ลงทะเบียนขีดความสามารถของฮาร์ดแวร์ */
    nex_capability_register(NEX_CAP_GPIO | NEX_CAP_UART | NEX_CAP_TIMER);

    /* 2. กำหนดและเริ่มต้นหน่วยความจำ Heap */
    nex_memory_init(s_heap, PLATFORM_HEAP_SIZE);

    /* 3. เริ่มต้นฮาร์ดแวร์ชั้น HAL */
    nex_gpio_init();
    nex_uart_init(0, NULL);

    /* 4. เริ่มต้นระบบแกนกลาง NexOS Core */
    nex_core_init();

    /* 5. สร้าง Task สำหรับแอปพลิเคชันและเริ่มทำงาน Scheduler */
    nex_task_create("app_main", (nex_task_entry_t)app_main, NULL, 4, 2048, NULL);
    nex_core_start();
}
```

---

## ขั้นตอนที่ 6: ตรวจสอบแพลตฟอร์มด้วยคำสั่ง CLI

รันคำสั่ง:
```bash
nex targets
```
ตรวจสอบว่า `my-target` ปรากฏในรายการพร้อมสถาปัตยกรรม CPU และขนาด RAM อย่างถูกต้อง

---

## ขั้นตอนที่ 7: ตรวจสอบรายละเอียดของแพลตฟอร์มเป้าหมาย

รันคำสั่ง:
```bash
nex target info my-target
```
ตรวจดูว่าขีดความสามารถ (Capabilities), ความเร็วสัญญาณนาฬิกา และการตั้งค่าคอมไพเลอร์แสดงผลอย่างถูกต้อง

---

## ขั้นตอนที่ 8: คอมไพล์แอปพลิเคชันตัวอย่าง

รันคำสั่ง:
```bash
nex build --target my-target
```
ระบบจะเรียกใช้ Cross-compiler และทำการ Link โปรแกรมด้วย Linker Script ของแพลตฟอร์มที่เพิ่งสร้างขึ้น

---

## ขั้นตอนที่ 9: ตรวจสอบความถูกต้องของสถาปัตยกรรมอัตโนมัติ

รันคำสั่ง:
```bash
python tests/run_all_tests.py
```
เพื่อให้แน่ใจว่าระบบผ่านการทดสอบ 100% และไม่มีโค้ดของชิปตัวใหม่รั่วไหลเข้าไปใน `core/`

---

## ขั้นตอนที่ 10: เปิดใช้งานบน NexOS Developer Studio

รันคำสั่ง:
```bash
python nexos-developer/server.py
```
ชิปเป้าหมายตัวใหม่จะปรากฏในหน้าต่างเลือก Target บน Web GUI พร้อมป้ายแสดง Capabilities โดยอัตโนมัติ!
