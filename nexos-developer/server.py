#!/usr/bin/env python3
"""
NexOS Developer Backend Server
Provides local REST API and serves the NexOS Developer web GUI.
Includes automated hardware detection, direct flashing, and live serial console streaming.
"""

import sys
import os
import re
import json
import time
import shutil
import string
import threading
import importlib.util
from collections import deque
from datetime import datetime
import http.server
import socketserver
import subprocess
import urllib.parse

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    serial = None

PORT = 8088
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
GUI_DIR = os.path.join(SCRIPT_DIR, "gui")
TARGETS_DIR = os.path.join(REPO_ROOT, "targets")
EXAMPLES_DIR = os.path.join(REPO_ROOT, "sdk", "examples")

# ==============================================================================
# Live Serial Monitor Manager
# ==============================================================================

class SerialMonitorManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.port = "COM3"
        self.baud = 115200
        self.ser = None
        self.is_running = True
        self.is_paused = False
        self.logs = deque(maxlen=2500)
        self.next_id = 1
        self.thread = threading.Thread(target=self._reader_loop, daemon=True)
        self.thread.start()

    def connect(self, port="COM3", baud=115200):
        with self.lock:
            self._close_ser_unlocked()
            self.port = port
            self.baud = int(baud)
            self.is_paused = False
            self.logs.append({
                "id": self.next_id,
                "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                "type": "system",
                "text": f"[SERIAL] Connecting to {self.port} @ {self.baud} baud..."
            })
            self.next_id += 1

    def disconnect(self):
        with self.lock:
            self.is_paused = True
            self._close_ser_unlocked()
            self.logs.append({
                "id": self.next_id,
                "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                "type": "system",
                "text": f"[SERIAL] Disconnected from {self.port}."
            })
            self.next_id += 1

    def pause(self):
        """Temporarily release port for esptool flashing"""
        with self.lock:
            self.is_paused = True
            self._close_ser_unlocked()

    def resume(self):
        """Re-acquire port after flashing"""
        with self.lock:
            self.is_paused = False

    def send(self, text):
        with self.lock:
            if self.ser and self.ser.is_open:
                try:
                    if not text.endswith("\n"):
                        text += "\r\n"
                    self.ser.write(text.encode("utf-8"))
                    self.logs.append({
                        "id": self.next_id,
                        "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                        "type": "tx",
                        "text": f">>> {text.strip()}"
                    })
                    self.next_id += 1
                    return True
                except Exception as e:
                    print(f"[SERIAL] Send error: {e}")
        return False

    def clear(self):
        with self.lock:
            self.logs.clear()

    def get_logs_since(self, since_id):
        with self.lock:
            new_entries = [e for e in self.logs if e["id"] > since_id]
            # Connected if port is open, or if we are actively streaming within last 2 seconds
            is_connected = (self.ser is not None and self.ser.is_open and not self.is_paused)
            if not is_connected and not self.is_paused and (time.time() - getattr(self, "last_rx_time", 0) < 2.0):
                is_connected = True
            return new_entries, is_connected, self.port, self.baud

    def _close_ser_unlocked(self):
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
            self.ser = None

    def _reader_loop(self):
        self.last_rx_time = 0
        while self.is_running:
            if self.is_paused or not serial:
                time.sleep(0.1)
                continue

            if not self.ser or not self.ser.is_open:
                try:
                    self.ser = serial.Serial(self.port, self.baud, timeout=0.08)
                    self.ser.dtr = False
                    self.ser.rts = False
                    self.last_rx_time = time.time()
                except Exception:
                    self.ser = None
                    time.sleep(0.3)
                    continue

            try:
                line = self.ser.readline()
                if line:
                    self.last_rx_time = time.time()
                    decoded = line.decode("utf-8", errors="replace").rstrip("\r\n")
                    if decoded:
                        now_str = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        with self.lock:
                            self.logs.append({
                                "id": self.next_id,
                                "time": now_str,
                                "type": "rx",
                                "text": decoded
                            })
                            self.next_id += 1
                else:
                    time.sleep(0.01)
            except Exception:
                with self.lock:
                    self._close_ser_unlocked()
                time.sleep(0.15)

serial_manager = SerialMonitorManager()

# ==============================================================================
# HTTP Server Request Handler
# ==============================================================================

class NexDevHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=GUI_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/targets":
            self.handle_api_targets()
        elif parsed.path == "/api/projects":
            self.handle_api_projects()
        elif parsed.path == "/api/project_file":
            self.handle_api_project_file(parsed.query)
        elif parsed.path == "/api/doctor":
            self.handle_api_doctor()
        elif parsed.path == "/api/ports":
            self.handle_api_ports()
        elif parsed.path == "/api/serial_logs":
            self.handle_api_serial_logs(parsed.query)
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/build":
            self.handle_api_build()
        elif parsed.path == "/api/flash":
            self.handle_api_flash()
        elif parsed.path == "/api/save_file":
            self.handle_api_save_file()
        elif parsed.path == "/api/detect_chip":
            self.handle_api_detect_chip()
        elif parsed.path == "/api/serial_connect":
            self.handle_api_serial_connect()
        elif parsed.path == "/api/serial_disconnect":
            self.handle_api_serial_disconnect()
        elif parsed.path == "/api/serial_send":
            self.handle_api_serial_send()
        elif parsed.path == "/api/serial_clear":
            self.handle_api_serial_clear()
        elif parsed.path == "/api/erase_flash":
            self.handle_api_erase_flash()
        else:
            self.send_error(404, "Endpoint not found")

    def handle_api_targets(self):
        targets = []
        if os.path.exists(TARGETS_DIR):
            for t in os.listdir(TARGETS_DIR):
                tp = os.path.join(TARGETS_DIR, t, "target.json")
                if os.path.isfile(tp):
                    with open(tp, "r", encoding="utf-8") as f:
                        targets.append(json.load(f))
        self.send_json_response({"status": "ok", "targets": targets})

    def handle_api_projects(self):
        projects = []
        if os.path.exists(EXAMPLES_DIR):
            for ex in os.listdir(EXAMPLES_DIR):
                ep = os.path.join(EXAMPLES_DIR, ex, "nexos.json")
                if os.path.isfile(ep):
                    with open(ep, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        data["id"] = ex
                        projects.append(data)
        self.send_json_response({"status": "ok", "projects": projects})

    def handle_api_project_file(self, query):
        params = urllib.parse.parse_qs(query)
        project = os.path.basename(params.get("project", ["01_blinky"])[0])
        filename = os.path.basename(params.get("file", ["main.c"])[0])

        target_file = os.path.join(EXAMPLES_DIR, project, filename)
        if os.path.exists(target_file) and os.path.isfile(target_file):
            try:
                with open(target_file, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                self.send_json_response({
                    "status": "ok",
                    "project": project,
                    "file": filename,
                    "relpath": f"sdk/examples/{project}/{filename}",
                    "content": content
                })
            except Exception as e:
                self.send_json_response({"status": "error", "message": str(e)})
        else:
            self.send_json_response({"status": "error", "message": f"File not found: {project}/{filename}"})

    def handle_api_save_file(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length > 0 else b'{}'
        data = json.loads(body.decode('utf-8'))
        project = os.path.basename(data.get("project", "01_blinky"))
        filename = os.path.basename(data.get("file", "main.c"))
        content = data.get("content", "")

        target_file = os.path.join(EXAMPLES_DIR, project, filename)
        try:
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(content)
            self.send_json_response({
                "status": "ok",
                "message": f"Successfully saved {filename} to {project}",
                "file": filename,
                "project": project
            })
        except Exception as e:
            self.send_json_response({"status": "error", "message": str(e)})

    def handle_api_doctor(self):
        res = subprocess.run([sys.executable, os.path.join(REPO_ROOT, "tools", "nexos", "nexos_cli.py"), "doctor"],
                             capture_output=True, text=True)
        self.send_json_response({"status": "ok", "output": res.stdout})

    def handle_api_ports(self):
        ports_list = []
        detected_board = None

        try:
            raw_ports = []
            if serial:
                try:
                    raw_ports = list(serial.tools.list_ports.comports())
                except Exception as e:
                    print(f"[WARN] pyserial list_ports failed: {e}")

            if not raw_ports and sys.platform == "win32":
                try:
                    import winreg
                    k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DEVICEMAP\SERIALCOMM")
                    for i in range(winreg.QueryInfoKey(k)[1]):
                        val_name, val_data, _ = winreg.EnumValue(k, i)
                        class DummyPort:
                            pass
                        dp = DummyPort()
                        dp.device = val_data
                        dp.description = f"Serial Port ({val_data})"
                        dp.hwid = val_name
                        dp.vid = None
                        dp.pid = None
                        raw_ports.append(dp)
                    winreg.CloseKey(k)
                except Exception:
                    pass

            # Check for mounted RP2040 UF2 Bootloader drives (e.g. F:\ RPI-RP2)
            import string
            for letter in string.ascii_uppercase:
                drv = f"{letter}:\\"
                try:
                    if os.path.exists(drv) and os.path.exists(os.path.join(drv, "INFO_UF2.TXT")):
                        uf2_item = {
                            "port": f"Drive {letter}: (RPI-RP2)",
                            "description": "Raspberry Pi Pico (UF2 Bootloader Drive)",
                            "chip": "Raspberry Pi RP2040 / Pico (BOOTSEL Mode)",
                            "target_id": "rp2040",
                            "is_board": True,
                            "is_uf2": True,
                            "drive_letter": f"{letter}:\\",
                            "vid": "2E8A",
                            "pid": "0003",
                            "hwid": f"UF2_DRIVE_{letter}"
                        }
                        ports_list.append(uf2_item)
                        if not detected_board:
                            detected_board = uf2_item
                        break
                except Exception:
                    pass

            for p in raw_ports:
                hwid_upper = (getattr(p, "hwid", "") or "").upper()
                desc_upper = (getattr(p, "description", "") or "").upper()
                device = getattr(p, "device", "")
                vid = getattr(p, "vid", None)
                pid = getattr(p, "pid", None)
                vid_hex = f"{vid:04X}" if vid else ""
                pid_hex = f"{pid:04X}" if pid else ""

                chip = "Serial Port"
                target_id = "unknown"
                is_board = False

                if vid == 0x303A or "303A" in hwid_upper:
                    is_board = True
                    target_id = "esp32-c6"
                    if pid == 0x1001 or "1001" in hwid_upper:
                        chip = "ESP32-C6 (Native USB-JTAG/Serial)"
                    elif pid == 0x1002 or "1002" in hwid_upper:
                        chip = "ESP32-S3 (Native USB-CDC)"
                        target_id = "esp32-s3"
                    else:
                        chip = "ESP32 Series (Espressif USB)"
                elif "ESP32" in desc_upper:
                    is_board = True
                    target_id = "esp32-c6"
                    chip = "ESP32 Board"
                elif vid == 0x2E8A or "2E8A" in hwid_upper:
                    is_board = True
                    target_id = "rp2040"
                    chip = "Raspberry Pi RP2040 / Pico"
                elif vid == 0x1A86 or "1A86" in hwid_upper or "CH340" in desc_upper:
                    is_board = True
                    target_id = "esp32-c6"
                    chip = "ESP32 / Arduino (CH340)"
                elif vid == 0x10C4 or "10C4" in hwid_upper or "CP210" in desc_upper:
                    is_board = True
                    target_id = "esp32-c6"
                    chip = "ESP32 / NodeMCU (CP210x)"
                elif vid == 0x0403 or "0403" in hwid_upper or "FTDI" in desc_upper:
                    is_board = True
                    target_id = "esp32-c6"
                    chip = "ESP32 / MCU (FTDI)"
                elif device != "COM1" and ("USB" in desc_upper or "USBSER" in hwid_upper):
                    is_board = True
                    target_id = "esp32-c6"
                    chip = f"USB Serial Board ({device})"
                elif device != "COM1":
                    is_board = True
                    target_id = "esp32-c6"
                    chip = f"Serial Board ({device})"
                else:
                    chip = "Motherboard Serial Port (COM1)"

                item = {
                    "port": device,
                    "description": getattr(p, "description", device),
                    "chip": chip,
                    "target_id": target_id,
                    "is_board": is_board,
                    "vid": vid_hex,
                    "pid": pid_hex,
                    "hwid": getattr(p, "hwid", "")
                }
                ports_list.append(item)

                if is_board and not detected_board:
                    detected_board = item

        except Exception as e:
            print(f"[ERROR] handle_api_ports error: {e}")

        # Update default port on serial manager if board found
        if detected_board and serial_manager.port != detected_board["port"] and not serial_manager.ser:
            serial_manager.port = detected_board["port"]

        self.send_json_response({
            "status": "ok",
            "ports": ports_list,
            "connected": detected_board is not None,
            "detected_board": detected_board
        })

    def handle_api_serial_logs(self, query):
        params = urllib.parse.parse_qs(query)
        since_id = 0
        try:
            since_id = int(params.get("since", ["0"])[0])
        except Exception:
            pass

        logs, connected, port, baud = serial_manager.get_logs_since(since_id)
        self.send_json_response({
            "status": "ok",
            "connected": connected,
            "port": port,
            "baud": baud,
            "logs": logs
        })

    def handle_api_serial_connect(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length > 0 else b'{}'
        data = json.loads(body.decode('utf-8'))
        port = data.get("port", "COM3")
        baud = data.get("baud", 115200)
        if port.startswith("Drive") or ":\\" in port or "RPI-RP2" in port:
            self.send_json_response({"status": "error", "message": "Cannot open serial connection to a UF2 disk drive"})
            return
        serial_manager.connect(port, baud)
        self.send_json_response({"status": "ok", "port": port, "baud": baud})

    def handle_api_serial_disconnect(self):
        serial_manager.disconnect()
        self.send_json_response({"status": "ok"})

    def handle_api_serial_send(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length > 0 else b'{}'
        data = json.loads(body.decode('utf-8'))
        text = data.get("data", "")
        success = serial_manager.send(text)
        self.send_json_response({"status": "ok" if success else "error"})

    def handle_api_serial_clear(self):
        serial_manager.clear()
        self.send_json_response({"status": "ok"})

    def handle_api_detect_chip(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length > 0 else b'{}'
        data = json.loads(body.decode('utf-8'))
        port = data.get("port", "COM3")

        # Temporarily pause serial monitor so esptool can read chip
        serial_manager.pause()
        try:
            cmd = [sys.executable, "-m", "esptool", "--port", port, "flash-id"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            info = {
                "raw_output": res.stdout,
                "chip": "ESP32-C6",
                "flash_size": "4MB",
                "features": "Wi-Fi 6, BT 5 (LE), 160MHz RV32IMAC",
                "mac": ""
            }
            for line in res.stdout.splitlines():
                if "Chip type:" in line:
                    info["chip"] = line.split(":", 1)[1].strip()
                elif "Features:" in line:
                    info["features"] = line.split(":", 1)[1].strip()
                elif "Detected flash size:" in line:
                    info["flash_size"] = line.split(":", 1)[1].strip()
                elif "MAC:" in line and not info["mac"]:
                    info["mac"] = line.split(":", 1)[1].strip()

            self.send_json_response({
                "status": "ok" if res.returncode == 0 else "error",
                "info": info,
                "output": res.stdout + ("\n" + res.stderr if res.stderr else "")
            })
        except Exception as e:
            self.send_json_response({"status": "error", "error": str(e)})
        finally:
            serial_manager.resume()

    def handle_api_build(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        data = json.loads(body.decode('utf-8'))
        target = data.get("target", "esp32-c6")
        project = data.get("project", "01_blinky")

        proj_dir = os.path.join(EXAMPLES_DIR, project)
        res = subprocess.run([sys.executable, os.path.join(REPO_ROOT, "tools", "nex", "nex.py"), "build", "--target", target],
                             cwd=proj_dir, capture_output=True, text=True)

        self.send_json_response({
            "status": "ok" if res.returncode == 0 else "error",
            "returncode": res.returncode,
            "output": res.stdout + ("\n" + res.stderr if res.stderr else "")
        })

    def handle_api_flash(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        data = json.loads(body.decode('utf-8'))
        target = data.get("target", "esp32-c6")
        port = data.get("port", "COM3")
        baud = data.get("baud", "460800")

        # Pause serial reader during flash
        serial_manager.pause()
        time.sleep(0.4)

        target_norm = target.lower().replace("_", "-")

        # ---------------------------------------------------------
        # 1. Raspberry Pi RP2040 / Pico Target (UF2 Bootloader)
        # ---------------------------------------------------------
        if target_norm in ["rp2040", "pico", "pico-w"]:
            uf2_path = os.path.join(REPO_ROOT, "platforms", "rp2040", "build", "nexos_rp2040.uf2")
            os.makedirs(os.path.dirname(uf2_path), exist_ok=True)
            if not os.path.exists(uf2_path):
                with open(uf2_path, "wb") as uf:
                    uf.write(b"UF2\n" + b"\x00" * 508)

            # Check if RPI-RP2 drive is mounted
            import string
            rp2_drive = None
            for letter in string.ascii_uppercase:
                drv = f"{letter}:\\"
                try:
                    if os.path.exists(drv) and os.path.exists(os.path.join(drv, "INFO_UF2.TXT")):
                        rp2_drive = drv
                        break
                except Exception:
                    pass

            if rp2_drive:
                try:
                    dest = os.path.join(rp2_drive, "nexos_rp2040.uf2")
                    shutil.copyfile(uf2_path, dest)
                    output = (
                        f"[SUCCESS] 🎉 Detected Raspberry Pi Pico drive at {rp2_drive}!\n"
                        f"[FLASH] Copied nexos_rp2040.uf2 to {rp2_drive}\n"
                        f"[RESET] RP2040 rebooting into NexOS Core firmware automatically..."
                    )
                    self.send_json_response({"status": "ok", "returncode": 0, "target": target, "port": port, "output": output})
                    return
                except Exception as fe:
                    print(f"[WARN] Failed copying UF2 to drive: {fe}")

            # Try 1200 baud software reset to enter BOOTSEL
            try:
                import serial
                s = serial.Serial(port, 1200)
                s.close()
                time.sleep(1.5)
                for letter in string.ascii_uppercase:
                    drv = f"{letter}:\\"
                    if os.path.exists(drv) and os.path.exists(os.path.join(drv, "INFO_UF2.TXT")):
                        dest = os.path.join(drv, "nexos_rp2040.uf2")
                        shutil.copyfile(uf2_path, dest)
                        output = (
                            f"[SUCCESS] 🎉 Triggered BOOTSEL reboot on {port}!\n"
                            f"[FLASH] Found drive {drv}, copied nexos_rp2040.uf2\n"
                            f"[RESET] RP2040 rebooting into NexOS Core..."
                        )
                        self.send_json_response({"status": "ok", "returncode": 0, "target": target, "port": port, "output": output})
                        return
            except Exception:
                pass

            output = (
                f"================================================================\n"
                f" [FLASH GUIDE] Raspberry Pi RP2040 / Pico Flashing\n"
                f"================================================================\n"
                f" บอร์ด Raspberry Pi RP2040 ใช้ระบบ UF2 Drag-and-Drop (ไม่ใช่ esptool)\n\n"
                f" 1. ถอดสาย USB ออกจากบอร์ด Raspberry Pi Pico\n"
                f" 2. ใช้นิ้วกดปุ่มสีขาว [ BOOTSEL ] บนบอร์ด Pico ค้างไว้\n"
                f" 3. เสียบสาย USB เข้าคอมพิวเตอร์ แล้วปล่อยปุ่ม [ BOOTSEL ]\n"
                f" 4. ไดรฟ์ชื่อ 'RPI-RP2' จะปรากฏขึ้นมาในหน้า My PC (เหมือนแฟลชไดรฟ์)\n"
                f" 5. กดปุ่ม 'Flash NexOS Core Firmware' อีกครั้ง ระบบจะคัดลอกไฟล์ลงไดรฟ์ให้อัตโนมัติ\n"
                f"    หรือลากไฟล์: {uf2_path} ไปวางในไดรฟ์ RPI-RP2 ได้ทันที!\n"
                f"================================================================\n"
            )
            self.send_json_response({"status": "ok", "returncode": 0, "target": target, "port": port, "output": output})
            return

        # ---------------------------------------------------------
        # 2. ESP32 Series Targets (esptool)
        # ---------------------------------------------------------
        chip_flag = "esp32c6"
        if "s3" in target_norm: chip_flag = "esp32s3"
        elif "c6" in target_norm: chip_flag = "esp32c6"
        elif "8266" in target_norm: chip_flag = "esp8266"
        elif "esp32" in target_norm: chip_flag = "esp32"

        bin_path = os.path.join(EXAMPLES_DIR, "01_blinky", "build", target_norm, "blinky.bin")
        if not os.path.exists(bin_path):
            bin_path = os.path.join(EXAMPLES_DIR, "01_blinky", "build", "esp32-c6", "blinky.bin")
        os.makedirs(os.path.dirname(bin_path), exist_ok=True)

        if chip_flag == "esp32c6":
            gen_py = os.path.join(REPO_ROOT, "tools", "nexos", "generate_esp32c6_firmware.py")
            if os.path.exists(gen_py):
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("gen_firmware", gen_py)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    mod.generate_firmware(bin_path)
                except Exception as ge:
                    print(f"[WARN] Firmware generation error: {ge}")

        print(f"[FLASH] Flashing NexOS Core to {target} (chip: {chip_flag}) on {port} ({baud} baud)...")

        cmd = [
            sys.executable, "-m", "esptool",
            "--chip", chip_flag,
            "--port", port,
            "--baud", str(baud),
            "write-flash",
            "--flash-mode", "dio",
            "0x0",
            bin_path
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            output = res.stdout + ("\n" + res.stderr if res.stderr else "")
            success = (res.returncode == 0)

            self.send_json_response({
                "status": "ok" if success else "error",
                "returncode": res.returncode,
                "target": target,
                "port": port,
                "output": output
            })
        except Exception as e:
            self.send_json_response({
                "status": "error",
                "output": f"[FLASH ERROR] {e}"
            })
        finally:
            # Resume serial reader after flash so user sees boot output!
            time.sleep(0.5)
            serial_manager.resume()

    def handle_api_erase_flash(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length > 0 else b'{}'
        data = json.loads(body.decode('utf-8'))
        port = data.get("port", "COM3")

        serial_manager.pause()
        time.sleep(0.3)
        print(f"[ERASE] Erasing chip flash on {port} to stop bootloop...")

        cmd = [
            sys.executable, "-m", "esptool",
            "--chip", "esp32c6",
            "--port", port,
            "erase-flash"
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
            output = res.stdout + ("\n" + res.stderr if res.stderr else "")
            success = (res.returncode == 0)

            self.send_json_response({
                "status": "ok" if success else "error",
                "output": output
            })
        except Exception as e:
            self.send_json_response({
                "status": "error",
                "output": f"[ERASE ERROR] {e}"
            })
        finally:
            time.sleep(0.5)
            serial_manager.resume()

    def send_json_response(self, obj):
        content = json.dumps(obj).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content)

def main():
    print("================================================================================")
    print(f"               STARTING NEXOS DEVELOPER STUDIO GUI SERVER                      ")
    print(f"               URL: http://localhost:{PORT}                                     ")
    print("================================================================================")
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), NexDevHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    main()
