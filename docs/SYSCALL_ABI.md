# การเชื่อมต่อ System Call และเอกสารอ้างอิง ABI ของ NexOS (v1)

แอปพลิเคชันทั้งหมดที่เขียนสำหรับ NexOS จะติดต่อและขอรับบริการจากเคอร์เนลผ่าน **ตาราง System Call Dispatch** (`nex_syscall_table_t`) เท่านั้น

---

## 1. ข้อตกลงการเรียกใช้ฟังก์ชัน (Calling Convention)

เมื่อตัวโหลดแอปพลิเคชันของ NexOS เริ่มต้นรันแอปพลิเคชัน จะเรียกใช้ฟังก์ชันทางเข้าที่เป็นแทรมโพลีน (Trampoline):
```c
int _nex_app_start(const nex_syscall_table_t *table);
```
พารามิเตอร์ `table` จะถูกส่งผ่านรีจิสเตอร์ `a0` ของสถาปัตยกรรม RISC-V (ตามมาตรฐาน RISC-V Calling Convention)
ตัวแทรมโพลีนจะทำการบันทึกแอดเดรสนี้ไว้ในพอยน์เตอร์ `g_nex_syscall_table` จากนั้นการเรียกใช้ฟังก์ชัน SDK ต่างๆ จะทำการส่งคำสั่งผ่าน Function Pointer ภายในตารางได้ทันที โดยไม่มี Overhead ของการทำ Context-Switching

---

## 2. รายการคำสั่งในตาราง Syscall Dispatch Vector

### งานและระบบทั่วไป (System & Tasks)
| สมาชิก | รูปแบบฟังก์ชัน (Signature) | คำอธิบาย |
| :--- | :--- | :--- |
| `sys_log` | `void (*)(const char *tag, const char *msg)` | บันทึกข้อความ Log ไปยังพอร์ตซีเรียลและหน้าต่างดีบัก |
| `sys_delay_ms` | `void (*)(uint32_t ms)` | สั่งหน่วงเวลาเป็นมิลลิวินาที |
| `sys_time_get_ms` | `uint32_t (*)(void)` | อ่านเวลาปัจจุบันเป็นมิลลิวินาทีนับตั้งแต่เริ่มเปิดเครื่อง |
| `sys_task_sleep_ms` | `void (*)(uint32_t ms)` | พักการทำงานของ Task ตามเวลาที่กำหนด |
| `sys_task_yield` | `void (*)(void)` | คืนการประมวลผลให้ Task อื่นที่มีลำดับความสำคัญพร้อมทำงาน |
| `sys_malloc` | `void* (*)(size_t size)` | จัดสรรหน่วยความจำ Heap จากโควตาของแอปพลิเคชัน |
| `sys_free` | `void (*)(void *ptr)` | คืนหน่วยความจำ Heap ที่เคยจองไว้ |
| `sys_device_has` | `bool (*)(uint32_t cap)` | ตรวจสอบขีดความสามารถของฮาร์ดแวร์เป้าหมาย |
| `sys_app_exit` | `void (*)(int exit_code)` | จบการทำงานของแอปพลิเคชันและแจ้งเคอร์เนลให้คืนทรัพยากร |

### อุปกรณ์ฮาร์ดแวร์และพอร์ตสื่อสาร (Hardware & Peripherals - ควบคุมด้วย Permissions)
| สมาชิก | รูปแบบฟังก์ชัน (Signature) | สิทธิ์ที่ต้องได้รับอนุมัติ |
| :--- | :--- | :--- |
| `sys_gpio_mode` | `nex_err_t (*)(uint32_t pin, uint32_t mode)` | `gpio = true` |
| `sys_gpio_write` | `nex_err_t (*)(uint32_t pin, uint32_t level)` | `gpio = true` |
| `sys_gpio_read` | `uint32_t (*)(uint32_t pin)` | `gpio = true` |
| `sys_gpio_toggle`| `nex_err_t (*)(uint32_t pin)` | `gpio = true` |
| `sys_uart_write` | `nex_err_t (*)(uint8_t port, const uint8_t *data, size_t len)` | `uart = true` |
| `sys_uart_read` | `nex_err_t (*)(uint8_t port, uint8_t *data, size_t len, size_t *rcvd, uint32_t timeout)` | `uart = true` |
