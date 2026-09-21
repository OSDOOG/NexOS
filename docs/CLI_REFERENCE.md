# คู่มือการใช้คำสั่ง NexOS CLI (`nex`)

อินเทอร์เฟซคอมมานด์ไลน์ `nex` ใช้สำหรับจัดการโปรเจกต์, แพลตฟอร์มเป้าหมาย, ทูลเชนคอมไพเลอร์, การจำลองบน Host PC และการตรวจสอบระบบ

```bash
nex <command> [options]
```

---

## 1. การจัดการแพลตฟอร์มเป้าหมาย (Target Management)

### `nex targets`
แสดงรายการบอร์ดฮาร์ดแวร์เป้าหมายทั้งหมดที่ลงทะเบียนไว้ พร้อมสถาปัตยกรรม, ชนิด CPU, ขนาด RAM, โปรไฟล์ OS และรูปแบบไฟล์ไบนารีผลลัพธ์

```bash
nex targets
```

### `nex target info <target_id>`
แสดงข้อมูลสเปกโดยละเอียดของแพลตฟอร์ม, การกำหนดพิน, การตั้งค่าทูลเชน และบิตมาสก์ของขีดความสามารถฮาร์ดแวร์

```bash
nex target info esp32-c6
nex target info rp2040
```

---

## 2. การสร้างโปรเจกต์และการคอมไพล์ (Project Creation & Compilation)

### `nex create <app_name>`
สร้างโครงสร้างแอปพลิเคชัน NexOS ใหม่ พร้อมไฟล์ Manifest `nexos.json` และโค้ดเริ่มต้น `main.c`

```bash
nex create my_sensor
```

### `nex build --target <target_id>`
คอมไพล์ซอร์สโค้ดของแอปพลิเคชันสำหรับบอร์ดฮาร์ดแวร์เป้าหมายที่เลือก

```bash
nex build --target esp32-c6
nex build --target rp2040
nex build --target arduino-avr
```

### `nex clean`
ลบไฟล์ผลลัพธ์การบิลด์ทั้งหมดในโฟลเดอร์ `build/`

---

## 3. ตัวจำลอง Host Simulator และการแฟลชโปรแกรม

### `nex run --target host`
คอมไพล์และรันแอปพลิเคชันบน Windows ทันทีผ่านระบบจำลอง Host Simulation Platform

```bash
nex run --target host
```

### `nex flash --target <target_id> [--port <port>]`
แฟลชไฟล์ไบนารีลงในชิปฮาร์ดแวร์จริง ผ่านเครื่องมือแฟลชประจำชิปนั้นๆ เช่น `esptool.py`, `picotool`, `avrdude`, `st-flash`

```bash
nex flash --target esp32-c6 --port COM3
```

### `nex monitor [--port <port>] [--baud <baud>]`
เปิดหน้าต่างมอนิเตอร์พอร์ตซีเรียลสำหรับดู Log จากบอร์ด

```bash
nex monitor --port COM3 --baud 115200
```

---

## 4. การตรวจสอบระบบและทูลเชนคอมไพเลอร์ (Diagnostics & Toolchains)

### `nex doctor`
ตรวจสอบความพร้อมของระบบ สภาพแวดล้อม Python, Node, Git, ความสมบูรณ์ของ Header ใน Core ตลอดจนคอมไพเลอร์ข้ามสถาปัตยกรรม (Cross-compilers)

```bash
nex doctor
```

### `nex toolchain list`
แสดงรายการ Cross-compiler ทั้งหมดที่ตรวจพบในเครื่องและที่ยังขาดอยู่ (`riscv-none-elf-gcc`, `xtensa-esp32-elf-gcc`, `arm-none-eabi-gcc`, `avr-gcc`)

```bash
nex toolchain list
```
