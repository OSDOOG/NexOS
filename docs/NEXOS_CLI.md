# คู่มือการใช้งาน NexOS Developer CLI (`nexos`)

เครื่องมือคอมมานด์ไลน์ `nexos` ทำหน้าที่เป็นศูนย์กลางในการสร้างโปรเจกต์ คอมไพล์ แพ็กเกจแอปพลิเคชัน ตรวจสอบความถูกต้อง และจัดการแอปพลิเคชัน NexOS

---

## คำสั่งทั้งหมด (Commands)

### `nexos create <name>`
สร้างโครงร่างโปรเจกต์แอปพลิเคชันใหม่ พร้อมไฟล์ `nexos.toml`, `src/main.c`, `include/config.h`, `resources/` และ `tests/`

```bash
nexos create sensor_app
```

---

### `nexos build [--release]`
คอมไพล์โค้ดภาษา C ของแอปพลิเคชันและสร้างแพ็กเกจเป็นไฟล์ `dist/<name>.app`
- ค่าเริ่มต้น (Default): โหมด Debug (เปิดข้อมูล Symbols และการบันทึก Log สำหรับดีบัก)
- ออปชัน `--release`: โหมด Release (เปิดการปรับแต่งความเร็วระดับ `-O2` สำหรับใช้งานจริง)

```bash
nexos build
nexos build --release
```

---

### `nexos clean`
ลบโฟลเดอร์ผลลัพธ์การบิลด์ `build/` และ `dist/`

```bash
nexos clean
```

---

### `nexos rebuild [--release]`
ล้างไฟล์บิลด์เก่าและคอมไพล์แอปพลิเคชันใหม่ทั้งหมดในคำสั่งเดียว

```bash
nexos rebuild --release
```

---

### `nexos validate <file.app>`
ตรวจสอบความถูกต้องและความสมบูรณ์ของแพ็กเกจแอปพลิเคชันอย่างละเอียด:
- ไบต์ตรวจสอบความถูกต้องของส่วนหัว (Magic Bytes: `\x7FNEXAPP\x01`)
- ความเข้ากันได้ของเวอร์ชันรูปแบบแพ็กเกจและเวอร์ชัน ABI
- ความตรงกันของสถาปัตยกรรม CPU และรหัสชิป SoC
- การตรวจสอบความสมบูรณ์ของเพย์โหลดด้วย SHA-256
- ข้อกำหนดด้านหน่วยความจำ (Stack และ Heap)
- การประกาศขอสิทธิ์การใช้งานฮาร์ดแวร์

```bash
nexos validate dist/hello.app
```

---

### `nexos info <file.app>`
แสดงข้อมูลเมทาดาตา ส่วนหัว ขนาดไฟล์ และสิทธิ์ที่แอปพลิเคชันขอใช้งาน

```bash
nexos info dist/hello.app
```

---

### `nexos size [file.app]`
แสดงการแจกแจงขนาดการใช้หน่วยความจำของโค้ดคำสั่ง, ข้อมูล, BSS ตลอดจนขนาด Stack และ Heap

```bash
nexos size
```

---

### `nexos doctor`
ตรวจสอบสภาพแวดล้อมของเครื่องคอมพิวเตอร์สำหรับการพัฒนา:
- เวอร์ชันของระบบปฏิบัติการ
- เวอร์ชันของ NexOS CLI และ NexOS SDK
- คอมไพเลอร์ RISC-V GCC (`riscv32-esp-elf-gcc` / `riscv-none-elf-gcc`)
- ชุดโปรแกรม Binutils (`objcopy`, `objdump`, `readelf`)
- เครื่องมือ CMake และ Ninja
- การติดตั้ง Python และ Git
- การตั้งค่าตัวแปรสภาพแวดล้อม PATH

```bash
nexos doctor
```

---

### `nexos install <file.app>`
ติดตั้งไฟล์แพ็กเกจ `.app` ลงในโฟลเดอร์ `/apps/` ของ MicroSD Card หรือพื้นที่จำลอง

```bash
nexos install dist/hello.app
```

---

### `nexos list`
แสดงรายชื่อแอปพลิเคชันทั้งหมดที่ติดตั้งอยู่บน MicroSD Card

```bash
nexos list
```

---

### `nexos uninstall <name>`
ถอนการติดตั้งและลบไฟล์แอปพลิเคชันออกจาก MicroSD Card

```bash
nexos uninstall hello
```

---

### `nexos version`
แสดงเวอร์ชันของ NexOS CLI, SDK และเวอร์ชัน ABI ปัจจุบัน

```bash
nexos version
```
