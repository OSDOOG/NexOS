# คู่มือเริ่มต้นใช้งาน NexOS ใน 5 นาที (5-Minute Quick Start)

คู่มือนี้จะพาคุณเริ่มต้นตั้งแต่ศูนย์ จนถึงการรันแอปพลิเคชัน NexOS ตัวแรกบนบอร์ด **ESP32-C6** ผ่าน MicroSD Card ภายในเวลาไม่เกิน 5 นาที

---

## ขั้นตอนที่ 1: ตรวจสอบความพร้อมของสภาพแวดล้อม (Verify Environment)

เปิด Command Prompt หรือ PowerShell แล้วรันคำสั่ง:

```bash
nexos doctor
```

ผลลัพธ์ที่คาดหวัง:
```text
NexOS Developer Environment
===========================
[OK] Operating System    : Windows 10/11 (AMD64)
[OK] NexOS CLI           : v2.0.0
[OK] NexOS SDK           : v2.0.0 (ABI v1)
[OK] ESP32-C6 target     : Ready (RV32IMAC 160MHz)
[OK] Environment PATH    : Verified
---------------------------
Environment is ready.
```

---

## ขั้นตอนที่ 2: สร้างโปรเจกต์ใหม่ (Create a New Project)

รันคำสั่ง `nexos create` เพื่อสร้างโครงสร้างโปรเจกต์:

```bash
nexos create hello
cd hello
```

ระบบจะสร้างโครงสร้างโฟลเดอร์ดังนี้:
```text
hello/
├── src/
│   └── main.c          <-- จุดเริ่มต้นการทำงานของแอปพลิเคชัน (app_main)
├── include/
│   └── config.h        <-- การตั้งค่าภายในโปรเจกต์
├── resources/          <-- ไฟล์รูปภาพหรือทรัพยากรคงที่
├── tests/              <-- ชุดทดสอบ Unit test
├── nexos.toml          <-- ไฟล์ตั้งค่าแอปพลิเคชันและการขอสิทธิ์ (Permissions)
└── README.md
```

---

## ขั้นตอนที่ 3: เขียนโค้ดแอปพลิเคชัน (Write Application Code)

เปิดไฟล์ `src/main.c`:

```c
#include <nexos.h>

void app_main(void)
{
    nex_log("Hello from NexOS on ESP32-C6!");

    while (1)
    {
        nex_delay_ms(1000);
    }
}
```

---

## ขั้นตอนที่ 4: ตั้งค่าการขอสิทธิ์ฮาร์ดแวร์ (`nexos.toml`)

เปิดดูไฟล์ `nexos.toml`:

```toml
[app]
name = "hello"
version = "1.0.0"
description = "NexOS Hello World Application"

[target]
architecture = "riscv32"
chip = "esp32c6"

[nexos]
minimum_version = "0.1.0"
abi_version = 1

[memory]
stack = 4096
heap = 8192

[permissions]
gpio = false
adc = false
i2c = false
spi = false
uart = true
display = true
storage = false
network = false
```

---

## ขั้นตอนที่ 5: คอมไพล์และสร้างแพ็กเกจ (.app)

คอมไพล์และแพ็กเกจแอปพลิเคชันสำหรับใช้งานจริง:

```bash
nexos build --release
```

ผลลัพธ์:
```text
Build successful
================
Application : hello
Version     : 1.0.0
Target      : ESP32C6
Architecture: RISCV32

Code        : 0.1 KB
RO Data     : 0.0 KB
Stack       : 4 KB
Heap        : 8 KB

Output:
  dist/hello.app
```

---

## ขั้นตอนที่ 6: ตรวจสอบความถูกต้องของแพ็กเกจ (.app)

ตรวจสอบความถูกต้อง ความเข้ากันได้ของ ABI และค่า Checksum ก่อนนำไปใช้งาน:

```bash
nexos validate dist/hello.app
```

ผลลัพธ์ที่คาดหวัง:
```text
NexOS Application Validator
===========================
Application: hello
Version:     1.0.0
Target:      ESP32-C6
Architecture:RISC-V 32-bit (rv32imac)
ABI:         1
NexOS:       >= 0.1.0

[OK]    Package format (NEXAPP magic valid)
[OK]    Architecture: RISC-V 32-bit (rv32imac)
[OK]    Target Chip: ESP32-C6
[OK]    ABI version: 1 (Compatible)
[OK]    Payload SHA-256 Checksum verified
[OK]    Memory requirements (Stack: 4 KB, Heap: 8 KB)
[OK]    Permissions: uart, display
---------------------------
Application is valid.
```

---

## ขั้นตอนที่ 7: คัดลอกลง MicroSD Card และรันบนบอร์ดจริง!

1. คัดลอกไฟล์ `dist/hello.app` ไปยังโฟลเดอร์ `/apps/` ใน MicroSD Card ของคุณ:
   ```text
   MicroSD (FAT32)
   └── apps/
       └── hello.app
   ```
2. เสียบ MicroSD Card เข้ากับบอร์ดพัฒนา ESP32-C6
3. จ่ายไฟให้บอร์ด ระบบ NexOS Core จะทำการตรวจพบไฟล์ `hello.app` โดยอัตโนมัติ ตรวจสอบความถูกต้องของค่า SHA-256 และการขอสิทธิ์ฮาร์ดแวร์ จากนั้นโหลดโค้ดเข้าสู่ SRAM และเริ่มทำงานทันทีโดยไม่ต้องแฟลชเฟิร์มแวร์ใหม่!
