#!/usr/bin/env python3
"""
NexOS Kernel Application Loader Test Suite
Tests loading, validation, and execution guards inside the application loader.
"""

import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "nexpack"))
import nexpack

class TestAppLoaderValidation(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.app_dir = os.path.join(self.test_dir.name, "sample_app")
        os.makedirs(self.app_dir, exist_ok=True)

        with open(os.path.join(self.app_dir, "nexos.toml"), "w", encoding="utf-8") as f:
            f.write("""
[app]
name = "loader_test"
version = "1.0.0"
[target]
architecture = "riscv32"
chip = "esp32c6"
[nexos]
minimum_version = "0.1.0"
abi_version = 1
[memory]
stack = 4096
heap = 8192
[permissions]
gpio = false
uart = true
""")
        self.bin_file = os.path.join(self.test_dir.name, "code.bin")
        with open(self.bin_file, "wb") as f:
            f.write(b"\x00" * 64) # 64 bytes payload

        self.app_file = os.path.join(self.test_dir.name, "loader_test.app")
        nexpack.create_app_package(self.app_dir, self.bin_file, self.app_file)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_loader_header_integrity(self):
        with open(self.app_file, "rb") as f:
            data = f.read()

        # Check header fields match specification
        info = nexpack.unpack_app_header(self.app_file)
        self.assertEqual(info["magic"], b"\x7FNEXAPP\x01")
        self.assertEqual(info["app_name"], "loader_test")
        self.assertEqual(info["format_version"], 1)
        self.assertEqual(info["abi_version"], 1)
        self.assertEqual(info["code_size"], 64)
        self.assertEqual(info["stack_size"], 4096)
        self.assertEqual(info["heap_size"], 8192)

    def test_installer_deliverables_exist(self):
        installer_exe = os.path.join(REPO_ROOT, "dist_installer", "NexOS-Developer-Setup.exe")
        self.assertTrue(os.path.exists(installer_exe), f"Setup executable {installer_exe} must be generated")
        self.assertGreater(os.path.getsize(installer_exe), 1000)

if __name__ == "__main__":
    unittest.main()
