# NexOS Multi-Target Micro-Kernel Operating System & Ecosystem v1.0.0

> **NexOS** คือระบบปฏิบัติการแบบ Micro-Kernel RTOS สำหรับสมองกลฝังตัว (Embedded Operating System) ที่ออกแบบตามสถาปัตยกรรมแยกส่วน (Modular), พกพาง่าย (Portable) และ **ไม่ยึดติดกับผู้ผลิตฮาร์ดแวร์ (Hardware-Independent)**
>
> มี **ESP32-C6 (RISC-V 32-bit)** เป็นฮาร์ดแวร์อ้างอิงหลัก และรองรับข้ามสถาปัตยกรรมถึง **9 แพลตฟอร์มเป้าหมาย** (RP2040, Pico W, ESP32, ESP32-S3, ESP8266, STM32, Arduino AVR และ Host PC Simulator)

---

## 📑 สารบัญ (Table of Contents)

1. [ปรัชญาและหลักการทำงานของ NexOS (Core Principles)](#-1-ปรัชญาและหลักการทำงานของ-nexos-core-principles)
2. [สถาปัตยกรรมระบบ 3 ชั้น (3-Tier Architecture) & โครงสร้างไฟล์ `.app`](#-2-สถาปัตยกรรมระบบ-3-ชั้น-3-tier-architecture--โครงสร้างไฟล์-app)
3. [แพลตฟอร์มฮาร์ดแวร์ที่รองรับ 9 เป้าหมาย (Supported Hardware Platforms)](#-3-แพลตฟอร์มฮาร์ดแวร์ที่รองรับ-9-เป้าหมาย-supported-hardware-platforms)
4. [การติดตั้งระบบ (Installation)](#-4-การติดตั้งระบบ-installation)
5. [การ Flash ตัว OS ลงบอร์ดจริงผ่าน Command Prompt และ Web GUI](#-5-การ-flash-ตัว-os-ลงบอร์ดจริงผ่าน-command-prompt-และ-web-gui)
   - [5.1 วิธีตรวจสอบพอร์ต COM บน Windows](#51-วิธีตรวจสอบพอร์ต-com-บน-windows)
   - [5.2 การ Flash บอร์ด ESP32 / ESP32-C6 ผ่าน Command Prompt](#52-การ-flash-บอร์ด-esp32--esp32-c6-ผ่าน-command-prompt)
   - [5.3 การ Flash บอร์ด Raspberry Pi Pico / RP2040 ผ่าน Command Prompt](#53-การ-flash-บอร์ด-raspberry-pi-pico--rp2040-ผ่าน-command-prompt)
   - [5.4 การ Flash บนบอร์ดตระกูลอื่นๆ (ESP32, ESP32-S3, ESP8266, AVR, STM32)](#54-การ-flash-บนบอร์ดตระกูลอื่นๆ-esp32-esp32-s3-esp8266-avr-stm32)
   - [5.5 การ Flash ผ่าน Web Developer Studio (One-Click Flash)](#55-การ-flash-ผ่าน-web-developer-studio-one-click-flash)
6. [คู่มือเริ่มต้นสร้างโปรเจกต์ใหม่แบบ Step-by-Step (Getting Started)](#-6-คู่มือเริ่มต้นสร้างโปรเจกต์ใหม่แบบ-step-by-step-getting-started)
   - [ขั้นตอนที่ 1: การใช้คำสั่งสร้างโปรเจกต์ใหม่](#ขั้นตอนที่-1-การใช้คำสั่งสร้างโปรเจกต์ใหม่)
   - [ขั้นตอนที่ 2: โครงสร้างไฟล์และไฟล์คอนฟิก (`nexos.toml` / `nexos.json`)](#ขั้นตอนที่-2-โครงสร้างไฟล์และไฟล์คอนฟิก-nexostoml--nexosjson)
   - [ขั้นตอนที่ 3: การเขียนโปรแกรม C และเรียกใช้ NexOS API](#ขั้นตอนที่-3-การเขียนโปรแกรม-c-และเรียกใช้-nexos-api)
   - [ขั้นตอนที่ 4: การคอมไพล์โปรเจกต์เป็นไฟล์ `.app`](#ขั้นตอนที่-4-การคอมไพล์โปรเจกต์เป็นไฟล์-app)
   - [ขั้นตอนที่ 5: การทดสอบบนคอมพิวเตอร์ด้วย Host Simulator](#ขั้นตอนที่-5-การทดสอบบนคอมพิวเตอร์ด้วย-host-simulator)
   - [ขั้นตอนที่ 6: การนำไปรันบนบอร์ดจริงผ่าน MicroSD Card](#ขั้นตอนที่-6-การนำไปรันบนบอร์ดจริงผ่าน-microsd-card)
7. [คู่มือคำสั่ง CLI ทั้งหมดโดยละเอียด (Complete Command Reference)](#-7-คู่มือคำสั่ง-cli-ทั้งหมดโดยละเอียด-complete-command-reference)
   - [7.1 ชุดคำสั่ง `nexos` (Application & Package Tool)](#71-ชุดคำสั่ง-nexos-application--package-tool)
   - [7.2 ชุดคำสั่ง `nex` (Multi-Target & Hardware Management Tool)](#72-ชุดคำสั่ง-nex-multi-target--hardware-management-tool)
8. [การใช้งาน NexOS Developer Studio (Web Mission Control)](#-8-การใช้งาน-nexos-developer-studio-web-mission-control)
9. [ขั้นตอนการพัฒนาแอปพลิเคชันด้วย IDE ภายนอก (VS Code / CLion)](#-9-ขั้นตอนการพัฒนาแอปพลิเคชันด้วย-ide-ภายนอก-vs-code--clion)
10. [การทดสอบด้วยระบบจำลอง (Host PC Simulator)](#-10-การทดสอบด้วยระบบจำลอง-host-pc-simulator)
11. [โครงสร้างไดเรกทอรีของโปรเจกต์ (Directory Structure)](#-11-โครงสร้างไดเรกทอรีของโปรเจกต์-directory-structure)
12. [การแก้ปัญหาที่พบบ่อย (Troubleshooting & FAQ)](#-12-การแก้ปัญหาที่พบบ่อย-troubleshooting--faq)
13. [ใบอนุญาตการใช้งาน (License)](#-13-ใบอนุญาตการใช้งาน-license)
14. [งานวิจัยและเอกสารอ้างอิง (Research & References)](docs/RESEARCH_AND_REFERENCES.md)

---

## 💡 1. ปรัชญาและหลักการทำงานของ NexOS (Core Principles)

ในระบบสมองกลฝังตัวแบบเดิม (Monolithic Firmware เช่น Arduino หรือ ESP-IDF ทั่วไป) โค้ดระบบปฏิบัติการ ไลบรารี และโค้ดโปรแกรมของผู้ใช้จะถูกคอมไพล์มัดรวมกันเป็นไฟล์ไบนารีเดียว หากต้องการแก้ไขโค้ดแม้แต่บรรทัดเดียว ผู้ใช้จำเป็นต้องต่อสาย USB แล้ว Flash บอร์ดใหม่ทั้งหมด

**NexOS เปลี่ยนสถาปัตยกรรมใหม่ โดยนำแนวคิดของระบบปฏิบัติการระดับสากล (เช่น Linux / Android) มาย่อส่วนสู่ไมโครคอนโทรลเลอร์:**

```text
       ┌─────────────────────────────────────────────────────────┐
       │                NexOS Core Firmware (OS)                 │
       │    (ติดตั้งลงใน Flash Memory ของบอร์ดเพียง "ครั้งเดียว")    │
       └──────────────────────────┬──────────────────────────────┘
                                  │ บูตระบบ & เฝ้าตรวจจับ Storage
                                  ▼
       ┌─────────────────────────────────────────────────────────┐
       │              MicroSD Card Storage (/apps/)              │
       │                                                         │
       │   [ blinky.app ]     [ sensor.app ]     [ shell.app ]   │
       │   (แอปที่ 1)          (แอปที่ 2)         (แอปที่ 3)      │
       └──────────────────────────┴──────────────────────────────┘
```

1. **การแยกตัว OS กับ Application ออกจากกันอย่างเด็ดขาด:**
   * **NexOS Core:** ติดตั้งลงใน Flash Memory ภายในของชิปเพียงครั้งเดียว ทำหน้าที่เป็น Micro-Kernel ให้บริการ Scheduler, Memory Management, Device Drivers, VFS และ Task Switching
   * **NexOS App (`.app`):** ผู้พัฒนาเขียนโปรแกรมภาษา C แล้วคอมไพล์เป็นไฟล์นามสกุล `.app` ใส่ลงใน **MicroSD Card** เมื่อนำการ์ดไปเสียบที่ตัวบอร์ด NexOS จะอ่านและโหลดโปรแกรมขึ้นมารันใน RAM ทันทีโดยไม่ต้องต่อสาย Flash ตัวบอร์ดซ้ำอีกต่อไป
2. **แกนกลางที่เป็นอิสระจากฮาร์ดแวร์ (Hardware-Independent Core):**
   * โค้ดในโฟลเดอร์ `core/` ทั้งหมดไม่มีการ `#include` ไฟล์เฉพาะของผู้ผลิตชิปใดๆ ไม่มีการแตะรีจิสเตอร์ของฮาร์ดแวร์โดยตรง
   * สื่อสารกับฮาร์ดแวร์ผ่าน **HAL (Hardware Abstraction Layer)** และ **Syscall ABI Table** มาตรฐานเท่านั้น
3. **ระบบตรวจสอบขีดความสามารถแบบไดนามิก (Dynamic Capabilities):**
   * แอปพลิเคชันสามารถสอบถามความสามารถของบอร์ดขณะรันไทม์ได้ทันที เช่น ตรวจสอบว่าบอร์ดมี Wi-Fi, I2C, SPI หรือจอแสดงผลหรือไม่ผ่าน `nex_device_has(NEX_CAP_*)` ทำให้โค้ดแอปชุดเดียวกันนำไปรันข้ามชิปได้โดยไม่เกิดแครช

---

## 🏛️ 2. สถาปัตยกรรมระบบ 3 ชั้น (3-Tier Architecture) & โครงสร้างไฟล์ `.app`

```text
┌───────────────────────────────────────────────────────────────────────────┐
│                        1. APPLICATION LAYER                               │
│        User Applications (*.app) / Examples (Blinky, Sensor, Shell)       │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │ nexos.h (API & Syscall Trampoline)
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                     2. SYSTEM CALL ABI VECTOR                             │
│     Function Dispatch Table: GPIO, UART, Timer, Task, Memory, IPC, VFS    │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │ Hardware Abstraction (HAL)
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                     3. NEXOS MICRO-KERNEL CORE                            │
│  ┌───────────────────────┬────────────────────────┬────────────────────┐  │
│  │ Priority Scheduler   │ Slab & Heap Allocator  │ Virtual FileSystem  │  │
│  ├───────────────────────┼────────────────────────┼────────────────────┤  │
│  │ IPC Message Queues    │ Software Timer Engine  │ Security & SHA-256 │  │
│  └───────────────────────┴────────────────────────┴────────────────────┘  │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │ Architecture Drivers
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                          HARDWARE TARGETS                                 │
│    ESP32-C6 (RV32) │ RP2040 (ARM) │ ESP32 (Xtensa) │ AVR │ Host Sim       │
└───────────────────────────────────────────────────────────────────────────┘
```

### โครงสร้างแพ็กเกจแอปพลิเคชัน (`.app`)
ไฟล์ `.app` เป็นไฟล์ไบนารีมาตรฐานที่มี Header ขนาด 64 ไบต์ ดังนี้:
* **Magic Bytes (4 ไบต์):** ค่าตายตัว `0x4E455841` ("NEXA")
* **ABI Version (2 ไบต์):** เวอร์ชัน Syscall ABI ที่แอปรองรับ
* **Target Chip / Architecture (4 ไบต์):** รหัสสถาปัตยกรรม CPU เช่น RISC-V 32, ARM Cortex-M0+, Xtensa, x86_64
* **Required Capabilities (8 ไบต์):** บิตสิทธิ์ของฮาร์ดแวร์ที่แอปต้องการ (GPIO, UART, SPI, I2C, WIFI, STORAGE ฯลฯ)
* **Execution Layout (14 ไบต์):** ขนาด Code, Data, BSS, Stack ที่ต้องการ และ Heap ที่ขอจัดสรร
* **SHA-256 Digest (32 ไบต์):** ลายเซ็นดิจิทัลสำหรับตรวจสอบความสมบูรณ์ของโค้ดก่อนที่ OS จะอนุญาตให้รัน

---

## 🎯 3. แพลตฟอร์มฮาร์ดแวร์ที่รองรับ 9 เป้าหมาย (Supported Hardware Platforms)

| แพลตฟอร์มเป้าหมาย | สถาปัตยกรรม CPU | ความถี่สัญญาณนาฬิกา | RAM / Flash | ฟอร์แมตเฟิร์มแวร์ | วิธีการ Flash OS |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ESP32-C6** *(Ref)* | RISC-V 32-bit (RV32IMAC) | 160 MHz | 512 KB / 4 MB | `.bin` | Serial (Baud: 460800, DIO) |
| **RP2040 / Pico** | Dual ARM Cortex-M0+ | 133 MHz | 264 KB / 2 MB | `.uf2` | UF2 Bootloader / Drive Copy |
| **Pico W** | Dual ARM Cortex-M0+ + Wi-Fi | 133 MHz | 264 KB / 2 MB | `.uf2` | UF2 Bootloader / Drive Copy |
| **ESP32** | Dual Xtensa LX6 | 240 MHz | 520 KB / 4 MB | `.bin` | Serial (esptool) |
| **ESP32-S3** | Dual Xtensa LX7 | 240 MHz | 512 KB / 8 MB | `.bin` | Serial (Native USB/CDC) |
| **ESP8266** | Xtensa LX106 | 80/160 MHz | 80 KB / 4 MB | `.bin` | Serial (esptool) |
| **Arduino AVR** | 8-bit ATmega328P | 16 MHz | 2 KB / 32 KB | `.hex` | Serial (avrdude) |
| **STM32F4** | ARM Cortex-M4 | 168 MHz | 192 KB / 1 MB | `.bin` | ST-Link / DFU |
| **Host PC** | x86_64 / Windows / Linux | Host Native | ไม่จำกัด | `.exe` | รันตรงบนคอมพิวเตอร์ |

---

## 📦 4. การติดตั้งระบบ (Installation)

### วิธีที่ 1: ติดตั้งผ่าน Windows Installer (แนะนำ)
1. รันไฟล์ติดตั้งตัวเต็มที่มาพร้อมระบบ:
   ```text
   dist_installer\NexOS-Developer-Setup.exe
   ```
2. ทำตามขั้นตอนบนหน้าจอ ตัวติดตั้งจะจัดการ:
   * ตั้งค่า Path และ Environment Variables อัตโนมัติ
   * ลงทะเบียนคำสั่ง `nexos` และ `nex` ให้เรียกใช้งานได้จากทุกโฟลเดอร์ใน Command Prompt / PowerShell
   * ติดตั้ง SDK, Header `<nexos.h>`, และตัวอย่างโปรเจกต์พร้อมใช้งานทันที

### วิธีที่ 2: รันจาก Source Code ของโปรเจกต์
* ตรวจสอบว่าเครื่องมี **Python 3.10 ขึ้นไป**
* ติดตั้งไลบรารีที่จำเป็นสำหรับการเชื่อมต่อฮาร์ดแวร์:
  ```bash
  pip install pyserial
  ```

---

## ⚡ 5. การ Flash ตัว OS ลงบอร์ดจริงผ่าน Command Prompt และ Web GUI

> [!IMPORTANT]
> ขั้นตอนการ Flash OS Core นี้ทำเพียง **ครั้งแรกครั้งเดียว** บนบอร์ดแต่ละตัว เพื่อติดตั้งแกนระบบปฏิบัติการลงใน Flash Memory ภายในชิป

### 5.1. วิธีตรวจสอบพอร์ต COM บน Windows

ก่อนสั่ง Flash ต้องทราบก่อนว่าบอร์ดที่เสียบอยู่อยู่ที่พอร์ต COM หมายเลขใด ตรวจสอบได้จาก Command Prompt หรือ PowerShell:

#### ผ่าน Command Prompt (CMD):
```cmd
mode
```
หรือใช้คำสั่งดูพอร์ต Serial:
```cmd
chgport
```

#### ผ่าน PowerShell:
```powershell
Get-CimInstance Win32_SerialPort | Select-Object DeviceID, Description
```

#### หรือผ่านโมดูล Python `pyserial`:
```bash
python -m serial.tools.list_ports -v
```
*(จะแสดงหมายเลขพอร์ต เช่น `COM3`, `COM5` พร้อมชื่อชิป USB-to-UART)*

---

### 5.2. การ Flash บอร์ด ESP32 / ESP32-C6 ผ่าน Command Prompt

บอร์ด ESP32-C6 ใช้หน่วยความจำ Flash ภายในแบบ **DIO (Dual I/O)**

#### 1. คำสั่ง Flash ตรงเข้าสู่บอร์ด:
เปิด Command Prompt หรือ PowerShell ในโฟลเดอร์โปรเจกต์ `NexOS` แล้วรันคำสั่ง (เปลี่ยน `COM5` เป็นพอร์ตของคุณ):
```cmd
python -m esptool --chip esp32c6 --port COM5 --baud 460800 write-flash --flash-mode dio 0x0 platforms/esp32c6/build/nexos_esp32c6.bin
```

#### 2. (ถ้าจำเป็น) ล้าง Flash Memory ก่อนแฟลชใหม่:
หากต้องการล้างข้อมูลเก่าทั้งหมดออกจากบอร์ด ให้สั่ง erase ก่อน:
```cmd
python -m esptool --chip esp32c6 --port COM5 erase_flash
```

#### 3. วิธีกดปุ่มเข้า Download Mode (ในกรณีที่คอมมานด์ไลน์ขึ้น `Failed to connect`):
1. ใช้นิ้ว **กดปุ่ม `BOOT` บนบอร์ด ESP32-C6 ค้างไว้**
2. ใช้อีกนิ้ว **กดปุ่ม `RST` 1 ครั้งแล้วปล่อย**
3. ปล่อยปุ่ม `BOOT`
4. รันคำสั่ง Flash ใน Command Prompt ซ้ำอีกครั้ง
5. เมื่อ Flash เสร็จ esptool จะสั่ง Reset บอร์ดให้อัตโนมัติ หรือกดปุ่ม `RST` 1 ครั้งเพื่อเริ่มรัน NexOS

---

### 5.3. การ Flash บอร์ด Raspberry Pi Pico / RP2040 ผ่าน Command Prompt

ชิป RP2040 **ไม่ได้ใช้ Serial Flash** แต่ใช้ระบบ **UF2 Virtual Drive Bootloader**:

#### ขั้นตอนการ Flash ผ่าน Command Prompt:
1. ถอดสาย USB ออกจากบอร์ด Raspberry Pi Pico
2. ใช้นิ้วกดปุ่มสีขาว **`[ BOOTSEL ]`** บนตัวบอร์ดค้างไว้
3. เสียบสาย USB กลับเข้าคอมพิวเตอร์ แล้วจึงปล่อยมือจากปุ่ม `BOOTSEL`
4. Windows จะตรวจพบไดรฟ์ใหม่ชื่อ **`RPI-RP2`** (สมมติว่าเป็นไดรฟ์ `D:\` หรือ `F:\`)
5. สั่ง Copy ไฟล์เฟิร์มแวร์ผ่าน Command Prompt ได้ทันที:
   ```cmd
   copy platforms\rp2040\build\nexos_rp2040.uf2 D:\
   ```
   *(เปลี่ยน `D:\` ให้ตรงกับไดรฟ์ `RPI-RP2` บนเครื่องของคุณ)*

#### หรือใช้ PowerShell ตรวจหาไดรฟ์และ Copy ให้อัตโนมัติ:
```powershell
$picoDrive = (Get-Volume -FileSystemLabel "RPI-RP2").DriveLetter + ":\"
Copy-Item platforms\rp2040\build\nexos_rp2040.uf2 $picoDrive
```

> [!NOTE]
> ทันทีที่คำสั่ง Copy เสร็จสิ้น ชิป RP2040 จะอ่านข้อมูล UF2 ไปเขียนลง Flash แล้วไดรฟ์ `RPI-RP2` จะปิดตัวลงอัตโนมัติ จากนั้นบอร์ดจะรีบูตเข้าสู่ระบบ NexOS ทันที

---

### 5.4. การ Flash บนบอร์ดตระกูลอื่นๆ (ESP32, ESP32-S3, ESP8266, AVR, STM32)

* **ESP32 (Xtensa Dual-Core):**
  ```cmd
  python -m esptool --chip esp32 --port COMx --baud 460800 write-flash 0x10000 platforms/esp32/build/nexos_esp32.bin
  ```
* **ESP32-S3:**
  ```cmd
  python -m esptool --chip esp32s3 --port COMx --baud 460800 write-flash 0x0 platforms/esp32s3/build/nexos_esp32s3.bin
  ```
* **ESP8266:**
  ```cmd
  python -m esptool --chip esp8266 --port COMx --baud 115200 write-flash 0x0 platforms/esp8266/build/nexos_esp8266.bin
  ```
* **Arduino AVR (ATmega328P / Uno):**
  ```cmd
  avrdude -c arduino -p m328p -P COMx -b 115200 -U flash:w:platforms/avr/build/nexos_avr.hex:i
  ```
* **STM32F4 (ARM Cortex-M4):**
  ```cmd
  st-flash write platforms/stm32/build/nexos_stm32.bin 0x8000000
  ```

---

### 5.5. การ Flash ผ่าน Web Developer Studio (One-Click Flash)

หากไม่ต้องการพิมพ์คำสั่งในคอนโซล สามารถใช้หน้าเว็บจัดการให้ในคลิกเดียว:
1. เปิดเซิร์ฟเวอร์ด้วยคำสั่ง: `python nexos-developer/server.py`
2. เปิดเบราว์เซอร์ไปที่ **[http://localhost:8088](http://localhost:8088)**
3. หน้าเว็บจะตรวจพบบอร์ดอัตโนมัติ (ไฟเขียว `🟢 CONNECTED`)
4. คลิกปุ่ม **`⚡ Flash NexOS Core Firmware`** ระบบจะส่งคำสั่งเบิร์นเฟิร์มแวร์และรีเซ็ตบอร์ดให้อัตโนมัติ

---

## 🚀 6. คู่มือเริ่มต้นสร้างโปรเจกต์ใหม่แบบ Step-by-Step (Getting Started)

ส่วนนี้จะแนะนำตั้งแต่การสร้างโปรเจกต์แอปพลิเคชันจากศูนย์ จนถึงการนำไปรันจริงบนบอร์ด

### ขั้นตอนที่ 1: การใช้คำสั่งสร้างโปรเจกต์ใหม่

เปิด Command Prompt หรือ PowerShell แล้วเลือกรูปแบบที่ต้องการสร้าง:

#### รูปแบบที่ 1: สร้างโปรเจกต์มาตรฐานผ่านคำสั่ง `nexos create`
```bash
nexos create my_sensor_app
```
คำสั่งนี้จะสร้างโฟลเดอร์ `my_sensor_app` พร้อมเทมเพลตมาตรฐาน ประกอบด้วย `nexos.toml`, โฟลเดอร์ `src/`, `include/`, `resources/` และ `tests/`

#### รูปแบบที่ 2: สร้างโปรเจกต์น้ำหนักเบาผ่านคำสั่ง `nex create`
```bash
nex create my_sensor_app
```
คำสั่งนี้จะสร้างโฟลเดอร์โปรเจกต์ที่ประกอบด้วย `main.c` และ `nexos.json` ทันที

---

### ขั้นตอนที่ 2: โครงสร้างไฟล์และไฟล์คอนฟิก (`nexos.toml` / `nexos.json`)

เข้าไปในโฟลเดอร์โปรเจกต์ของคุณ:
```bash
cd my_sensor_app
```

#### โครงสร้างโฟลเดอร์โปรเจกต์:
```text
my_sensor_app/
├── nexos.toml        # ไฟล์กำหนดค่าแอป สถาปัตยกรรม และสิทธิ์ฮาร์ดแวร์
├── src/
│   └── main.c        # ซอร์สโค้ดภาษา C หลักของแอปพลิเคชัน
├── include/          # เฮดเดอร์ไฟล์เพิ่มเติมของโปรเจกต์
├── resources/        # ข้อมูลดิบ รูปภาพ หรือไฟล์ Asset ที่ต้องการแพ็กเกจ
└── tests/            # ชุดทดสอบ Unit Test ของแอป
```

#### ไฟล์คอนฟิกโปรเจกต์ `nexos.toml`:
```toml
[app]
name = "my_sensor_app"
version = "1.0.0"
description = "NexOS Temperature & Status App"

[target]
architecture = "riscv32"
chip = "esp32c6"

[nexos]
minimum_version = "0.1.0"
abi_version = 1

[memory]
stack = 4096      # จองขนาด Stack 4 KB
heap = 8192       # จองขนาด Heap 8 KB

[permissions]
gpio = true       # ขอสิทธิ์ใช้งานพิน GPIO
uart = true       # ขอสิทธิ์ใช้งาน UART สำหรับพิมพ์ Log
i2c = true        # ขอสิทธิ์ใช้งานบัส I2C
spi = false
storage = true    # ขอสิทธิ์อ่าน/เขียน MicroSD Card
network = false
```

---

### ขั้นตอนที่ 3: การเขียนโปรแกรม C และเรียกใช้ NexOS API

เปิดไฟล์ `src/main.c` (หรือ `main.c`) เพื่อเขียนโค้ดภาษา C:

```c
/**
 * @file main.c
 * @brief NexOS Application Source Code
 */

#include <nexos.h>

#define TAG "SENSOR_APP"
#define STATUS_LED_PIN 15

void app_main(void)
{
    nex_log_info(TAG, "====================================");
    nex_log_info(TAG, " My Sensor Application Initialized! ");
    nex_log_info(TAG, "====================================");

    // 1. ตรวจสอบขีดความสามารถของบอร์ดขณะรันไทม์
    if (nex_device_has(NEX_CAP_GPIO)) {
        nex_log_info(TAG, "Configuring LED Pin %d as Output...", STATUS_LED_PIN);
        nex_gpio_mode(STATUS_LED_PIN, NEX_PIN_OUTPUT);
    } else {
        nex_log_warn(TAG, "Current target hardware does not support GPIO!");
    }

    // 2. ลูปการทำงานของแอปพลิเคชัน
    int reading_count = 0;
    while (reading_count < 5) {
        nex_log_info(TAG, "Sensor Reading Cycle #%d", reading_count + 1);

        // เปิดไฟ LED
        if (nex_device_has(NEX_CAP_GPIO)) {
            nex_gpio_write(STATUS_LED_PIN, NEX_HIGH);
        }
        nex_delay_ms(500);

        // ปิดไฟ LED
        if (nex_device_has(NEX_CAP_GPIO)) {
            nex_gpio_write(STATUS_LED_PIN, NEX_LOW);
        }
        nex_delay_ms(500);

        reading_count++;
    }

    nex_log_info(TAG, "Application main task finished cleanly.");
}
```

---

### ขั้นตอนที่ 4: การคอมไพล์โปรเจกต์เป็นไฟล์ `.app`

สั่งคอมไพล์โปรเจกต์ผ่านคำสั่ง:
```bash
nexos build
```
หรือหากต้องการคอมไพล์แบบปรับแต่งความเร็วสูงสุด (Release Optimization):
```bash
nexos build --release
```
หรือสั่งระบุฮาร์ดแวร์เป้าหมายผ่าน `nex`:
```bash
nex build --target esp32-c6
```

ระบบจะคอมไพล์และสร้างแพ็กเกจไฟล์ออกมาที่:
```text
dist/my_sensor_app.app
```

---

### ขั้นตอนที่ 5: การทดสอบบนคอมพิวเตอร์ด้วย Host Simulator

ก่อนนำไปลงบอร์ดจริง คุณสามารถรันจำลองการทำงานบนคอมพิวเตอร์ของคุณได้ทันที:
```bash
nex run --target host
```
ระบบจะจำลองระบบนาฬิกา, สัญญาณ SysTick, การทำงานของ GPIO เสมือน และแสดงผล Log ออกมาทางหน้าจอทันที เพื่อให้คุณตรวจสอบความถูกต้องของตรรกะโปรแกรมได้สะดวกรวดเร็ว

---

### ขั้นตอนที่ 6: การนำไปรันบนบอร์ดจริงผ่าน MicroSD Card

1. **สั่งคัดลอกไฟล์ `.app` ลง MicroSD Card ผ่านคำสั่ง CLI:**
   ```bash
   nexos install dist/my_sensor_app.app
   ```
   *(หรือคัดลอกไฟล์ `my_sensor_app.app` ไปวางไว้ในโฟลเดอร์ `/apps/` บนการ์ด MicroSD โดยตรง)*
2. **เสียบ MicroSD Card เข้ากับตัวบอร์ด:**
   ตัวระบบปฏิบัติการ NexOS Core ที่รันอยู่บนบอร์ดจะตรวจพบไฟล์แอปพลิเคชันใหม่ ตรวจสอบความถูกต้องของ SHA-256 Digest แล้วโหลดขึ้นมารันบนตัวชิปทันที!

---

## 📖 7. คู่มือคำสั่ง CLI ทั้งหมดโดยละเอียด (Complete Command Reference)

ระบบ NexOS มาพร้อมเครื่องมือ CLI หลัก 2 ตัวที่ทำงานสอดประสานกัน:
* **`nexos`**: เครื่องมือสำหรับสร้างโปรเจกต์, คอมไพล์, แพ็กเกจ, ตรวจสอบไบนารี `.app`, และจัดการไฟล์บน MicroSD
* **`nex`**: เครื่องมือระดับระบบสำหรับตรวจสอบฮาร์ดแวร์เป้าหมาย 9 ชนิด, เช็ค Toolchain, ตรวจสอบ SDK, Flash บอร์ด, และเปิด Serial Monitor

---

### 7.1. ชุดคำสั่ง `nexos` (Application & Package Tool)

#### 1. `nexos create <name>`
* **หน้าที่:** สร้างโฟลเดอร์โปรเจกต์แอปพลิเคชันใหม่จากเทมเพลตมาตรฐาน
* **พารามิเตอร์:** `<name>` คือชื่อของแอปพลิเคชัน (ระบบจะแปลงเป็นตัวพิมพ์เล็กและขีดล่างอัตโนมัติ)
* **ตัวอย่าง:**
  ```bash
  nexos create my_blinky
  ```

#### 2. `nexos build [--release]`
* **หน้าที่:** คอมไพล์โค้ดในโปรเจกต์ปัจจุบันและสร้างแพ็กเกจไฟล์ไบนารี `.app` ในโฟลเดอร์ `dist/`
* **ตัวเลือก (Flags):**
  * `--release`: คอมไพล์ด้วย Flag `-O2` เพื่อความเร็วสูงสุดและขนาดไฟล์ที่เล็กที่สุด (หากไม่ใส่จะเป็นโหมด Debug `-Og -g`)
* **ตัวอย่าง:**
  ```bash
  nexos build
  nexos build --release
  ```

#### 3. `nexos clean`
* **หน้าที่:** ลบไฟล์และโฟลเดอร์ที่เกิดจากการคอมไพล์ทั้งหมด (`build/` และ `dist/`)
* **ตัวอย่าง:**
  ```bash
  nexos clean
  ```

#### 4. `nexos rebuild [--release]`
* **หน้าที่:** ทำการ Clean แล้วสั่ง Build ใหม่ทันทีในคำสั่งเดียว
* **ตัวอย่าง:**
  ```bash
  nexos rebuild --release
  ```

#### 5. `nexos package [--release]`
* **หน้าที่:** ตรวจสอบความสมบูรณ์และแพ็กเกจไฟล์ไบนารีเข้าสู่โครงสร้าง `.app` พร้อมคำนวณ Checksum
* **ตัวอย่าง:**
  ```bash
  nexos package
  ```

#### 6. `nexos validate <file.app>`
* **หน้าที่:** ตรวจสอบความถูกต้องของไฟล์แพ็กเกจ `.app` (Magic Header `0x4E455841`, ABI Version, และการตรวจสอบความถูกต้องของ SHA-256)
* **ตัวอย่าง:**
  ```bash
  nexos validate dist/my_app.app
  ```

#### 7. `nexos info <file.app>`
* **หน้าที่:** แสดงข้อมูล Metadata ทั้งหมดของไฟล์ `.app` เช่น ชื่อแอป, เวอร์ชัน, ชิปเป้าหมาย, สถาปัตยกรรม CPU, ขนาด Code/Data, ขนาด Stack/Heap ที่ขอ, และ Checksum
* **ตัวอย่าง:**
  ```bash
  nexos info dist/my_app.app
  ```

#### 8. `nexos size [<file.app>]`
* **หน้าที่:** แสดงสัดส่วนการใช้พื้นที่หน่วยความจำอย่างละเอียด (Header, ส่วนโค้ด `.text`, ส่วนข้อมูล `.data`, `.bss`, และขนาด RAM ที่ต้องใช้)
* **ตัวอย่าง:**
  ```bash
  nexos size dist/my_app.app
  ```

#### 9. `nexos symbols [<file.app>]`
* **หน้าที่:** แสดงตาราง Symbol Table และจุดกระโดด Entry Point (Entry Trampoline และ `app_main`)
* **ตัวอย่าง:**
  ```bash
  nexos symbols
  ```

#### 10. `nexos targets`
* **หน้าที่:** แสดงรายชื่อฮาร์ดแวร์เป้าหมายทั้งหมดที่ระบบรองรับ พร้อมสเปก CPU, RAM, Profile และฟอร์แมตเอาต์พุต
* **ตัวอย่าง:**
  ```bash
  nexos targets
  ```

#### 11. `nexos run [--target <name>]`
* **หน้าที่:** สั่งรันแอปพลิเคชันบนตัวจำลองระบบ (Host Simulator) หรือฮาร์ดแวร์เป้าหมาย
* **ตัวเลือก (Flags):**
  * `--target`: ระบุแพลตฟอร์ม (ค่าเริ่มต้นคือ `host`)
* **ตัวอย่าง:**
  ```bash
  nexos run --target host
  ```

#### 12. `nexos doctor [-t <target>]`
* **หน้าที่:** ตรวจสอบความพร้อมของสภาพแวดล้อมการพัฒนาในเครื่อง หรือระบุ Target เพื่อตรวจเช็คความพร้อมของชิปตัวนั้นๆ โดยเฉพาะ (เช่น สเปกชิป, คอมไพเลอร์เฉพาะสถาปัตยกรรม, เครื่องมือ Flash, เฟิร์มแวร์ Core OS, และ Pinout)
* **ตัวเลือก (Flags):**
  * `-t, --target`: แพลตฟอร์มเป้าหมาย เช่น `esp32c6`, `rp2040`, `pico-w`, `host`, `esp32`, `esp32-s3`, `arduino-avr`, `stm32` (หากไม่ระบุ จะเป็นการตรวจภาพรวมทั้งระบบ)
* **ตัวอย่าง:**
  ```bash
  nexos doctor
  nexos doctor --target rp2040
  nexos doctor --target esp32c6
  nexos doctor --target host
  ```

#### 13. `nexos install <file.app>`
* **หน้าที่:** ติดตั้งและคัดลอกไฟล์ `.app` ไปยังไดเรกทอรี `/apps/` บน MicroSD Card
* **ตัวอย่าง:**
  ```bash
  nexos install dist/my_app.app
  ```

#### 14. `nexos uninstall <name>`
* **หน้าที่:** ลบไฟล์แอปพลิเคชันออกจาก MicroSD Card
* **ตัวอย่าง:**
  ```bash
  nexos uninstall my_app
  ```

#### 15. `nexos list`
* **หน้าที่:** แสดงรายชื่อไฟล์แอปพลิเคชันทั้งหมดที่ติดตั้งอยู่บน MicroSD Card (`/apps/`) พร้อมขนาดไฟล์
* **ตัวอย่าง:**
  ```bash
  nexos list
  ```

#### 16. `nexos version`
* **หน้าที่:** แสดงหมายเลขเวอร์ชันของ NexOS CLI และเวอร์ชันของ ABI ปัจจุบัน
* **ตัวอย่าง:**
  ```bash
  nexos version
  ```

---

### 7.2. ชุดคำสั่ง `nex` (Multi-Target & Hardware Management Tool)

#### 1. `nex targets`
* **หน้าที่:** แสดงตารางเปรียบเทียบแพลตฟอร์มฮาร์ดแวร์เป้าหมายทั้ง 9 แพลตฟอร์มอย่างเป็นระเบียบ
* **ตัวอย่าง:**
  ```bash
  nex targets
  ```

#### 2. `nex target info <target_name>`
* **หน้าที่:** ดูสเปกอย่างละเอียดของชิปเป้าหมายที่ระบุ เช่น ความถี่สัญญาณนาฬิกา, สเปก RAM/Flash, รายชื่อ Hardware Capabilities ที่ชิปนั้นรองรับ, และ Default Pin Mapping
* **ตัวอย่าง:**
  ```bash
  nex target info esp32-c6
  nex target info rp2040
  ```

#### 3. `nex toolchain list`
* **หน้าที่:** ตรวจสอบว่าในเครื่องคอมพิวเตอร์มีคอมไพเลอร์สำหรับแต่ละสถาปัตยกรรมติดตั้งอยู่หรือไม่ (RISC-V, Xtensa ESP32/S3/8266, ARM Cortex-M, AVR, และ GCC) พร้อมบอกที่อยู่ไฟล์หรือลิงก์ดาวน์โหลดหากยังไม่มี
* **ตัวอย่าง:**
  ```bash
  nex toolchain list
  ```

#### 4. `nex sdk list`
* **หน้าที่:** แสดงรายชื่อไลบรารีใน SDK และโปรเจกต์ตัวอย่างในตัวระบบ (Blinky, Multitask, Sensor, Shell)
* **ตัวอย่าง:**
  ```bash
  nex sdk list
  ```

#### 5. `nex create <name>`
* **หน้าที่:** สร้างโปรเจกต์แอปพลิเคชันใหม่ที่มี `main.c` และ `nexos.json` พร้อมคอมไพล์ได้ทันที
* **ตัวอย่าง:**
  ```bash
  nex create my_project
  ```

#### 6. `nex build [-t <target>] [-p <profile>]`
* **หน้าที่:** คอมไพล์โปรเจกต์ตามฮาร์ดแวร์เป้าหมายที่ระบุ
* **ตัวเลือก (Flags):**
  * `-t, --target`: แพลตฟอร์มเป้าหมาย เช่น `esp32-c6`, `rp2040`, `host`, `esp32`, `arduino-avr` (ค่าเริ่มต้น: `esp32-c6`)
  * `-p, --profile`: เลือกระดับฟีเจอร์ OS เช่น `micro`, `standard`, `advanced`
* **ตัวอย่าง:**
  ```bash
  nex build -t esp32-c6
  nex build -t rp2040
  ```

#### 7. `nex run [-t host]`
* **หน้าที่:** คอมไพล์และเปิดระบบจำลอง Host Simulator รันโค้ดแอปพลิเคชันทันทีบนคอมพิวเตอร์
* **ตัวอย่าง:**
  ```bash
  nex run
  nex run -t host
  ```

#### 8. `nex flash [-t <target>] [--port <port>]`
* **หน้าที่:** ส่งคำสั่ง Flash เฟิร์มแวร์ลงบอร์ดฮาร์ดแวร์ผ่านเครื่องมือ Flash ประจำชิปนั้นๆ
* **ตัวเลือก (Flags):**
  * `-t, --target`: ชิปเป้าหมาย (เช่น `esp32-c6`)
  * `--port`: พอร์ต Serial เช่น `COM5`
* **ตัวอย่าง:**
  ```bash
  nex flash -t esp32-c6 --port COM5
  ```

#### 9. `nex monitor [--port <port>] [--baud <baud>]`
* **หน้าที่:** เปิดหน้าต่างดู Serial Monitor คอนโซลสดจากตัวบอร์ด
* **ตัวเลือก (Flags):**
  * `--port`: ระบุพอร์ต COM (ถ้าไม่ใส่จะค้นหาให้อัตโนมัติ)
  * `--baud`: ความเร็ว Baud rate (ค่าเริ่มต้น: `115200`)
* **ตัวอย่าง:**
  ```bash
  nex monitor --port COM5 --baud 115200
  ```

#### 10. `nex clean`
* **หน้าที่:** ทำความสะอาดไดเรกทอรี `build/`
* **ตัวอย่าง:**
  ```bash
  nex clean
  ```

#### 11. `nex doctor [-t <target>]`
* **หน้าที่:** ตรวจสอบความสมบูรณ์ทั้งระบบ Ecosystem (Python, Git, Target Definitions, ESP32-C6 Reference Integrity, Core Headers ปราศจากการปนเปื้อน Header เฉพาะค่าย, Toolchains, และ Packaging Tools) หรือระบุ Target เพื่อเจาะลึกเฉพาะชิปนั้น
* **ตัวเลือก (Flags):**
  * `-t, --target`: แพลตฟอร์มเป้าหมาย เช่น `esp32-c6`, `rp2040`, `pico-w`, `host`
* **ตัวอย่าง:**
  ```bash
  nex doctor
  nex doctor -t esp32-c6
  nex doctor -t rp2040
  nex doctor -t pico-w
  ```

---

## 🖥️ 8. การใช้งาน NexOS Developer Studio (Web Mission Control)

NexOS Developer Studio คือศูนย์ควบคุมฮาร์ดแวร์ผ่านหน้าเว็บ (Hardware Mission Control & Live Serial Monitor) เพื่ออำนวยความสะดวกในการตรวจจับและดูการทำงานของบอร์ด:

### วิธีเปิดใช้งาน:
1. เปิด Terminal ในโฟลเดอร์โปรเจกต์ แล้วรันคำสั่ง:
   ```bash
   python nexos-developer/server.py
   ```
2. เปิดเว็บบราวเซอร์ไปที่: **[http://localhost:8088](http://localhost:8088)**

### เมนูและเครื่องมือบนหน้าเว็บ:
1. **Target Dashboard (หน้าจอหลัก):**
   * **Smart Auto-Discovery:** ตรวจจับบอร์ดอัตโนมัติผ่าน USB VID:PID ทันทีที่เสียบสาย USB
   * **Hardware Inspection Card:** แสดงสเปกจริงของชิปที่กำลังเชื่อมต่อ (CPU Architecture, Clock Speed, RAM, Flash, Active Capabilities)
   * **Action Controls:** ปุ่ม `Flash OS`, ปุ่ม `Build`, และปุ่ม `Run on Host`
   * **Build & Diagnostics Console:** กล่องข้อความแสดงผลการคอมไพล์และการเชื่อมต่อแบบ Real-time
2. **Live Serial Monitor (หน้าต่างเทอร์มินัล):**
   * หน้าต่าง Terminal ขนาดใหญ่ยาวเต็มความสูงหน้าจอ (Full Viewport Height)
   * รองรับการรับ-ส่งข้อความ (TX/RX) และคำสั่ง Interactive กับตัวบอร์ดที่ความเร็ว 115,200 Baud
   * ระบบกรองเฉพาะพอร์ต Serial จริง (ป้องกันการต่อเข้า Drive ผิดพลาด)
   * มีตัวเลือก Auto-scroll และปุ่ม Clear หน้าจอ
3. **NexOS Doctor (เครื่องมือวิเคราะห์ระบบ):**
   * ตรวจเช็คความสมบูรณ์ของสภาพแวดล้อมการพัฒนา, Toolchains, SDK, และคอมไพเลอร์ในเครื่องของคุณ

---

## 💻 9. ขั้นตอนการพัฒนาแอปพลิเคชันด้วย IDE ภายนอก (VS Code / CLion)

คุณสามารถใช้โปรแกรมแก้ไขโค้ดที่คุณคุ้นเคย เช่น **Visual Studio Code, CLion, หรือ Cursor** ในการพัฒนาแอปพลิเคชัน NexOS ได้อย่างเต็มประสิทธิภาพ:

1. **เปิดโฟลเดอร์โปรเจกต์ใน VS Code:**
   * เปิดโฟลเดอร์โปรเจกต์ของคุณใน VS Code เพื่อใช้งาน C/C++ IntelliSense, Code Navigation, และระบบตรวจจับไวยากรณ์
2. **แก้ไขโค้ดใน `main.c` และกำหนดสิทธิ์ใน `nexos.json` / `nexos.toml`:**
   * โค้ดทั้งหมดจะเรียกใช้ API ผ่าน `#include <nexos.h>` เท่านั้น
3. **เปิด Integrated Terminal ใน VS Code:**
   * สั่งคอมไพล์: `nexos build` หรือ `nex build --target esp32-c6`
   * สั่งทดสอบบนคอมพิวเตอร์: `nex run --target host`
4. **นำไฟล์ `.app` ไปใช้งาน:**
   * สั่ง `nexos install dist/my_app.app` เพื่อนำไฟล์ไปวางใน MicroSD Card แล้วนำไปเสียบบอร์ดจริง

---

## 🧪 10. การทดสอบด้วยระบบจำลอง (Host PC Simulator)

คุณสามารถพัฒนาและทดสอบตรรกะของโปรแกรมได้ทันทีโดย **ไม่ต้องมีบอร์ดฮาร์ดแวร์จริงต่ออยู่**:

```bash
nex run --target host
```

> [!TIP]
> **สำหรับผู้ใช้ PowerShell บน Windows:**
> หากรันคำสั่งจากโฟลเดอร์โปรเจกต์โดยตรง ให้พิมพ์ **`.\nex`** (มี `.\` นำหน้าตามมาตรฐานความปลอดภัยของ PowerShell) เช่น:
> ```powershell
> .\nex run --target host
> ```
> หรือสั่งผ่าน Python ตรงๆ: `python tools/nex/nex.py run --target host`
> หรือติดตั้งตัวติดตั้ง [NexOS-Developer-Setup.exe](dist_installer/NexOS-Developer-Setup.exe) เพื่อให้พิมพ์ `nex` ได้จากทุกที่โดยไม่ต้องมี `.\`

ระบบจะคอมไพล์แอปพลิเคชันเข้ากับชั้นจำลอง **Host Architecture (x86_64)** และจำลองสัญญาณ SysTick, สัญญาณนาฬิกา, และพิน GPIO เสมือน พร้อมพิมพ์ Log ออกมาทางหน้าจอคอนโซลทันที เหมาะอย่างยิ่งสำหรับการเขียน Unit Test และการทำ CI/CD Automated Pipelines

---

## 📂 11. โครงสร้างไดเรกทอรีของโปรเจกต์ (Directory Structure)

```text
NexOS/
├── core/                  # แกนกลางระบบปฏิบัติการ (Hardware-Independent)
│   ├── kernel/            # Kernel Lifecycle & Initialization
│   ├── scheduler/         # Priority Preemptive Task Scheduler
│   ├── task/              # Task Control Blocks (TCB) & Context
│   ├── memory/            # Slab Allocator & Safe Heap Pool
│   ├── synchronization/   # Mutexes, Semaphores, Event Groups
│   ├── ipc/               # Message Queues & Ring Buffers
│   ├── filesystem/        # Virtual File System (VFS)
│   ├── loader/            # .app Binary Loader & Relocator
│   └── security/          # SHA-256 & Signature Verification
│
├── hal/                   # Hardware Abstraction Layer Interfaces
│   └── include/           # GPIO, UART, SPI, I2C, PWM, ADC, Timer, Power
│
├── arch/                  # Architecture-Specific Context Switching
│   ├── riscv/             # RISC-V 32-bit (ESP32-C6)
│   ├── arm/               # ARM Cortex-M0+/M4 (RP2040, STM32)
│   ├── xtensa/            # Xtensa LX6/LX7/LX106 (ESP32, S3, 8266)
│   ├── avr/               # 8-bit AVR (Arduino ATmega328P)
│   └── host/              # Native x86_64 Simulation
│
├── targets/               # นิยามฮาร์ดแวร์เป้าหมาย (target.json) ทั้ง 9 แพลตฟอร์ม
├── platforms/             # โค้ดคอมไพล์เฟิร์มแวร์เฉพาะบอร์ด (esp32c6, rp2040, host)
├── sdk/                   # SDK สำหรับผู้พัฒนาแอปพลิเคชัน
│   ├── include/nexos.h    # Header API หลักที่ผู้พัฒนาใช้งาน
│   ├── abi/               # Syscall Client Trampolines
│   └── examples/          # โปรเจกต์ตัวอย่าง (Blinky, Multitask, Sensor, Shell)
│
├── nexos-developer/       # NexOS Developer Studio (Mission Control Web GUI)
│   ├── server.py          # Local REST API & Serial Streaming Backend
│   └── gui/               # หน้าเว็บ Dark-Mode Frontend (HTML/CSS/JS)
│
├── tools/                 # ชุดเครื่องมือ CLI และเฟิร์มแวร์เจเนอเรเตอร์
│   ├── nexos/             # คำสั่ง nexos และตัวสร้างไบนารีบูต
│   ├── nex/               # คำสั่ง nex สำหรับบริหารจัดการฮาร์ดแวร์และมอนิเตอร์
│   └── nexpack/           # ตัวแพ็กเกจไฟล์ .app
│
├── templates/             # แม่แบบโปรเจกต์เริ่มต้นสำหรับการสร้างแอปใหม่
├── installer/             # ตัวติดตั้ง Windows Installer (.iss และ build script)
└── tests/                 # ชุดทดสอบอัตโนมัติ (Automated Tests Suite)
```

---

## ❓ 12. การแก้ปัญหาที่พบบ่อย (Troubleshooting & FAQ)

### Q: เกิดข้อผิดพลาด `PermissionError: [Errno 13] Access is denied: 'COM3'` เวลา Flash
* **สาเหตุ:** พอร์ต COM กำลังถูกโปรแกรมอื่นใช้งานอยู่ เช่น Serial Monitor ของ Arduino IDE, PuTTY หรือหน้าต่างเซิร์ฟเวอร์เดิมที่เปิดค้างไว้
* **วิธีแก้:** ปิดโปรแกรมอื่นที่เปิดพอร์ต Serial ค้างไว้ หรือกดปุ่ม Disconnect ใน Serial Monitor ก่อนกด Flash

### Q: เสียบบอร์ด ESP32-C6 แล้ว Flash ขึ้นข้อความ `Failed to connect: No serial data received`
* **สาเหตุ:** ตัวชิปไม่ได้อยู่ใน Download Mode
* **วิธีแก้:** ใช้นิ้ว **กดปุ่ม `BOOT` บนบอร์ด ESP32-C6 ค้างไว้** แล้วกดปุ่ม `RST/EN` 1 ครั้ง จากนั้นปล่อยปุ่ม `BOOT` บอร์ดจะเข้าสู่ Download Mode พร้อมให้ Flash ทันที

### Q: เสียบ Raspberry Pi Pico แล้วหน้าเว็บไม่เห็นพอร์ต COM หรือไดรฟ์ RPI-RP2 ไม่ขึ้น
* **สาเหตุ:** ไม่ได้กดปุ่มบูตก่อนเสียบสาย USB
* **วิธีแก้:** ถอดสาย USB ออก กดปุ่มสีขาว **`[ BOOTSEL ]`** ค้างไว้ แล้วเสียบสาย USB กลับเข้าคอมพิวเตอร์ ไดรฟ์ `RPI-RP2` จะเด้งขึ้นมาให้ลากไฟล์ `.uf2` ได้ทันที

### Q: ทำไมในไดรฟ์ `RPI-RP2` ของ Pico ถึงไม่มีไฟล์ `.uf2` อยู่เลยหลังจากวางลงไปแล้ว?
* **คำตอบ:** ไดรฟ์ `RPI-RP2` เป็น **ไดรฟ์รับไฟล์ชั่วคราว (Virtual Bootloader)** เมื่อคุณลากไฟล์ `.uf2` ใส่ลงไป ชิปจะดูดข้อมูลไปเขียนลง Flash ทันที แล้วไดรฟ์จะปิดตัวลงเพื่อรีบูตเข้าสู่ระบบปฏิบัติการ ตัวไฟล์จึงไม่ได้ค้างอยู่ในไดรฟ์ ซึ่งเป็นการทำงานที่ถูกต้องตามปกติของ Raspberry Pi ครับ

### Q: วันที่ในบันทึกบูต `ESP-ROM: ... Build:Sep 19 2022` คือวันที่อะไร?
* **คำตอบ:** คือวันที่บริษัท Espressif (ผู้ผลิตชิป) ทำการหล่อโค้ด ROM Bootloader ฝังลงในผลึกซิลิคอนของชิปจากโรงงาน เป็นค่าถาวรของฮาร์ดแวร์ตัวชิป ไม่ใช่วันที่ปัจจุบันของระบบ NexOS

---

## 📄 13. ใบอนุญาตการใช้งาน (License)

NexOS ได้รับการเผยแพร่ภายใต้ใบอนุญาต **MIT License** — สามารถนำไปศึกษา ดัดแปลง ใช้งานเชิงพาณิชย์ และพัฒนาต่อยอดได้อย่างอิสระ

---

## 📚 14. งานวิจัยและเอกสารอ้างอิง (Research & References)

ดูรายการงานวิจัยระดับนานาชาติ (ACM / IEEE / USENIX) และบทความทางวิศวกรรมที่ใช้เทียบเคียงสถาปัตยกรรมของ NexOS ฉบับสมบูรณ์พร้อมลิงก์ดาวน์โหลดและอ่านเปเปอร์ได้ที่:
👉 **[คู่มืองานวิจัยและเอกสารอ้างอิง (docs/RESEARCH_AND_REFERENCES.md)](docs/RESEARCH_AND_REFERENCES.md)**

