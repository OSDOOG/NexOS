# ข้อกำหนดรูปแบบแพ็กเกจแอปพลิเคชัน NexOS (.app)

**เวอร์ชันรูปแบบ**: 1.0  
**ไบต์เวทมนตร์ (Magic Bytes)**: `\x7FNEXAPP\x01` (8 ไบต์)  
**ขนาดส่วนหัว (Header Size)**: คงที่ 128 ไบต์  
**เพย์โหลด (Payload)**: ไบนารีเนทีฟที่ย้ายตำแหน่งได้ (Relocatable Native Binary)  

---

## 1. ผังโครงสร้างไบนารี (Binary Layout)

```text
+-------------------------------------------------------------+
|             ส่วนหัวคงที่ขนาด 128 ไบต์ (Header Metadata)       |
+-------------------------------------------------------------+
|             เซกชัน .text (โค้ดคำสั่งที่ประมวลผลได้)             |
+-------------------------------------------------------------+
|             เซกชัน .data (ข้อมูลคงที่ที่กำหนดค่าเริ่มต้นไว้)     |
+-------------------------------------------------------------+
|             [ไฟล์ทรัพยากรคงที่ / ทรัพยากรเพิ่มเติม (ถ้ามี)]     |
+-------------------------------------------------------------+
```

---

## 2. นิยามโครงสร้างส่วนหัว (Header Structure - 128 Bytes)

```c
#pragma pack(push, 1)
typedef struct {
    uint8_t  magic[8];              /* 0x00: ไบต์ตรวจสอบความถูกต้อง \x7FNEXAPP\x01 */
    uint16_t format_version;        /* 0x08: เวอร์ชันของรูปแบบแพ็กเกจ (1) */
    uint16_t abi_version;           /* 0x0A: เวอร์ชัน ABI ของ NexOS (1) */
    uint16_t target_arch;           /* 0x0C: สถาปัตยกรรม CPU (1 = RISC-V 32-bit) */
    uint16_t target_chip;           /* 0x0E: ชิปไมโครคอนโทรลเลอร์เป้าหมาย (1 = ESP32-C6) */
    uint8_t  min_nexos_ver[4];      /* 0x10: เวอร์ชันขั้นต่ำของ OS [major, minor, patch, 0] */
    char     app_name[32];          /* 0x14: ชื่อแอปพลิเคชัน (สิ้นสุดด้วย null) */
    char     app_version[16];       /* 0x34: ข้อความระบุเวอร์ชัน (เช่น "1.0.0") */
    uint32_t entry_offset;          /* 0x44: ออฟเซ็ตของจุดเริ่มต้นฟังก์ชันจากท้าย Header (0) */
    uint32_t code_size;             /* 0x48: ขนาดของโค้ดคำสั่งในเซกชัน .text (ไบต์) */
    uint32_t data_size;             /* 0x4C: ขนาดของข้อมูลในเซกชัน .data (ไบต์) */
    uint32_t bss_size;              /* 0x50: ขนาดของหน่วยความจำเซกชัน .bss (ไบต์) */
    uint32_t stack_size;            /* 0x54: ขนาด Stack ที่ต้องการใช้งาน (เช่น 4096 ไบต์) */
    uint32_t heap_size;             /* 0x58: โควตา Heap ที่แอปพลิเคชันต้องการ (เช่น 8192 ไบต์) */
    uint32_t permissions;           /* 0x5C: บิตมาสก์ของสิทธิ์การเข้าถึงฮาร์ดแวร์ */
    uint8_t  checksum[32];          /* 0x60: ค่าแฮช SHA-256 ของเพย์โหลด (code + data) */
} nex_app_header_t;
#pragma pack(pop)
```

---

## 3. รหัสระบุสถาปัตยกรรม CPU (Architecture Identifiers)

| รหัส (ID) | ชื่อสถาปัตยกรรม | ชุดคำสั่ง (Instruction Set) |
| :--- | :--- | :--- |
| `1` | `RISC-V 32-bit` | RV32IMAC / ilp32 (ESP32-C6) |
| `2` | `Xtensa` | LX106 / LX6 / LX7 (ESP8266, ESP32) |
| `3` | `ARM Cortex-M0+`| ARMv6-M (RP2040, Raspberry Pi Pico) |
| `4` | `ARM Cortex-M4` | ARMv7E-M พร้อม FPU (STM32) |
| `5` | `AVR 8-bit` | AVR (ATmega328P) |
| `6` | `Host x86_64` | AMD64 / Intel 64 Native Simulation |

---

## 4. บิตมาสก์การขอสิทธิ์ฮาร์ดแวร์ (Permissions Bitmask)

```c
#define NEX_APP_PERM_GPIO       (1U << 0)
#define NEX_APP_PERM_UART       (1U << 1)
#define NEX_APP_PERM_I2C        (1U << 2)
#define NEX_APP_PERM_SPI        (1U << 3)
#define NEX_APP_PERM_STORAGE    (1U << 4)
#define NEX_APP_PERM_NETWORK    (1U << 5)
#define NEX_APP_PERM_DISPLAY    (1U << 6)
#define NEX_APP_PERM_ADC        (1U << 7)
```
ค่าเหล่านี้จะถูกระบุในไฟล์ `nexos.toml` และได้รับการตรวจสอบโดยตัวครอบคำสั่งเคอร์เนล (Syscall Wrappers) ก่อนการเข้าถึงพินหรือบัสสื่อสารจริงเสมอ
