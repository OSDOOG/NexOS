# ตารางคุณสมบัติแพลตฟอร์มที่รองรับบน NexOS (Supported Targets)

| รหัส Target | ชิป SoC / MCU | สถาปัตยกรรม | แกนประมวลผล CPU | ขนาด RAM | ขนาด Flash | ฟอร์แมตไฟล์ | โปรไฟล์ OS | สถานะ |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `esp32-c6` | ESP32-C6 | RISC-V | RV32IMAC @ 160MHz | 512 KB | 4 MB | `.bin` / `.app` | Advanced | **แพลตฟอร์มอ้างอิง (Reference Platform)** |
| `rp2040` | RP2040 | ARM | Dual Cortex-M0+ | 264 KB | 2 MB | `.uf2` | Standard | รองรับการใช้งาน |
| `pico-w` | RP2040 + CYW43 | ARM | Dual Cortex-M0+ | 264 KB | 2 MB | `.uf2` | Standard | รองรับการใช้งาน |
| `esp8266` | ESP8266EX | Xtensa | LX106 | 80 KB | 4 MB | `.bin` | Standard | รองรับการใช้งาน |
| `esp32` | ESP32-D0WD | Xtensa | Dual LX6 | 520 KB | 4 MB | `.bin` | Advanced | รองรับการใช้งาน |
| `esp32-s3` | ESP32-S3 | Xtensa | Dual LX7 | 512 KB | 8 MB | `.bin` | Advanced | รองรับการใช้งาน |
| `arduino-avr`| ATmega328P | AVR | 8-bit AVR | 2 KB | 32 KB | `.hex` | Micro | รองรับการใช้งาน (NexOS Micro) |
| `stm32` | STM32F401/411 | ARM | Cortex-M4 with FPU | 128 KB | 512 KB | `.bin` | Advanced | รองรับการใช้งาน |
| `host` | PC Native | Host | x86_64 | 16 MB | 64 MB | `.exe` | Advanced | **ตัวจำลองบนคอมพิวเตอร์ (Desktop Simulator)** |
