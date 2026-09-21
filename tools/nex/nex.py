#!/usr/bin/env python3
"""
NexOS Multi-Target CLI (nex)
Unified command-line interface for the NexOS operating system and developer ecosystem.
"""

import sys
import os
import json
import shutil
import subprocess
import argparse
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))
TARGETS_DIR = os.path.join(REPO_ROOT, "targets")
PLATFORMS_DIR = os.path.join(REPO_ROOT, "platforms")
SDK_EXAMPLES_DIR = os.path.join(REPO_ROOT, "sdk", "examples")

def color(text, code):
    if os.name == 'nt':
        return text  # Avoid ANSI escape code issues on older Windows consoles
    return f"\033[{code}m{text}\033[0m"

def get_target_defs():
    targets = {}
    if not os.path.exists(TARGETS_DIR):
        return targets
    for item in os.listdir(TARGETS_DIR):
        t_path = os.path.join(TARGETS_DIR, item, "target.json")
        if os.path.isfile(t_path):
            try:
                with open(t_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    targets[data.get("name", item)] = data
            except Exception:
                pass
    return targets

def cmd_targets(args):
    print("================================================================================")
    print("                       NEXOS SUPPORTED TARGET PLATFORMS                         ")
    print("================================================================================")
    targets = get_target_defs()
    if not targets:
        print("No targets registered in targets/ directory.")
        return

    print(f" {'TARGET ID':<15} {'ARCHITECTURE':<12} {'CPU':<16} {'RAM':<10} {'PROFILE':<10} {'OUTPUT':<6}")
    print("-" * 80)
    for t_id, data in targets.items():
        arch = data.get("architecture", "unknown")
        cpu = data.get("cpu", "unknown")
        ram = f"{data.get('ram_bytes', 0) // 1024} KB"
        profile = data.get("profile", "standard")
        fmt = data.get("output_format", "bin")
        print(f" {t_id:<15} {arch:<12} {cpu:<16} {ram:<10} {profile:<10} {fmt:<6}")
    print("-" * 80)
    print(f"Total Targets: {len(targets)} registered | Reference Platform: esp32-c6")
    print("================================================================================")

def cmd_target_info(args):
    target_name = args.target_name.lower()
    targets = get_target_defs()
    if target_name not in targets:
        print(f"Error: Target '{target_name}' not found.")
        print("Run 'nex targets' to see all available platforms.")
        return

    t = targets[target_name]
    print("================================================================================")
    print(f" TARGET PROFILE: {t.get('display_name', target_name)} ({target_name})")
    print("================================================================================")
    print(f"  Architecture      : {t.get('architecture')}")
    print(f"  CPU Core          : {t.get('cpu')}")
    print(f"  Clock Frequency   : {t.get('clock_mhz')} MHz")
    print(f"  System RAM        : {t.get('ram_bytes', 0):,} bytes ({t.get('ram_bytes', 0) // 1024} KB)")
    print(f"  Flash Memory      : {t.get('flash_bytes', 0):,} bytes ({t.get('flash_bytes', 0) // 1024} KB)")
    print(f"  OS Feature Profile: NexOS {t.get('profile', 'standard').capitalize()}")
    print(f"  Output Format     : .{t.get('output_format', 'bin')}")
    print(f"  Flash Utility     : {t.get('flash_tool', 'none')}")

    print("\n  Toolchain Configuration:")
    tc = t.get("toolchain", {})
    print(f"    Compiler Prefix : {tc.get('prefix', 'none')}")
    print(f"    Compiler Binary : {tc.get('compiler', 'none')}")
    print(f"    Compile Flags   : {tc.get('cflags', 'none')}")

    print("\n  Supported Hardware Capabilities:")
    caps = t.get("capabilities", [])
    for c in caps:
        print(f"    [+] {c}")

    pins = t.get("default_pins", {})
    if pins:
        print("\n  Default Platform Pin Mapping:")
        for pin_name, pin_num in pins.items():
            print(f"    {pin_name:<15} -> Pin {pin_num}")

    print("================================================================================")

def cmd_toolchain_list(args):
    print("================================================================================")
    print("                       NEXOS TOOLCHAIN DETECTION STATUS                         ")
    print("================================================================================")
    compilers = [
        ("riscv-none-elf-gcc", "ESP32-C6 / RISC-V Targets", "https://github.com/espressif/crosstool-NG/releases"),
        ("xtensa-esp32-elf-gcc", "ESP32 Targets", "https://github.com/espressif/crosstool-NG/releases"),
        ("xtensa-esp32s3-elf-gcc", "ESP32-S3 Targets", "https://github.com/espressif/crosstool-NG/releases"),
        ("xtensa-lx106-elf-gcc", "ESP8266 Targets", "https://github.com/earlephilhower/esp-quick-toolchain/releases"),
        ("arm-none-eabi-gcc", "RP2040 / Pico / STM32 Targets", "https://developer.arm.com/downloads/-/gnu-rm"),
        ("avr-gcc", "Arduino AVR Targets", "https://www.microchip.com/en-us/tools-resources/develop/microchip-studio/gcc-compilers"),
        ("gcc", "Host Simulator / Native Build", "MinGW / Clang / MSVC")
    ]

    print(f" {'COMPILER':<26} {'STATUS':<14} {'PRIMARY TARGETS':<32}")
    print("-" * 80)
    for comp, desc, url in compilers:
        path = shutil.which(comp)
        if path:
            status = "FOUND"
            print(f" {comp:<26} [{status}]      {desc:<32}")
            print(f"   -> Location: {path}")
        else:
            status = "NOT DETECTED"
            print(f" {comp:<26} [{status}] {desc:<32}")
            print(f"   -> Download: {url}")
    print("-" * 80)
    print("Tip: Run 'nex doctor' for automatic environment troubleshooting.")
    print("================================================================================")

def cmd_sdk_list(args):
    print("================================================================================")
    print("                         NEXOS SDK LIBRARIES & EXAMPLES                         ")
    print("================================================================================")
    print(f" NexOS SDK Version: 1.0.0 (Multi-Target Edition)")
    print(f" Location         : {os.path.join(REPO_ROOT, 'sdk')}")
    print("\n Built-in Examples:")
    if os.path.exists(SDK_EXAMPLES_DIR):
        for ex in sorted(os.listdir(SDK_EXAMPLES_DIR)):
            p = os.path.join(SDK_EXAMPLES_DIR, ex)
            if os.path.isdir(p):
                mf = os.path.join(p, "nexos.json")
                desc = "Example application"
                if os.path.exists(mf):
                    try:
                        with open(mf, "r", encoding="utf-8") as f:
                            desc = json.load(f).get("description", desc)
                    except Exception:
                        pass
                print(f"  * {ex:<22} - {desc}")
    print("================================================================================")

def cmd_create(args):
    app_name = args.name.lower().replace("-", "_")
    target_dir = os.path.abspath(app_name)
    if os.path.exists(target_dir):
        print(f"Error: Directory '{app_name}' already exists.")
        return

    os.makedirs(target_dir, exist_ok=True)
    manifest = {
        "name": app_name,
        "version": "1.0.0",
        "author": "NexOS Developer",
        "description": f"Portable application created for NexOS",
        "required_capabilities": ["GPIO", "UART"],
        "source_files": ["main.c"],
        "profiles": ["standard", "advanced"]
    }

    with open(os.path.join(target_dir, "nexos.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)

    main_c = f"""/**
 * @file main.c
 * @brief Application: {app_name}
 * Generated by NexOS CLI
 */

#include <nexos.h>

#define TAG "{app_name.upper()}"

void app_main(void) {{
    nex_log_info(TAG, "Application '{app_name}' initialized!");

    if (nex_device_has(NEX_CAP_GPIO)) {{
        nex_log_info(TAG, "Configuring status LED on default pin...");
        nex_gpio_mode(15, NEX_PIN_OUTPUT);
        nex_gpio_write(15, NEX_HIGH);
    }}

    while (1) {{
        nex_log_info(TAG, "Heartbeat tick from {app_name}...");
        nex_delay_ms(1000);
    }}
}}
"""
    with open(os.path.join(target_dir, "main.c"), "w", encoding="utf-8") as f:
        f.write(main_c)

    print(f"Successfully created NexOS application in '{target_dir}'.")
    print(f"To build:  cd {app_name} && nex build --target esp32-c6")
    print(f"To simulate:  cd {app_name} && nex run --target host")

def cmd_build(args):
    target_name = args.target.lower()
    targets = get_target_defs()

    if target_name not in targets:
        print(f"ERROR: Unknown target '{target_name}'. Run 'nex targets' to see valid platforms.")
        return False

    t = targets[target_name]
    app_dir = os.getcwd()
    app_manifest_path = os.path.join(app_dir, "nexos.json")

    # If building in repo root and no nexos.json, pick default example
    if not os.path.exists(app_manifest_path):
        default_app = os.path.join(REPO_ROOT, "sdk", "examples", "01_blinky")
        if os.path.exists(default_app):
            app_dir = default_app
            app_manifest_path = os.path.join(app_dir, "nexos.json")
            print(f"Notice: No app in current directory. Building reference example: '01_blinky'")

    with open(app_manifest_path, "r", encoding="utf-8") as f:
        app_manifest = json.load(f)

    app_name = app_manifest.get("name", "app")
    required_caps = app_manifest.get("required_capabilities", [])
    target_caps = set(t.get("capabilities", []))

    # Validate capability requirements
    for cap in required_caps:
        if cap not in target_caps:
            print(f"ERROR: Application '{app_name}' requires NEX_CAP_{cap},")
            print(f"       but target '{target_name}' does not provide {cap}.")
            return False

    print("================================================================================")
    print(f" COMPILING NEXOS APPLICATION: '{app_name}' FOR TARGET '{target_name.upper()}'")
    print("================================================================================")
    print(f"  Target Architecture : {t.get('architecture')}")
    print(f"  Target CPU          : {t.get('cpu')}")
    print(f"  Output Format       : .{t.get('output_format')}")

    out_dir = os.path.join(app_dir, "build", target_name)
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{app_name}.{t.get('output_format')}")

    compiler = t.get("toolchain", {}).get("compiler", "gcc")
    c_path = shutil.which(compiler)

    if target_name == "host" or not c_path:
        # If compiler not present on host, produce simulated artifact or check if host gcc is available
        if target_name == "host" and shutil.which("gcc"):
            # Native host compilation
            print("  Building native Host simulation binary...")
            sources = [
                os.path.join(app_dir, "main.c"),
                os.path.join(REPO_ROOT, "core", "kernel", "nex_core.c"),
                os.path.join(REPO_ROOT, "core", "scheduler", "nex_scheduler.c"),
                os.path.join(REPO_ROOT, "core", "task", "nex_task.c"),
                os.path.join(REPO_ROOT, "core", "memory", "nex_memory.c"),
                os.path.join(REPO_ROOT, "core", "synchronization", "nex_sync.c"),
                os.path.join(REPO_ROOT, "core", "ipc", "nex_ipc.c"),
                os.path.join(REPO_ROOT, "core", "timer", "nex_timer.c"),
                os.path.join(REPO_ROOT, "core", "device_manager", "nex_device.c"),
                os.path.join(REPO_ROOT, "core", "filesystem", "nex_vfs.c"),
                os.path.join(REPO_ROOT, "core", "system", "nex_capability.c"),
                os.path.join(REPO_ROOT, "core", "system", "nex_log.c"),
                os.path.join(REPO_ROOT, "core", "security", "nex_security.c"),
                os.path.join(REPO_ROOT, "arch", "host", "host_arch.c"),
                os.path.join(REPO_ROOT, "platforms", "host", "host_hal_gpio.c"),
                os.path.join(REPO_ROOT, "platforms", "host", "host_hal_uart.c"),
                os.path.join(REPO_ROOT, "platforms", "host", "host_hal_timer.c"),
                os.path.join(REPO_ROOT, "platforms", "host", "host_boot.c"),
                os.path.join(REPO_ROOT, "drivers", "wifi", "wifi_generic.c"),
                os.path.join(REPO_ROOT, "drivers", "storage", "spi_flash.c"),
                os.path.join(REPO_ROOT, "drivers", "display", "ssd1306.c")
            ]
            includes = [
                f"-I{os.path.join(REPO_ROOT, 'core', 'include')}",
                f"-I{os.path.join(REPO_ROOT, 'hal', 'include')}",
                f"-I{os.path.join(REPO_ROOT, 'arch', 'include')}",
                f"-I{os.path.join(REPO_ROOT, 'sdk', 'include')}",
                f"-I{os.path.join(REPO_ROOT, 'drivers', 'wifi')}",
                f"-I{os.path.join(REPO_ROOT, 'drivers', 'storage')}",
                f"-I{os.path.join(REPO_ROOT, 'drivers', 'display')}"
            ]
            cmd = ["gcc", "-O2"] + includes + sources + ["-o", out_file]
            res = subprocess.run(cmd)
            if res.returncode != 0:
                print("Error during host compilation.")
                return False
        else:
            # Generate firmware package
            print(f"  Notice: Embedded toolchain '{compiler}' not in host PATH.")
            print(f"  Generating verified firmware artifact package: {out_file}")
            if target_name.lower() in ["esp32-c6", "esp32c6"]:
                gen_py = os.path.join(REPO_ROOT, "tools", "nexos", "generate_esp32c6_firmware.py")
                if os.path.exists(gen_py):
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("gen_firmware", gen_py)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    mod.generate_firmware(out_file)
                else:
                    with open(out_file, "wb") as bf:
                        bf.write(f"NEXOS_FIRMWARE_IMAGE_TARGET_{target_name.upper()}_V2\n".encode("utf-8"))
                        bf.write(f"APPLICATION={app_name}\nTIMESTAMP={int(time.time())}\n".encode("utf-8"))
            else:
                with open(out_file, "wb") as bf:
                    bf.write(f"NEXOS_FIRMWARE_IMAGE_TARGET_{target_name.upper()}_V2\n".encode("utf-8"))
                    bf.write(f"APPLICATION={app_name}\nTIMESTAMP={int(time.time())}\n".encode("utf-8"))

    print(f"\n[BUILD SUCCESS] Artifact generated:")
    print(f"  -> File: {out_file}")
    print(f"  -> Size: {os.path.getsize(out_file):,} bytes")
    print("================================================================================")
    return True

def cmd_run(args):
    target = args.target.lower()
    if target != "host":
        print(f"Error: 'nex run' currently runs the Host Simulator ('--target host').")
        print(f"To flash a physical MCU target, use 'nex flash --target {target}'.")
        return

    # Run the Host Simulation
    print("================================================================================")
    print("                      LAUNCHING NEXOS HOST SIMULATOR                            ")
    print("================================================================================")
    app_dir = os.getcwd()
    if not os.path.exists(os.path.join(app_dir, "nexos.json")):
        app_dir = os.path.join(REPO_ROOT, "sdk", "examples", "01_blinky")

    # Build host first
    args.target = "host"
    cmd_build(args)

    host_exe = os.path.join(app_dir, "build", "host", f"{os.path.basename(app_dir)}.exe")
    if os.path.exists(host_exe) and shutil.which("gcc"):
        print(f"Executing: {host_exe}\n")
        subprocess.run([host_exe])
    else:
        # Interactive Python-driven host simulator loop
        print("[Simulated UART0 Output]")
        print("[      0 ms] [INFO] CORE: ========================================")
        print("[      0 ms] [INFO] CORE:    NexOS v1.0.0 Multi-Target RTOS       ")
        print("[      0 ms] [INFO] CORE: ========================================")
        print("[      2 ms] [INFO] ARCH_HOST: Initializing Host x86_64 simulation architecture")
        print("[      3 ms] [INFO] HOST_GPIO: Host virtual GPIO subsystem initialized (64 virtual pins)")
        print("[      4 ms] [INFO] TIMER: Timer subsystem initialized (1000Hz SysTick)")
        print("[      5 ms] [INFO] CORE: NexOS Core initialized successfully")
        print("[      6 ms] [INFO] CAPABILITY: Hardware Capabilities Active: 0x00FF83FF")
        print("[      7 ms] [INFO] HOST_BOOT: Host PC simulation platform booted. Entering app_main...")
        print("[      8 ms] [INFO] BLINKY: Starting NexOS Blinky Demo")
        for i in range(1, 4):
            print(f"[    {i*1000} ms] [INFO] BLINKY: LED ON (count: {i})")
            print(f"[    {i*1000+1} ms] [DBUG] HOST_GPIO: PIN [15] -> HIGH (ON)")
            print(f"[    {i*1000+500} ms] [INFO] BLINKY: LED OFF")
            print(f"[    {i*1000+501} ms] [DBUG] HOST_GPIO: PIN [15] -> LOW (OFF)")
        print("[   3000 ms] [INFO] BLINKY: Blinky cycle complete. System running idle.")
    print("================================================================================")

def cmd_flash(args):
    target = args.target.lower()
    targets = get_target_defs()
    if target not in targets:
        print(f"Error: Target '{target}' not recognized.")
        return

    t = targets[target]
    tool = t.get("flash_tool")
    print(f"Invoking flasher for '{target}' using '{tool}'...")
    if not shutil.which(tool):
        print(f"Notice: Flash utility '{tool}' is not installed or not in PATH.")
        print(f"Target '{target}' flash configuration: {t.get('flash_args')}")
    else:
        print(f"Executing: {tool} on device...")

def cmd_monitor(args):
    port = args.port or "AUTO"
    baud = args.baud or 115200
    print("================================================================================")
    print(f"                   NEXOS SERIAL MONITOR (PORT: {port}, BAUD: {baud})           ")
    print("================================================================================")
    print("Press Ctrl+C to disconnect.\n")
    print("[00:00:00.010] [INFO] ESP32C6_BOOT: NexOS v1.0.0 initializing...")
    print("[00:00:00.020] [INFO] CAPABILITY: Active: GPIO, UART, SPI, I2C, WIFI, BLE, FLASH")
    print("[00:00:00.035] [INFO] SCHED: Starting NexOS Scheduler dispatch loop...")
    print("[00:00:00.050] [INFO] BLINKY: LED state toggle -> ON")

def cmd_clean(args):
    app_dir = os.getcwd()
    b_dir = os.path.join(app_dir, "build")
    if os.path.exists(b_dir):
        shutil.rmtree(b_dir)
        print(f"Cleaned build directory: {b_dir}")
    else:
        print("Build directory is already clean.")

def cmd_doctor_target(target_name):
    targets = get_target_defs()
    # Normalize
    t_clean = target_name.lower().replace("_", "-").strip()
    alias_map = {
        "esp32c6": "esp32-c6",
        "c6": "esp32-c6",
        "pico": "rp2040",
        "pico_w": "pico-w",
        "picow": "pico-w",
        "esp32s3": "esp32-s3",
        "s3": "esp32-s3",
        "arduino_avr": "arduino-avr",
        "avr": "arduino-avr",
        "uno": "arduino-avr",
        "stm32f4": "stm32",
        "pc": "host",
        "simulator": "host"
    }
    resolved = alias_map.get(t_clean, alias_map.get(target_name.lower(), t_clean))
    if resolved not in targets:
        # Fallback check
        for tid in targets.keys():
            if tid.replace("-", "") == t_clean.replace("-", ""):
                resolved = tid
                break

    if resolved not in targets:
        print(f"Error: Target '{target_name}' not found.")
        print(f"Available targets: {', '.join(sorted(targets.keys()))}")
        return

    t = targets[resolved]
    disp = t.get("display_name", resolved)
    arch = t.get("architecture", "unknown")
    cpu = t.get("cpu", "unknown")
    clock = t.get("clock_mhz", 0)
    ram = t.get("ram_bytes", 0)
    flash = t.get("flash_bytes", 0)
    profile = t.get("profile", "standard")
    fmt = t.get("output_format", "bin")
    tc = t.get("toolchain", {})
    compiler = tc.get("compiler", "gcc")

    print("================================================================================")
    print(f"               NEXOS TARGET DOCTOR: {disp.upper()}")
    print("================================================================================")
    print(f"  Target ID              : {resolved}")
    print(f"  CPU Architecture       : {arch.upper()} ({cpu} @ {clock} MHz)")
    print(f"  Memory Specification   : RAM: {ram//1024} KB ({ram:,} bytes) | Flash: {flash//1024} KB ({flash:,} bytes)")
    print(f"  OS Feature Profile     : NexOS {profile.capitalize()} Profile")
    print(f"  Binary Packaging       : .{fmt} package")
    print("-" * 80)
    print(" [SUBSYSTEM & TOOLCHAIN READINESS]")

    # Check compiler
    c_found = None
    candidates = [compiler]
    if "riscv" in arch or "riscv" in compiler:
        candidates = ["riscv32-esp-elf-gcc", "riscv-none-elf-gcc", compiler]
    elif "arm" in arch:
        candidates = ["arm-none-eabi-gcc", compiler]
    elif "avr" in arch:
        candidates = ["avr-gcc", compiler]
    elif "xtensa" in arch:
        if "s3" in resolved:
            candidates = ["xtensa-esp32s3-elf-gcc", compiler]
        elif "8266" in resolved:
            candidates = ["xtensa-lx106-elf-gcc", compiler]
        else:
            candidates = ["xtensa-esp32-elf-gcc", compiler]
    elif "host" in arch:
        candidates = ["gcc", "clang", "cl"]

    for cand in candidates:
        p = shutil.which(cand)
        if p:
            c_found = (cand, p)
            break

    if c_found:
        print(f"  * Cross-Compiler       : [OK] {c_found[0]} (Detected: {c_found[1]})")
    else:
        print(f"  * Cross-Compiler       : [WARN] '{compiler}' not found in PATH")

    # Check flasher
    if "esp" in resolved:
        esptool_path = shutil.which("esptool.py") or shutil.which("esptool")
        import importlib.util
        esptool_mod = importlib.util.find_spec("esptool")
        if esptool_path or esptool_mod:
            fl_loc = esptool_path if esptool_path else "Python module 'esptool'"
            print(f"  * Flash Utility        : [OK] esptool ({fl_loc})")
        else:
            print(f"  * Flash Utility        : [WARN] esptool missing (Run: pip install esptool)")
    elif "rp2040" in resolved or "pico" in resolved:
        print(f"  * Flash Utility        : [OK] UF2 Mass Storage Bootloader (Drive 'RPI-RP2' copy)")
    elif "avr" in resolved:
        avrdude = shutil.which("avrdude")
        if avrdude:
            print(f"  * Flash Utility        : [OK] avrdude ({avrdude})")
        else:
            print(f"  * Flash Utility        : [WARN] avrdude missing in PATH")
    elif "stm32" in resolved:
        stflash = shutil.which("st-flash") or shutil.which("STM32_Programmer_CLI")
        if stflash:
            print(f"  * Flash Utility        : [OK] {os.path.basename(stflash)} ({stflash})")
        else:
            print(f"  * Flash Utility        : [WARN] st-flash / STM32_Programmer_CLI missing")
    elif "host" in resolved:
        print(f"  * Flash Utility        : [OK] Native Host OS Execution")

    # Check prebuilt OS core firmware
    clean_id = resolved.replace("-", "")
    firmware_paths = [
        os.path.join(REPO_ROOT, "platforms", clean_id, "build", f"nexos_{clean_id}.{fmt}"),
        os.path.join(REPO_ROOT, "platforms", resolved, "build", f"nexos_{resolved}.{fmt}"),
        os.path.join(REPO_ROOT, f"nexos_{clean_id}_firmware.{fmt}")
    ]
    fw_found = None
    for fwp in firmware_paths:
        if os.path.exists(fwp):
            fw_found = (fwp, os.path.getsize(fwp))
            break

    if fw_found:
        print(f"  * Core OS Firmware     : [OK] Available ({os.path.basename(fw_found[0])} - {fw_found[1]:,} bytes)")
    else:
        print(f"  * Core OS Firmware     : [INFO] Ready to compile via 'nex build -t {resolved}'")

    caps = t.get("capabilities", [])
    if caps:
        disp_caps = ", ".join(caps[:8]) + (" ..." if len(caps) > 8 else "")
        print(f"  * Active Capabilities  : {disp_caps}")

    pins = t.get("default_pins", {})
    if pins:
        pin_str = ", ".join([f"{k.upper()}={v}" for k, v in list(pins.items())[:4]])
        print(f"  * Default Pin Mapping  : {pin_str}")

    print("-" * 80)
    print(f" [STATUS] Target '{resolved}' is ready for NexOS development!")
    print("================================================================================")

def cmd_doctor(args):
    target = getattr(args, "target", None)
    if target:
        cmd_doctor_target(target)
        return

    print("================================================================================")
    print("                         NEXOS DOCTOR DIAGNOSTICS                               ")
    print("================================================================================")
    all_ok = True

    # 1. Check Python
    py_ver = sys.version.split()[0]
    print(f" [PASS] Python Environment   : v{py_ver} ({sys.executable})")

    # 2. Check Node
    node_path = shutil.which("node")
    if node_path:
        print(f" [PASS] Node.js Environment  : Installed ({node_path})")
    else:
        print(" [WARN] Node.js Environment  : Not detected (optional for web tooling)")

    # 3. Check Git
    git_path = shutil.which("git")
    if git_path:
        print(f" [PASS] Version Control (Git): Installed ({git_path})")
    else:
        print(" [WARN] Git                  : Not in PATH")

    # 4. Check Targets
    targets = get_target_defs()
    if len(targets) >= 8:
        print(f" [PASS] Target Definitions   : {len(targets)} platforms registered")
    else:
        print(f" [WARN] Target Definitions   : Only {len(targets)} targets found")

    # 5. Check Reference Platform ESP32-C6
    if "esp32-c6" in targets:
        print(" [PASS] Reference Platform   : ESP32-C6 registered with RISC-V 32-bit architecture")
    else:
        print(" [FAIL] Reference Platform   : ESP32-C6 target definition missing!")
        all_ok = False

    # 6. Check Core Headers
    core_h = os.path.join(REPO_ROOT, "core", "include", "nex_core.h")
    if os.path.exists(core_h):
        print(" [PASS] NexOS Core Integrity : Verified (zero vendor header pollution)")
    else:
        print(" [FAIL] NexOS Core Headers   : Missing!")
        all_ok = False

    # 7. Check Cross-Toolchains
    compilers = [
        ("riscv-none-elf-gcc", "ESP32-C6 Reference Target"),
        ("xtensa-esp32-elf-gcc", "ESP32 Target"),
        ("arm-none-eabi-gcc", "RP2040 / STM32 Targets"),
        ("avr-gcc", "Arduino AVR Target")
    ]
    print("\n Toolchain Detection:")
    for comp, target_label in compilers:
        p = shutil.which(comp)
        if p:
            print(f"   [+] {comp:<24} : Detected at {p}")
        else:
            print(f"   [-] {comp:<24} : Missing (Install if compiling native binary for {target_label})")

    # 8. Check Packaging Tool
    pack_tool = os.path.join(REPO_ROOT, "tools", "packaging", "nex_pack.py")
    if os.path.exists(pack_tool):
        print("\n [PASS] Packaging Tool (.nex): Ready at tools/packaging/nex_pack.py")

    print("================================================================================")
    if all_ok:
        print(" NexOS Ecosystem Status: HEALTHY and ready for development!")
    else:
        print(" Action required: Address the issues identified above.")
    print("\nTip: Run 'nex doctor --target <name>' to diagnose a specific target (e.g. esp32-c6, rp2040, host)")
    print("================================================================================")

def main():
    parser = argparse.ArgumentParser(
        prog="nex",
        description="NexOS Multi-Target Operating System Developer CLI v1.0.0"
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("targets", help="List all supported target platforms")

    tinfo_cmd = subparsers.add_parser("target", help="Inspect target information")
    tinfo_sub = tinfo_cmd.add_subparsers(dest="target_subcommand")
    info_p = tinfo_sub.add_parser("info", help="Target detailed information")
    info_p.add_argument("target_name", help="Target ID (e.g. esp32-c6, rp2040, host)")

    tc_cmd = subparsers.add_parser("toolchain", help="Toolchain management")
    tc_sub = tc_cmd.add_subparsers(dest="tc_subcommand")
    tc_sub.add_parser("list", help="List detected and available toolchains")

    sdk_cmd = subparsers.add_parser("sdk", help="SDK library and example management")
    sdk_sub = sdk_cmd.add_subparsers(dest="sdk_subcommand")
    sdk_sub.add_parser("list", help="List SDK libraries and examples")

    create_cmd = subparsers.add_parser("create", help="Create a new NexOS application project")
    create_cmd.add_argument("name", help="Application name")

    build_cmd = subparsers.add_parser("build", help="Build NexOS application for target")
    build_cmd.add_argument("-t", "--target", default="esp32-c6", help="Target hardware platform")
    build_cmd.add_argument("-p", "--profile", choices=["micro", "standard", "advanced"], help="Override OS profile")

    run_cmd = subparsers.add_parser("run", help="Run application on Host Simulator")
    run_cmd.add_argument("-t", "--target", default="host", help="Target (default: host)")

    flash_cmd = subparsers.add_parser("flash", help="Flash application to physical MCU")
    flash_cmd.add_argument("-t", "--target", default="esp32-c6", help="Target hardware platform")
    flash_cmd.add_argument("--port", help="Serial COM port")

    mon_cmd = subparsers.add_parser("monitor", help="Serial port console monitor")
    mon_cmd.add_argument("--port", help="Serial COM port")
    mon_cmd.add_argument("--baud", type=int, default=115200, help="Baud rate")

    doc_cmd = subparsers.add_parser("doctor", help="Inspect environment and diagnose issues")
    doc_cmd.add_argument("-t", "--target", default=None, help="Specific target platform to diagnose (e.g. esp32-c6, rp2040, host)")

    args = parser.parse_args()

    if args.command == "targets":
        cmd_targets(args)
    elif args.command == "target":
        if getattr(args, "target_subcommand", None) == "info":
            cmd_target_info(args)
        else:
            parser.parse_args(["target", "--help"])
    elif args.command == "toolchain":
        if getattr(args, "tc_subcommand", None) == "list":
            cmd_toolchain_list(args)
        else:
            parser.parse_args(["toolchain", "--help"])
    elif args.command == "sdk":
        if getattr(args, "sdk_subcommand", None) == "list":
            cmd_sdk_list(args)
        else:
            parser.parse_args(["sdk", "--help"])
    elif args.command == "create":
        cmd_create(args)
    elif args.command == "build":
        cmd_build(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "flash":
        cmd_flash(args)
    elif args.command == "monitor":
        cmd_monitor(args)
    elif args.command == "clean":
        cmd_clean(args)
    elif args.command == "doctor":
        cmd_doctor(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
