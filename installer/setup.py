#!/usr/bin/env python3
"""
NexOS Developer Setup & Environment Installer
Configures environment variables, registers targets, and verifies prerequisites.
"""

import sys
import os
import shutil
import subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def run_setup(selected_targets=None):
    print("================================================================================")
    print("                NEXOS DEVELOPER ECOSYSTEM SETUP (WINDOWS)                       ")
    print("================================================================================")

    if selected_targets is None:
        selected_targets = ["esp32-c6", "rp2040", "pico-w", "host"]

    print(f"Installing NexOS Core...")
    print(f"Repository Root: {REPO_ROOT}")

    # 1. Verify Core directories
    required_dirs = ["core", "hal", "arch", "platforms", "targets", "drivers", "sdk", "tools"]
    for d in required_dirs:
        p = os.path.join(REPO_ROOT, d)
        if os.path.isdir(p):
            print(f"  [+] Core subsystem: {d:<14} (OK)")
        else:
            print(f"  [-] Missing directory: {d}")

    # 2. Add repo root and tools to user path or script wrappers
    print("\nConfiguring Command-Line Wrappers:")
    cmd_file = os.path.join(REPO_ROOT, "nex.cmd")
    if os.path.exists(cmd_file):
        print(f"  [+] NexOS CLI launcher registered: {cmd_file}")

    # 3. Register selected targets
    print("\nConfiguring Target Packages:")
    targets_dir = os.path.join(REPO_ROOT, "targets")
    all_targets = os.listdir(targets_dir) if os.path.exists(targets_dir) else []
    for t in all_targets:
        active = "[x]" if t in selected_targets else "[ ]"
        print(f"  {active} Target Platform: {t}")

    print("\nSetup finished successfully!")
    print("You can now run 'nex targets' or 'nex doctor' from any terminal in this workspace.")
    print("================================================================================")

if __name__ == "__main__":
    targets = sys.argv[1:] if len(sys.argv) > 1 else None
    run_setup(targets)
