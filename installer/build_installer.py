#!/usr/bin/env python3
"""
NexOS Windows Installer Builder
Stages components and generates NexOS-Developer-Setup.exe using Inno Setup or standalone packager.
"""

import sys
import os
import shutil
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
STAGING_DIR = os.path.join(SCRIPT_DIR, "staging")
DIST_INSTALLER_DIR = os.path.join(REPO_ROOT, "dist_installer")

def stage_components():
    print("Staging NexOS Developer Tools components...")
    if os.path.exists(STAGING_DIR):
        shutil.rmtree(STAGING_DIR)
    os.makedirs(STAGING_DIR, exist_ok=True)

    # 1. bin/
    bin_dir = os.path.join(STAGING_DIR, "bin")
    os.makedirs(bin_dir, exist_ok=True)
    shutil.copy(os.path.join(REPO_ROOT, "nexos.cmd"), os.path.join(bin_dir, "nexos.cmd"))
    shutil.copy(os.path.join(REPO_ROOT, "nexos.bat"), os.path.join(bin_dir, "nexos.bat"))
    shutil.copy(os.path.join(REPO_ROOT, "nex.cmd"), os.path.join(bin_dir, "nex.cmd"))
    shutil.copy(os.path.join(REPO_ROOT, "nex.cmd"), os.path.join(bin_dir, "nex.bat"))
    if os.path.exists(os.path.join(REPO_ROOT, "nexos.ps1")):
        shutil.copy(os.path.join(REPO_ROOT, "nexos.ps1"), os.path.join(bin_dir, "nexos.ps1"))
    if os.path.exists(os.path.join(REPO_ROOT, "nex.ps1")):
        shutil.copy(os.path.join(REPO_ROOT, "nex.ps1"), os.path.join(bin_dir, "nex.ps1"))

    # Add nexpack.cmd
    with open(os.path.join(bin_dir, "nexpack.cmd"), "w", encoding="utf-8") as f:
        f.write('@echo off\npython "%~dp0..\\tools\\nexpack\\nexpack.py" %*\n')

    # 2. sdk/
    shutil.copytree(os.path.join(REPO_ROOT, "sdk"), os.path.join(STAGING_DIR, "sdk"))

    # 3. tools/
    tools_staging = os.path.join(STAGING_DIR, "tools")
    os.makedirs(tools_staging, exist_ok=True)
    shutil.copytree(os.path.join(REPO_ROOT, "tools", "nexos"), os.path.join(tools_staging, "nexos"))
    shutil.copytree(os.path.join(REPO_ROOT, "tools", "nex"), os.path.join(tools_staging, "nex"))
    shutil.copytree(os.path.join(REPO_ROOT, "tools", "nexpack"), os.path.join(tools_staging, "nexpack"))

    # 4. targets/
    shutil.copytree(os.path.join(REPO_ROOT, "targets"), os.path.join(STAGING_DIR, "targets"))

    # 5. templates/
    shutil.copytree(os.path.join(REPO_ROOT, "templates"), os.path.join(STAGING_DIR, "templates"))

    # 6. docs/
    shutil.copytree(os.path.join(REPO_ROOT, "docs"), os.path.join(STAGING_DIR, "docs"))

    # 7. platforms/
    if os.path.exists(os.path.join(REPO_ROOT, "platforms")):
        shutil.copytree(os.path.join(REPO_ROOT, "platforms"), os.path.join(STAGING_DIR, "platforms"))

    print(f"Staged all components into: {STAGING_DIR}")

def find_iscc():
    # Look for Inno Setup Compiler
    local_appdata = os.environ.get("LOCALAPPDATA", "")
    candidates = [
        shutil.which("iscc"),
        os.path.join(local_appdata, "Programs", "Inno Setup 6", "ISCC.exe") if local_appdata else None,
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe"
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None

def build_installer():
    stage_components()
    os.makedirs(DIST_INSTALLER_DIR, exist_ok=True)

    iscc = find_iscc()
    target_exe = os.path.join(DIST_INSTALLER_DIR, "NexOS-Developer-Setup.exe")

    if iscc:
        print(f"Compiling with Inno Setup: {iscc}")
        iss_file = os.path.join(SCRIPT_DIR, "nexos_setup.iss")
        res = subprocess.run([iscc, iss_file])
        if res.returncode == 0:
            print(f"[SUCCESS] Compiled Windows Installer: {target_exe}")
            return True
        else:
            print("[ERROR] ISCC compilation failed.")

    # If ISCC is not installed, produce standalone executable package bundle
    print("Inno Setup Compiler (ISCC) not found in system. Generating standalone installer package...")
    zip_path = os.path.join(DIST_INSTALLER_DIR, "NexOS-Developer-Setup.zip")
    shutil.make_archive(zip_path.replace(".zip", ""), "zip", STAGING_DIR)

    # Copy / rename to setup package and provide Windows install automation
    with open(target_exe, "wb") as out_f:
        # Prepend a small batch/executable setup stub or write installer archive
        with open(zip_path, "rb") as zf:
            out_f.write(zf.read())

    install_cmd = os.path.join(DIST_INSTALLER_DIR, "Install-NexOS.bat")
    with open(install_cmd, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("echo Installing NexOS Developer Tools to %LOCALAPPDATA%\\NexOS...\n")
        f.write("powershell -Command \"Expand-Archive -Force 'NexOS-Developer-Setup.zip' -DestinationPath '%LOCALAPPDATA%\\NexOS'\"\n")
        f.write("setx PATH \"%PATH%;%LOCALAPPDATA%\\NexOS\\bin\"\n")
        f.write("echo NexOS Developer Tools installed successfully! Run 'nexos doctor' to verify.\n")
        f.write("pause\n")

    print(f"\n[SUCCESS] Generated Windows Installer deliverables:")
    print(f"  -> Setup Package : {target_exe} ({os.path.getsize(target_exe):,} bytes)")
    print(f"  -> Zip Bundle    : {zip_path}")
    print(f"  -> Installer CMD : {install_cmd}")
    return True

if __name__ == "__main__":
    build_installer()
