#!/usr/bin/env python3
"""
NexPack — NexOS Application Packaging, Inspection & Validation Utility
Builds, validates, and inspects standardized NexOS .app binary packages.
"""

import sys
import os
import struct
import hashlib
import argparse
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

# Constants matching tools/nexpack/app_format.h
NEX_APP_MAGIC = b"\x7FNEXAPP\x01"
NEX_APP_FORMAT_VERSION = 1
NEX_APP_HEADER_SIZE = 128
HEADER_STRUCT_FORMAT = "<8sHHHH4s32s16sIIIIIII32s"

ARCH_MAP = {
    "riscv32": 1, "riscv": 1,
    "xtensa": 2,
    "arm_m0": 3, "cortex-m0plus": 3, "rp2040": 3,
    "arm_m4": 4, "cortex-m4": 4, "stm32": 4,
    "avr": 5, "atmega328p": 5,
    "host": 6, "x86_64": 6
}

CHIP_MAP = {
    "esp32c6": 1, "esp32-c6": 1,
    "rp2040": 2, "pico": 2, "pico-w": 2,
    "esp8266": 3,
    "esp32": 4,
    "esp32s3": 5, "esp32-s3": 5,
    "stm32f4": 6, "stm32": 6,
    "atmega328p": 7, "arduino-avr": 7,
    "host": 8, "x86_64": 8
}

REV_ARCH_MAP = {1: "RISC-V 32-bit (rv32imac)", 2: "Xtensa", 3: "ARM Cortex-M0+", 4: "ARM Cortex-M4", 5: "AVR 8-bit", 6: "Host x86_64"}
REV_CHIP_MAP = {1: "ESP32-C6", 2: "RP2040", 3: "ESP8266", 4: "ESP32", 5: "ESP32-S3", 6: "STM32F4", 7: "ATmega328P", 8: "Host PC"}

PERMS_MAP = {
    "gpio": 1 << 0,
    "uart": 1 << 1,
    "i2c": 1 << 2,
    "spi": 1 << 3,
    "storage": 1 << 4,
    "network": 1 << 5,
    "display": 1 << 6,
    "adc": 1 << 7
}

def parse_toml(toml_path):
    with open(toml_path, "rb") as f:
        if hasattr(tomllib, "load"):
            return tomllib.load(f)
        else:
            # Simple fallback parser for key = value
            content = f.read().decode("utf-8")
            data = {}
            current_section = data
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"): continue
                if line.startswith("[") and line.endswith("]"):
                    sec = line[1:-1]
                    data[sec] = {}
                    current_section = data[sec]
                elif "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if v.lower() == "true": v = True
                    elif v.lower() == "false": v = False
                    elif v.isdigit(): v = int(v)
                    current_section[k] = v
            return data

def build_permissions_bitmask(perms_dict):
    mask = 0
    if not isinstance(perms_dict, dict):
        return mask
    for k, v in perms_dict.items():
        if v and k.lower() in PERMS_MAP:
            mask |= PERMS_MAP[k.lower()]
    return mask

def create_app_package(app_dir, binary_path, output_path):
    toml_path = os.path.join(app_dir, "nexos.toml")
    if not os.path.exists(toml_path):
        raise FileNotFoundError(f"Missing configuration file: {toml_path}")

    cfg = parse_toml(toml_path)
    app_sec = cfg.get("app", {})
    target_sec = cfg.get("target", {})
    nex_sec = cfg.get("nexos", {})
    mem_sec = cfg.get("memory", {})
    perm_sec = cfg.get("permissions", {})

    app_name = app_sec.get("name", "app")[:31].encode("utf-8")
    app_name = app_name.ljust(32, b"\x00")

    app_version = app_sec.get("version", "1.0.0")[:15].encode("utf-8")
    app_version = app_version.ljust(16, b"\x00")

    arch_id = ARCH_MAP.get(target_sec.get("architecture", "riscv32").lower(), 1)
    chip_id = CHIP_MAP.get(target_sec.get("chip", "esp32c6").lower(), 1)
    abi_version = int(nex_sec.get("abi_version", 1))

    # Min version (e.g. 0.1.0)
    min_ver_str = str(nex_sec.get("minimum_version", "0.1.0"))
    parts = [int(p) if p.isdigit() else 0 for p in min_ver_str.split(".")]
    while len(parts) < 3: parts.append(0)
    min_nexos_ver = bytes([parts[0], parts[1], parts[2], 0])

    stack_size = int(mem_sec.get("stack", 4096))
    heap_size = int(mem_sec.get("heap", 8192))
    perms_mask = build_permissions_bitmask(perm_sec)

    # Read application executable payload
    if not os.path.exists(binary_path):
        raise FileNotFoundError(f"Compiled binary not found: {binary_path}")

    with open(binary_path, "rb") as f:
        payload = f.read()

    code_size = len(payload)
    data_size = 0
    bss_size = 512
    entry_offset = 0

    # Calculate SHA-256 checksum of payload
    h = hashlib.sha256()
    h.update(payload)
    checksum = h.digest()

    reserved = b"\x00" * 4

    # Pack 128-byte header
    header_bytes = struct.pack(
        HEADER_STRUCT_FORMAT,
        NEX_APP_MAGIC,
        NEX_APP_FORMAT_VERSION,
        abi_version,
        arch_id,
        chip_id,
        min_nexos_ver,
        app_name,
        app_version,
        entry_offset,
        code_size,
        data_size,
        bss_size,
        stack_size,
        heap_size,
        perms_mask,
        checksum
    )

    assert len(header_bytes) == NEX_APP_HEADER_SIZE, f"Header size must be 128 bytes, got {len(header_bytes)}"

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(header_bytes)
        f.write(payload)

    return {
        "app_name": app_sec.get("name", "app"),
        "version": app_sec.get("version", "1.0.0"),
        "target_chip": target_sec.get("chip", "esp32c6"),
        "architecture": target_sec.get("architecture", "riscv32"),
        "code_size": code_size,
        "data_size": data_size,
        "stack_size": stack_size,
        "heap_size": heap_size,
        "output_path": output_path,
        "checksum": h.hexdigest()
    }

def unpack_app_header(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    size = os.path.getsize(file_path)
    if size < NEX_APP_HEADER_SIZE:
        raise ValueError("File is smaller than minimum NexOS 128-byte header")

    with open(file_path, "rb") as f:
        header_data = f.read(NEX_APP_HEADER_SIZE)
        payload = f.read()

    unpacked = struct.unpack(HEADER_STRUCT_FORMAT, header_data)
    magic = unpacked[0]
    fmt_ver = unpacked[1]
    abi_ver = unpacked[2]
    arch_id = unpacked[3]
    chip_id = unpacked[4]
    min_ver = unpacked[5]
    name = unpacked[6].decode("utf-8", errors="ignore").rstrip("\x00")
    version = unpacked[7].decode("utf-8", errors="ignore").rstrip("\x00")
    entry_offset = unpacked[8]
    code_size = unpacked[9]
    data_size = unpacked[10]
    bss_size = unpacked[11]
    stack_size = unpacked[12]
    heap_size = unpacked[13]
    perms = unpacked[14]
    checksum = unpacked[15]

    return {
        "magic": magic,
        "format_version": fmt_ver,
        "abi_version": abi_ver,
        "arch_id": arch_id,
        "chip_id": chip_id,
        "min_version": f"{min_ver[0]}.{min_ver[1]}.{min_ver[2]}",
        "app_name": name,
        "version": version,
        "entry_offset": entry_offset,
        "code_size": code_size,
        "data_size": data_size,
        "bss_size": bss_size,
        "stack_size": stack_size,
        "heap_size": heap_size,
        "permissions": perms,
        "checksum": checksum.hex(),
        "payload": payload,
        "total_size": size
    }

def validate_app_package(file_path):
    diagnostics = []
    is_valid = True

    try:
        info = unpack_app_header(file_path)
    except Exception as e:
        return False, [f"Header parsing failure: {e}"]

    # 1. Magic check
    if info["magic"] == NEX_APP_MAGIC:
        diagnostics.append(("[OK]", "Package format (NEXAPP magic valid)"))
    else:
        diagnostics.append(("[FAIL]", f"Invalid magic bytes: {info['magic']}"))
        is_valid = False

    # 2. Architecture & Chip
    arch_name = REV_ARCH_MAP.get(info["arch_id"], "Unknown Architecture")
    chip_name = REV_CHIP_MAP.get(info["chip_id"], "Unknown SoC")
    diagnostics.append(("[OK]", f"Architecture: {arch_name}"))
    diagnostics.append(("[OK]", f"Target Chip: {chip_name}"))

    # 3. ABI version
    if info["abi_version"] == 1:
        diagnostics.append(("[OK]", f"ABI version: {info['abi_version']} (Compatible)"))
    else:
        diagnostics.append(("[FAIL]", f"Unsupported ABI version: {info['abi_version']}"))
        is_valid = False

    # 4. Checksum verification
    h = hashlib.sha256()
    h.update(info["payload"])
    actual_chk = h.hexdigest()
    if actual_chk == info["checksum"]:
        diagnostics.append(("[OK]", f"Payload SHA-256 Checksum verified"))
    else:
        diagnostics.append(("[FAIL]", f"Checksum mismatch! Expected: {info['checksum'][:16]}..., Computed: {actual_chk[:16]}..."))
        is_valid = False

    # 5. Memory bounds
    if info["stack_size"] >= 1024 and info["heap_size"] >= 1024:
        diagnostics.append(("[OK]", f"Memory requirements (Stack: {info['stack_size']//1024} KB, Heap: {info['heap_size']//1024} KB)"))
    else:
        diagnostics.append(("[WARN]", "Memory requirements below minimum recommendations (<1KB)"))

    # 6. Permissions summary
    active_perms = [k for k, v in PERMS_MAP.items() if (info["permissions"] & v)]
    diagnostics.append(("[OK]", f"Permissions: {', '.join(active_perms) if active_perms else 'None'}"))

    return is_valid, diagnostics

def main():
    parser = argparse.ArgumentParser(prog="nexpack", description="NexOS Application Packaging & Validation Tool")
    sub = parser.add_subparsers(dest="cmd")

    pack_cmd = sub.add_parser("create", help="Create a .app package")
    pack_cmd.add_argument("app_dir", help="Application project root containing nexos.toml")
    pack_cmd.add_argument("-b", "--binary", required=True, help="Compiled binary payload")
    pack_cmd.add_argument("-o", "--output", required=True, help="Output .app destination")

    val_cmd = sub.add_parser("validate", help="Validate a .app package")
    val_cmd.add_argument("app_file", help="Path to .app file")

    info_cmd = sub.add_parser("info", help="Display metadata of a .app package")
    info_cmd.add_argument("app_file", help="Path to .app file")

    args = parser.parse_args()

    if args.cmd == "create":
        res = create_app_package(args.app_dir, args.binary, args.output)
        print(f"Successfully packaged: {res['output_path']} ({res['code_size']} bytes code)")
    elif args.cmd == "validate":
        valid, diags = validate_app_package(args.app_file)
        print("NexOS Application Validator")
        print("===========================")
        for status, msg in diags:
            print(f"{status:<7} {msg}")
        print("-" * 27)
        if valid:
            print("Application is valid.")
            sys.exit(0)
        else:
            print("Application validation failed.")
            sys.exit(1)
    elif args.cmd == "info":
        info = unpack_app_header(args.app_file)
        print("NexOS Application Info")
        print("======================")
        print(f"Name         : {info['app_name']}")
        print(f"Version      : {info['version']}")
        print(f"Architecture : {REV_ARCH_MAP.get(info['arch_id'])}")
        print(f"Target Chip  : {REV_CHIP_MAP.get(info['chip_id'])}")
        print(f"ABI Version  : {info['abi_version']}")
        print(f"Min NexOS    : {info['min_version']}")
        print(f"Code Size    : {info['code_size']:,} bytes")
        print(f"Data Size    : {info['data_size']:,} bytes")
        print(f"BSS Size     : {info['bss_size']:,} bytes")
        print(f"Stack Req    : {info['stack_size']:,} bytes ({info['stack_size']//1024} KB)")
        print(f"Heap Req     : {info['heap_size']:,} bytes ({info['heap_size']//1024} KB)")
        print(f"Checksum     : {info['checksum']}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
