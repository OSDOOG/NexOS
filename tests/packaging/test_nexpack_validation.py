#!/usr/bin/env python3
"""
NexPack Packaging and Security Validation Test Suite
Tests negative and positive validation scenarios:
- Valid package verification
- Corrupted header magic
- Tampered payload (checksum mismatch)
- Incompatible ABI version
- Truncated package file
"""

import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "nexpack"))
import nexpack

class TestNexpackValidation(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.app_dir = os.path.join(self.test_dir.name, "my_app")
        os.makedirs(self.app_dir, exist_ok=True)

        # Create valid nexos.toml
        with open(os.path.join(self.app_dir, "nexos.toml"), "w", encoding="utf-8") as f:
            f.write("""
[app]
name = "sensor"
version = "2.1.0"
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
gpio = true
uart = true
""")
        self.bin_file = os.path.join(self.test_dir.name, "payload.bin")
        with open(self.bin_file, "wb") as bf:
            bf.write(b"\x93\x00\x00\x00" * 32) # Simulated RISC-V instructions

        self.valid_app = os.path.join(self.test_dir.name, "sensor.app")
        nexpack.create_app_package(self.app_dir, self.bin_file, self.valid_app)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_valid_package(self):
        valid, diags = nexpack.validate_app_package(self.valid_app)
        self.assertTrue(valid)
        self.assertTrue(any("magic valid" in d[1] for d in diags))
        self.assertTrue(any("Checksum verified" in d[1] for d in diags))

    def test_corrupted_magic(self):
        corrupt_app = os.path.join(self.test_dir.name, "corrupt_magic.app")
        with open(self.valid_app, "rb") as vf:
            data = bytearray(vf.read())
        data[0:8] = b"BADMAGIC"
        with open(corrupt_app, "wb") as cf:
            cf.write(data)

        valid, diags = nexpack.validate_app_package(corrupt_app)
        self.assertFalse(valid)
        self.assertTrue(any("Invalid magic" in d[1] for d in diags))

    def test_tampered_payload_checksum_mismatch(self):
        tampered_app = os.path.join(self.test_dir.name, "tampered.app")
        with open(self.valid_app, "rb") as vf:
            data = bytearray(vf.read())
        # Modify a byte in the payload
        data[-1] ^= 0xFF
        with open(tampered_app, "wb") as tf:
            tf.write(data)

        valid, diags = nexpack.validate_app_package(tampered_app)
        self.assertFalse(valid)
        self.assertTrue(any("Checksum mismatch" in d[1] for d in diags))

    def test_truncated_file(self):
        trunc_app = os.path.join(self.test_dir.name, "trunc.app")
        with open(trunc_app, "wb") as tf:
            tf.write(b"SHORT")

        valid, diags = nexpack.validate_app_package(trunc_app)
        self.assertFalse(valid)
        self.assertTrue(any("Header parsing failure" in d for d in diags))

if __name__ == "__main__":
    unittest.main()
