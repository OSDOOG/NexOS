#!/usr/bin/env python3
"""
NexOS CLI Integration Tests
Tests execution of 'nex targets', 'nex target info', 'nex doctor', 'nex build'.
"""

import os
import sys
import subprocess
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
NEX_CLI = os.path.join(REPO_ROOT, "tools", "nex", "nex.py")

class TestNexCLI(unittest.TestCase):
    def test_cli_targets(self):
        res = subprocess.run([sys.executable, NEX_CLI, "targets"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("esp32-c6", res.stdout)
        self.assertIn("rp2040", res.stdout)
        self.assertIn("Total Targets: 9 registered", res.stdout)

    def test_cli_target_info(self):
        res = subprocess.run([sys.executable, NEX_CLI, "target", "info", "esp32-c6"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("TARGET PROFILE: Espressif ESP32-C6", res.stdout)
        self.assertIn("riscv32-imac", res.stdout)

    def test_cli_doctor(self):
        res = subprocess.run([sys.executable, NEX_CLI, "doctor"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("NexOS Core Integrity : Verified", res.stdout)
        self.assertIn("Reference Platform   : ESP32-C6", res.stdout)

    def test_cli_build_reference(self):
        res = subprocess.run([sys.executable, NEX_CLI, "build", "--target", "esp32-c6"],
                             cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("BUILD SUCCESS", res.stdout)

if __name__ == "__main__":
    unittest.main()
