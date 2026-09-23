# 📚 เอกสารงานวิจัยและบทความทางวิศวกรรมที่เกี่ยวข้องกับ NexOS (Related Research & References)

เอกสารฉบับนี้รวบรวมงานวิจัยระดับนานาชาติ (Academic Papers) จากสมาคมวิชาการชั้นนำ (ACM, IEEE, USENIX) และบทความทางวิศวกรรมระบบปฏิบัติการที่ใช้เป็นรากฐานอ้างอิงและเทียบเคียงกับสถาปัตยกรรมของ **NexOS Micro-Kernel RTOS**

---

## 📑 สารบัญ (Table of Contents)
1. [งานวิจัยสถาปัตยกรรม Micro-Kernel & Process Isolation บน MCU](#1-งานวิจัยสถาปัตยกรรม-micro-kernel--process-isolation-บน-mcu)
2. [งานวิจัยการโหลดและรีโลเคตโค้ดเนทีฟบนชิปไร้ MMU (Dynamic Loading & Relocation)](#2-งานวิจัยการโหลดและรีโลเคตโค้ดเนทีฟบนชิปไร้-mmu-dynamic-loading--relocation)
3. [งานวิจัยด้าน Capability-based Security & สถาปัตยกรรม RISC-V](#3-งานวิจัยด้าน-capability-based-security--สถาปัตยกรรม-risc-v)
4. [งานวิจัยสำรวจระบบปฏิบัติการสมองกลฝังตัว (Surveys on Embedded / IoT OS)](#4-งานวิจัยสำรวจระบบปฏิบัติการสมองกลฝังตัว-surveys-on-embedded--iot-os)
5. [บทความและสถาปัตยกรรมอ้างอิงระดับอุตสาหกรรม (Industry Reference Architectures)](#5-บทความและสถาปัตยกรรมอ้างอิงระดับอุตสาหกรรม-industry-reference-architectures)

---

## 1. งานวิจัยสถาปัตยกรรม Micro-Kernel & Process Isolation บน MCU

### 📌 1.1 Tock OS: Multiprogramming a 64kB Computer Safely and Efficiently
* **ผู้แต่ง:** Amit Levy, Bradford Campbell, Branden Ghena, Daniel B. Giffin, Pat Pannuto, Prabal Dutta, Philip Levis
* **ตีพิมพ์ใน:** ACM SOSP 2017 (26th ACM Symposium on Operating Systems Principles)
* **ความเกี่ยวข้องกับ NexOS:** อธิบายการแยกส่วนแอปพลิเคชัน (Userland Processes) ออกจากตัวเคอร์เนลของไมโครคอนโทรลเลอร์ขนาดเล็ก และการสื่อสารผ่าน System Call ซึ่งตรงกับสถาปัตยกรรม 3-Tier ของ NexOS
* **ลิงก์:**
  * 📄 **อ่านเปเปอร์ฉบับเต็ม (PDF):** [https://www.tockos.org/assets/papers/tock-sosp2017.pdf](https://www.tockos.org/assets/papers/tock-sosp2017.pdf)
  * 🔗 **ACM Digital Library:** [https://dl.acm.org/doi/10.1145/3132747.3132786](https://dl.acm.org/doi/10.1145/3132747.3132786)
  * 🌐 **เว็บไซต์ทางการ:** [https://www.tockos.org/](https://www.tockos.org/)
  * 💻 **GitHub Repository:** [https://github.com/tock/tock](https://github.com/tock/tock)

### 📌 1.2 SOS: An Operating System for Embedded Sensor Networks
* **ผู้แต่ง:** Chih-Chieh (Simon) Han, Ram Kumar, Roy Shea, Eddie Kohler, Mani Srivastava (UCLA)
* **ตีพิมพ์ใน:** ACM MobiSys 2005 (3rd International Conference on Mobile Systems, Applications, and Services)
* **ความเกี่ยวข้องกับ NexOS:** นำเสนอแนวคิด **Flash Core OS เพียงครั้งเดียว** แล้วปล่อยให้ผู้ใช้โหลด Native Binary Modules เข้ามารันและปลดออกได้แบบ Dynamic ตลอดเวลาโดยไม่ต้องต่อสาย Re-flash ชิปใหม่
* **ลิงก์:**
  * 📄 **อ่านเปเปอร์ฉบับเต็ม (USENIX PDF):** [https://www.usenix.org/legacy/event/mobisys05/tech/full_papers/han/han.pdf](https://www.usenix.org/legacy/event/mobisys05/tech/full_papers/han/han.pdf)
  * 🔗 **ACM Digital Library:** [https://dl.acm.org/doi/10.1145/1067178.1067205](https://dl.acm.org/doi/10.1145/1067178.1067205)

---

## 2. งานวิจัยการโหลดและรีโลเคตโค้ดเนทีฟบนชิปไร้ MMU (Dynamic Loading & Relocation)

### 📌 2.1 Contiki OS: Run-Time Dynamic Linking for Reprogramming Distributed Systems
* **ผู้แต่ง:** Adam Dunkels, Niclas Finne, Joakim Eriksson, Thiemo Voigt
* **ตีพิมพ์ใน:** ACM SenSys 2006 (4th ACM Conference on Embedded Networked Sensor Systems)
* **ความเกี่ยวข้องกับ NexOS:** นำเสนอเทคนิคการทำ Dynamic Linking & Relocation บนไมโครคอนโทรลเลอร์ที่ไม่มี MMU โดยชี้ให้เห็นว่าการรันโค้ดเนทีฟแบบจัดสรรหน่วยความจำ SRAM ให้ประสิทธิภาพความเร็วและความประหยัดพลังงานสูงกว่าการใช้ Bytecode Virtual Machine (Lua/Wasm) หลายสิบเท่า (สอดคล้องกับเอกสารการวิเคราะห์ `docs/APPLICATION_RUNTIME_ANALYSIS.md` ของ NexOS)
* **ลิงก์:**
  * 📄 **อ่านเปเปอร์ฉบับเต็ม (PDF):** [https://dunkels.com/adam/dunkels06run-time.pdf](https://dunkels.com/adam/dunkels06run-time.pdf)
  * 🔗 **ACM Digital Library:** [https://dl.acm.org/doi/10.1145/1182807.1182810](https://dl.acm.org/doi/10.1145/1182807.1182810)
  * 💻 **Contiki-NG GitHub:** [https://github.com/contiki-ng/contiki-ng](https://github.com/contiki-ng/contiki-ng)

### 📌 2.2 uClinux and Binary Flat (bFLT) Executable Format
* **ผู้แต่ง / บทความ:** D. McCullough, *"uClinux for Linux without an MMU"* (Linux Journal)
* **ความเกี่ยวข้องกับ NexOS:** โครงสร้างไฟล์แพ็กเกจ `.app` ของ NexOS (Header 64 ไบต์, Magic Bytes `0x4E455841`, Execution Layout Code/Data/BSS/Stack/Heap) ได้รับแรงบันดาลใจและพัฒนาต่อยอดมาจากหลักการ Flat Binary Format ที่สร้างขึ้นสำหรับระบบสมองกลฝังตัวที่ไม่มีระบบ Virtual Memory Mapping
* **ลิงก์:**
  * 📰 **บทความต้นฉบับ Linux Journal:** [https://www.linuxjournal.com/article/7221](https://www.linuxjournal.com/article/7221)
  * 💻 **ซอร์สโค้ดเคอร์เนล Linux (`fs/binfmt_flat.c`):** [https://github.com/torvalds/linux/blob/master/fs/binfmt_flat.c](https://github.com/torvalds/linux/blob/master/fs/binfmt_flat.c)

---

## 3. งานวิจัยด้าน Capability-based Security & สถาปัตยกรรม RISC-V

### 📌 3.1 seL4 Microkernel on RISC-V & Capability-based Access Control
* **ผู้แต่ง:** Gernot Heiser et al. (Trustworthy Systems)
* **ความเกี่ยวข้องกับ NexOS:** ต้นแบบการออกแบบความปลอดภัยของระบบปฏิบัติการแบบ Capability-Based ซึ่ง NexOS นำมาปรับใช้ในการตรวจสอบสิทธิ์ของแอปพลิเคชัน (`nex_device_has` และการตรวจสอบ Capability Flags ใน `.app` Header) ก่อนอนุญาตให้เรียกใช้ System Call สู่ฮาร์ดแวร์จริง
* **ลิงก์:**
  * 📄 **seL4 Whitepaper (PDF):** [https://sel4.systems/About/seL4-whitepaper.pdf](https://sel4.systems/About/seL4-whitepaper.pdf)
  * 🌐 **เอกสารทางการ seL4 on RISC-V:** [https://docs.sel4.systems/Hardware/riscv.html](https://docs.sel4.systems/Hardware/riscv.html)
  * 💻 **seL4 GitHub Repository:** [https://github.com/seL4/seL4](https://github.com/seL4/seL4)

### 📌 3.2 RISC-V Real-Time & Trap Latency Research
* **สมาคมวิชาการ:** Workshop on Computer Architecture Research with RISC-V (CARRV) / IEEE Real-Time Systems Symposium (RTSS)
* **ความเกี่ยวข้องกับ NexOS:** ศึกษาประสิทธิภาพความเร็วและ Overhead ของการเรียกคำสั่งระบบ (`ecall` trap vs Direct Trampoline Vector) บนไมโครคอนโทรลเลอร์ RISC-V 32-bit (เช่น RV32IMAC บน ESP32-C6)
* **ลิงก์:**
  * 🌐 **CARRV Workshop:** [https://carrv.github.io/](https://carrv.github.io/)
  * 🌐 **RISC-V International Architecture Specifications:** [https://riscv.org/technical/specifications/](https://riscv.org/technical/specifications/)

---

## 4. งานวิจัยสำรวจระบบปฏิบัติการสมองกลฝังตัว (Surveys on Embedded / IoT OS)

### 📌 4.1 Operating Systems for Low-End Devices in the Internet of Things: A Survey
* **ผู้แต่ง:** Oliver Hahm, Emmanuel Baccelli, Hauke Petersen, Nicolas Tsiftes
* **ตีพิมพ์ใน:** IEEE Internet of Things Journal (Volume 3, Issue 5, 2016)
* **ความเกี่ยวข้องกับ NexOS:** เปรียบเทียบสถาปัตยกรรมของ OS ฝังตัวอย่างละเอียด ทั้งแบบ Monolithic (FreeRTOS, TinyOS) และแบบ Modular/Microkernel (RIOT, Contiki) แสดงให้เห็นข้อดี-ข้อจำกัดของหน่วยความจำและการจัดการ Task
* **ลิงก์:**
  * 📄 **Open Access Preprint (arXiv PDF):** [https://arxiv.org/pdf/1510.03577.pdf](https://arxiv.org/pdf/1510.03577.pdf)
  * 🔗 **IEEE Xplore:** [https://ieeexplore.ieee.org/document/7364234](https://ieeexplore.ieee.org/document/7364234)
  * 🔗 **arXiv Abstract:** [https://arxiv.org/abs/1510.03577](https://arxiv.org/abs/1510.03577)

### 📌 4.2 RIOT: An Open Source Operating System for Low-End Embedded Devices in the IoT
* **ผู้แต่ง:** Emmanuel Baccelli et al.
* **ตีพิมพ์ใน:** IEEE Internet of Things Journal (2018)
* **ความเกี่ยวข้องกับ NexOS:** นำเสนอการทำ Multi-threading และ Hardware Abstraction Layer (HAL) ที่เป็นอิสระจากฮาร์ดแวร์เพื่อรองรับไมโครคอนโทรลเลอร์ต่างค่าย (เช่นเดียวกับที่ NexOS รองรับ 9 Targets)
* **ลิงก์:**
  * 🔗 **IEEE Xplore:** [https://ieeexplore.ieee.org/document/8315122](https://ieeexplore.ieee.org/document/8315122)
  * 🌐 **เว็บไซต์ทางการ RIOT OS:** [https://riot-os.org/](https://riot-os.org/)

---

## 5. บทความและสถาปัตยกรรมอ้างอิงระดับอุตสาหกรรม (Industry Reference Architectures)

### 📌 5.1 Hubris & Humility: Microkernel for Deeply Embedded Systems
* **ผู้พัฒนา:** Oxide Computer Company (นำทีมโดย Cliff L. Biffle)
* **ความเกี่ยวข้องกับ NexOS:** เป็นระบบปฏิบัติการแบบ Microkernel สมัยใหม่สำหรับไมโครคอนโทรลเลอร์ที่แยก Driver ออกจาก Kernel เพื่อความปลอดภัย พร้อมทั้งมีชุดเครื่องมือ Developer Console (Humility) สำหรับติดตามการทำงาน เช่นเดียวกับ **NexOS Developer Studio**
* **ลิงก์:**
  * 📰 **บทความสถาปัตยกรรม (Oxide Blog):** [https://oxide.computer/blog/hubris-and-humility](https://oxide.computer/blog/hubris-and-humility)
  * 🌐 **เว็บไซต์และคู่มือทางการ:** [https://hubris.oxide.computer/](https://hubris.oxide.computer/)
  * 💻 **GitHub Repository:** [https://github.com/oxidecomputer/hubris](https://github.com/oxidecomputer/hubris)

### 📌 5.2 Zephyr Project: Userspace, Memory Domains & Syscalls
* **ผู้พัฒนา:** Linux Foundation
* **ความเกี่ยวข้องกับ NexOS:** เอกสารสถาปัตยกรรมอธิบายหลักการทำ System Call และการแบ่งโหมด Privilege / Unprivileged Mode บนไมโครคอนโทรลเลอร์
* **ลิงก์:**
  * 📖 **คู่มือสถาปัตยกรรม Userspace:** [https://docs.zephyrproject.org/latest/kernel/usermode/index.html](https://docs.zephyrproject.org/latest/kernel/usermode/index.html)
  * 📖 **คู่มือกลไก System Calls:** [https://docs.zephyrproject.org/latest/kernel/usermode/syscalls.html](https://docs.zephyrproject.org/latest/kernel/usermode/syscalls.html)
  * 🌐 **เว็บไซต์ทางการ Zephyr Project:** [https://www.zephyrproject.org/](https://www.zephyrproject.org/)
