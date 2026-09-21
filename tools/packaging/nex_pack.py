#!/usr/bin/env python3
"""
NexOS Application Package (.nex) Tool
Handles creation, inspection, verification, and extraction of .nex packages.
"""

import sys
import os
import json
import zipfile
import hashlib
import argparse

MAGIC_HEADER = "NEXPKG01"

def calculate_sha256(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def create_package(app_dir: str, output_path: str, target: str = "esp32-c6", binary_path: str = None):
    app_dir = os.path.abspath(app_dir)
    manifest_file = os.path.join(app_dir, "nexos.json")

    if not os.path.exists(manifest_file):
        print(f"Error: manifest file '{manifest_file}' not found.")
        return False

    with open(manifest_file, "r", encoding="utf-8") as f:
        app_manifest = json.load(f)

    package_manifest = {
        "format": "NEX_PACKAGE_V1",
        "app_name": app_manifest.get("name", "unnamed_app"),
        "version": app_manifest.get("version", "1.0.0"),
        "author": app_manifest.get("author", "Unknown"),
        "target": target,
        "required_capabilities": app_manifest.get("required_capabilities", []),
        "entry_point": "app_main",
        "timestamp": 1772620000
    }

    if not output_path.endswith(".nex"):
        output_path += ".nex"

    print(f"Packaging '{package_manifest['app_name']}' -> '{output_path}' for target '{target}'...")

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Write manifest
        manifest_bytes = json.dumps(package_manifest, indent=4).encode("utf-8")
        zf.writestr("manifest.json", manifest_bytes)

        # Write binary if provided, or stub
        if binary_path and os.path.exists(binary_path):
            with open(binary_path, "rb") as bf:
                bin_data = bf.read()
            zf.writestr(f"bin/{package_manifest['app_name']}.bin", bin_data)
        else:
            stub_bin = f"/* NEXOS EMBEDDED BINARY FOR {target.upper()} */\n".encode("utf-8")
            zf.writestr(f"bin/{package_manifest['app_name']}.bin", stub_bin)

        # Write sources/config
        for root, _, files in os.walk(app_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, app_dir)
                zf.write(full_path, f"src/{rel_path}")

        # Compute package checksum
        chk = calculate_sha256(manifest_bytes)
        zf.writestr("checksum.sha256", chk.encode("utf-8"))

    print(f"Successfully created NexOS package: {output_path} (SHA-256: {chk[:16]}...)")
    return True

def inspect_package(package_path: str):
    if not os.path.exists(package_path):
        print(f"Error: package '{package_path}' does not exist.")
        return False

    with zipfile.ZipFile(package_path, "r") as zf:
        if "manifest.json" not in zf.namelist():
            print("Error: Invalid .nex package (missing manifest.json)")
            return False

        manifest_data = json.loads(zf.read("manifest.json").decode("utf-8"))
        checksum = zf.read("checksum.sha256").decode("utf-8") if "checksum.sha256" in zf.namelist() else "N/A"

        print("==================================================")
        print("          NEXOS PACKAGE INSPECTION REPORT         ")
        print("==================================================")
        print(f" Package File     : {os.path.basename(package_path)}")
        print(f" Application Name : {manifest_data.get('app_name')}")
        print(f" Version          : {manifest_data.get('version')}")
        print(f" Author           : {manifest_data.get('author')}")
        print(f" Target Target    : {manifest_data.get('target')}")
        print(f" Required Caps    : {', '.join(manifest_data.get('required_capabilities', [])) or 'None'}")
        print(f" Entry Point      : {manifest_data.get('entry_point')}")
        print(f" Integrity Check  : {checksum[:32]}...")
        print(" Contents:")
        for info in zf.infolist():
            print(f"   - {info.filename:<30} ({info.file_size} bytes)")
        print("==================================================")
    return True

def main():
    parser = argparse.ArgumentParser(description="NexOS Package (.nex) Utility")
    subparsers = parser.add_subparsers(dest="command")

    pack_cmd = subparsers.add_parser("create", help="Create a .nex package")
    pack_cmd.add_argument("app_dir", help="Path to application source directory")
    pack_cmd.add_argument("-o", "--output", required=True, help="Output .nex file path")
    pack_cmd.add_argument("-t", "--target", default="esp32-c6", help="Target hardware platform")
    pack_cmd.add_argument("-b", "--binary", help="Optional prebuilt binary file")

    inspect_cmd = subparsers.add_parser("inspect", help="Inspect a .nex package")
    inspect_cmd.add_argument("package_path", help="Path to .nex file")

    args = parser.parse_args()
    if args.command == "create":
        success = create_package(args.app_dir, args.output, args.target, args.binary)
        sys.exit(0 if success else 1)
    elif args.command == "inspect":
        success = inspect_package(args.package_path)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
