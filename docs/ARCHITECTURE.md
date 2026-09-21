# ข้อกำหนดสถาปัตยกรรม NexOS v2.0 (Architecture Specification)

## 1. หลักการสำคัญของสถาปัตยกรรม (Core Architectural Principle)

NexOS เป็นสถาปัตยกรรมระบบปฏิบัติการสมองกลฝังตัวแบบแยกส่วน (Modular), พกพาง่าย (Portable) และไม่ยึดติดกับฮาร์ดแวร์ (Hardware-Independent)
โดยมีกฎเหล็กพื้นฐานของระบบคือ:

> **แกนกลางของ NexOS (NexOS Core) ต้องไม่ขึ้นตรงต่อไมโครคอนโทรลเลอร์, ชิป SoC, บอร์ดพัฒนา, SDK ของผู้ผลิต หรือรีจิสเตอร์ของฮาร์ดแวร์ใดๆ เป็นการเฉพาะ**

การติดต่อกับฮาร์ดแวร์ทั้งหมดจะถูกแยกขาดไว้เบื้องหลังอินเทอร์เฟซมาตรฐาน:
- **Hardware Abstraction Layer (HAL)**: สัญญาและข้อตกลงฟังก์ชันที่เป็นอิสระจากฮาร์ดแวร์
- **Platform Support Packages (PSP)**: โค้ดอิมพลีเมนต์เฉพาะของแต่ละชิป SoC
- **Device Drivers**: ไดรเวอร์อุปกรณ์มาตรฐานบนระบบ VFS (`nex_device_*`)

```text
                    แอปพลิเคชัน NexOS (Applications)
                                    │
                                    ▼
                     NexOS API / SDK (<nexos.h>)
                                    │
                                    ▼
                    NexOS Runtime & Syscall Vector
                                    │
                                    ▼
                       NexOS Core (แกนกลาง OS)
     (Kernel, Scheduler, Memory, Tasks, Sync, IPC, VFS)
                                    │
                                    ▼
                    Hardware HAL (ชั้นนามธรรมของฮาร์ดแวร์)
                                    │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
          RISC-V          Xtensa          ARM / AVR / Host
     (ESP32-C6 Ref)   (ESP32/ESP8266)  (RP2040, STM32, Arduino)
             │              │              │
          ฮาร์ดแวร์        ฮาร์ดแวร์        ฮาร์ดแวร์
```

---

## 2. การรองรับหลายสถาปัตยกรรม CPU (Multi-Architecture Support)

NexOS ห่อหุ้มคำสั่งเฉพาะของสถาปัตยกรรม CPU ไว้ใน `arch/include/nex_arch.h`:
- การเตรียมพื้นที่และจัด Stack Frame (`nex_arch_stack_init`)
- การเปิด/ปิดการขัดจังหวะระบบ (Global Interrupt Lock/Unlock) (`nex_arch_interrupt_disable`, `nex_arch_interrupt_restore`)
- การสั่งสลับบริบทการทำงาน (Context Switching) (`nex_arch_context_switch`)
- การเริ่มทำงานงานแรกสุด (First Task Dispatch) (`nex_arch_start_first_task`)

สถาปัตยกรรม CPU ที่รองรับ:
- **RISC-V 32-bit (`arch/riscv/`)**: RV32IMC / RV32IMAC (แพลตฟอร์มอ้างอิง ESP32-C6)
- **Xtensa (`arch/xtensa/`)**: Xtensa LX6/LX7/LX106 (ESP32, ESP32-S3, ESP8266)
- **ARM Cortex-M (`arch/arm/`)**: ARMv6-M / ARMv7-M / ARMv8-M (RP2040, STM32)
- **AVR 8-bit (`arch/avr/`)**: ATmega328P (Arduino Uno / Nano)
- **Host Simulation (`arch/host/`)**: ระบบจำลองสถาปัตยกรรม x86_64 บน Windows และ Linux

---

## 3. โปรไฟล์การจัดการหน่วยความจำ (Memory Profiles)

NexOS ปรับแต่งตัวเองให้เหมาะสมกับขนาดหน่วยความจำของไมโครคอนโทรลเลอร์แต่ละกลุ่มผ่าน 3 โปรไฟล์มาตรฐาน:

| โปรไฟล์ (Profile) | กลุ่มเป้าหมาย | ขนาด RAM | ฟีเจอร์หลักในแกนกลาง |
| :--- | :--- | :--- | :--- |
| **NexOS Micro** | ATmega328P, ไมโครคอนโทรลเลอร์ขนาดเล็ก | < 16 KB | Cooperative Scheduler, การจัดสรรหน่วยความจำแบบ Static Pool, รองรับ GPIO/UART/Timer พื้นฐาน |
| **NexOS Standard** | ESP8266, RP2040, Pico W | 64 - 256 KB | Preemptive Multitasking, ตัวจัดสรร Heap Dynamic, คิวส่งข้อความ (Message Queues), ระบบไฟล์เสมือน VFS, การเชื่อมต่อเครือข่ายเบื้องต้น |
| **NexOS Advanced** | ESP32-C6, ESP32-S3, STM32 | > 256 KB | Multitasking เต็มรูปแบบ, Dynamic Slab/Heap, WiFi 6, Bluetooth LE, ระบบความปลอดภัยและตัวโหลดแอปพลิเคชันจาก MicroSD |

---

## 4. ระบบค้นหาขีดความสามารถของอุปกรณ์ (Capability System)

แอปพลิเคชันสามารถสอบถามคุณสมบัติของฮาร์ดแวร์แบบไดนามิกขณะทำงานได้ผ่านฟังก์ชัน `nex_device_has(NEX_CAP_*)`:

```c
if (nex_device_has(NEX_CAP_WIFI)) {
    nex_wifi_init();
    nex_wifi_connect(&cfg);
} else {
    nex_log_info("APP", "บอร์ดนี้ไม่มีโมดูล WiFi จะเปลี่ยนไปบันทึกข้อมูลลงพื้นที่จัดเก็บภายในแทน");
}
```

สิ่งนี้ช่วยรับประกันว่าซอร์สโค้ดของแอปพลิเคชันจะสามารถทำงานข้ามบอร์ดฮาร์ดแวร์ต่างๆ ได้อย่างราบรื่น ไม่เกิดข้อผิดพลาดของระบบ และไม่ต้องเขียนโค้ดแยกเงื่อนไข `#ifdef` ซ้ำซ้อน

---

## 5. การพกพาโค้ดข้ามแพลตฟอร์ม (Source Portability)

NexOS มุ่งเน้นไปที่ **Source-Level Portability (ความสามารถในการนำซอร์สโค้ดเดิมไปคอมไพล์ได้ทุกแพลตฟอร์ม)**:
ไฟล์ `main.c` เดียวกันสามารถคอมไพล์เพื่อใช้งานบน ESP32-C6, RP2040, ESP8266, Arduino AVR และ Host PC ได้โดยไม่ต้องแก้ไขโค้ดแอปพลิเคชัน
โดยแต่ละแพลตฟอร์มจะสร้างไฟล์เอาต์พุตไบนารีตามรูปแบบที่ฮาร์ดแวร์นั้นๆ ต้องการ:
- ESP32-C6: `.bin` / `.app`
- ESP8266: `.bin`
- RP2040 / Pico: `.uf2`
- Arduino AVR: `.hex`
- STM32: `.bin`
- Host Simulator: `.exe`
