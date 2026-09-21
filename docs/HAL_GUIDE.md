# คู่มือชั้นนามธรรมของฮาร์ดแวร์ NexOS (HAL Guide)

ชั้น Hardware Abstraction Layer (HAL) ทำหน้าที่กำหนดสัญญาและฟังก์ชันมาตรฐานที่เป็นอิสระจากฮาร์ดแวร์ สำหรับติดต่อกับอุปกรณ์รอบข้าง (Peripherals) ทั้งหมดของไมโครคอนโทรลเลอร์

---

## 1. GPIO พินดิจิทัล (`nex_hal_gpio.h`)
- `nex_gpio_init()`: เริ่มต้นระบบควบคุมพิน
- `nex_gpio_mode(pin, mode)`: กำหนดทิศทางและโหมดของพิน (`NEX_PIN_INPUT`, `NEX_PIN_OUTPUT`, `NEX_PIN_INPUT_PULLUP`, `NEX_PIN_INPUT_PULLDOWN`, `NEX_PIN_OUTPUT_OPENDRAIN`)
- `nex_gpio_write(pin, level)`: ส่งสัญญาณลอจิกสูง (`NEX_HIGH`) หรือต่ำ (`NEX_LOW`)
- `nex_gpio_read(pin)`: อ่านค่าสถานะลอจิกปัจจุบันของพิน
- `nex_gpio_toggle(pin)`: สลับสถานะลอจิกของพินเอาต์พุต
- `nex_gpio_attach_interrupt(pin, type, isr, arg)`: ผูกฟังก์ชันบริการอินเทอร์รัปต์ (ISR) เมื่อเกิดสัญญาณขอบขาขึ้น/ลง

---

## 2. พอร์ตสื่อสารซีเรียล UART (`nex_hal_uart.h`)
- `nex_uart_init(port, config)`: กำหนด Baud rate, พาริตี, Stop bits และการแมปพิน
- `nex_uart_write(port, data, len)`: ส่งชุดข้อมูลไบต์ออกทางพอร์ตซีเรียล
- `nex_uart_read(port, buf, len, received, timeout_ms)`: อ่านข้อมูลไบต์เข้ามาพร้อมการกำหนด Timeout
- `nex_uart_putc(port, c)`: ส่งตัวอักษรเดี่ยวออกไป
- `nex_uart_getc(port)`: อ่านตัวอักษรเดี่ยวแบบไม่บล็อกการทำงาน (Non-blocking)

---

## 3. บัสสื่อสารความเร็วสูง SPI (`nex_hal_spi.h`)
- `nex_spi_init(bus, config)`: กำหนดความถี่สัญญาณนาฬิกา, โหมด SPI (0-3), ลำดับบิต และพิน
- `nex_spi_transfer(bus, tx, rx, len)`: รับ-ส่งข้อมูลแบบ Full-duplex แบบซิงโครนัส
- `nex_spi_write(bus, tx, len)`: ส่งข้อมูลแบบ Half-duplex
- `nex_spi_read(bus, rx, len)`: รับข้อมูลแบบ Half-duplex

---

## 4. บัสสื่อสาร I2C (`nex_hal_i2c.h`)
- `nex_i2c_init(port, config)`: กำหนดความเร็วบัส (100 kHz มาตรฐาน, 400 kHz ความเร็วสูง) และพิน
- `nex_i2c_write(port, addr, data, len)`: ส่งข้อมูลในฐานะ Master ไปยัง Slave แอดเดรส 7 บิต
- `nex_i2c_read(port, addr, data, len)`: อ่านข้อมูลในฐานะ Master จาก Slave แอดเดรส 7 บิต
- `nex_i2c_write_reg(port, addr, reg, data, len)`: เขียนข้อมูลลงในรีจิสเตอร์ของอุปกรณ์ปลายทาง
- `nex_i2c_read_reg(port, addr, reg, data, len)`: อ่านข้อมูลจากรีจิสเตอร์ของอุปกรณ์ปลายทาง

---

## 5. สัญญาณความกว้างพัลส์ PWM (`nex_hal_pwm.h`)
- `nex_pwm_init(channel, pin, freq_hz)`: ผูกชาแนล PWM เข้ากับพินพร้อมกำหนดความถี่ (Hz)
- `nex_pwm_set_duty(channel, duty_percent)`: กำหนดค่า Duty Cycle 0-100%
- `nex_pwm_start(channel)`: เริ่มต้นสร้างสัญญาณ PWM
- `nex_pwm_stop(channel)`: หยุดการสร้างสัญญาณ PWM

---

## 6. วงจรแปลงสัญญาณแอนะล็อกเป็นดิจิทัล ADC (`nex_hal_adc.h`)
- `nex_adc_init(channel, resolution)`: กำหนดความละเอียด (8, 10, 12 บิต)
- `nex_adc_read_raw(channel)`: อ่านค่าตัวเลขดิบจากการแปลงสัญญาณ
- `nex_adc_read_voltage_mv(channel)`: อ่านค่าแรงดันไฟฟ้าที่ปรับเทียบแล้วเป็นมิลลิโวลต์ (mV)

---

## 7. ตัวนับเวลาและสัญญาณนาฬิการะบบ SysTick (`nex_hal_timer.h`)
- `nex_hal_systick_init(tick_rate_hz, isr, arg)`: ตั้งค่าตัวนับเวลา 1ms สำหรับจังหวะการทำงานของ OS
- `nex_hal_get_cycles()`: อ่านตัวนับไซเคิลสัญญาณนาฬิกาความแม่นยำสูง
- `nex_hal_delay_us(us)`: หน่วงเวลาในระดับไมโครวินาที (Microseconds)

---

## 8. การเชื่อมต่อเครือข่ายไร้สาย WiFi (`nex_hal_network.h`)
- `nex_wifi_init()`: เริ่มต้นการทำงานของวงจร 802.11 MAC/PHY
- `nex_wifi_connect(config)`: เชื่อมต่อ Access Point ด้วยชื่อ SSID และรหัสผ่าน
- `nex_wifi_disconnect()`: ยกเลิกการเชื่อมต่อเครือข่าย
- `nex_wifi_get_status()`: ตรวจสอบสถานะการเชื่อมต่อ (`CONNECTED`, `GOT_IP`, `ERROR`)
- `nex_wifi_get_ip_info(info)`: ดึงข้อมูล IP Address, Subnet Mask, Gateway และ DNS
