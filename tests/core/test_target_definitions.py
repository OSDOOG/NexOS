#!/usr/bin/env python3
"""
NexOS Target Definition Test
Validates machine-readable target.json files across all architectures.
"""

import os
import json
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
TARGETS_DIR = os.path.join(REPO_ROOT, "targets")

REQUIRED_TARGET_FIELDS = [
    "name", "display_name", "architecture", "cpu", "clock_mhz",
    "ram_bytes", "flash_bytes", "profile", "toolchain", "output_format", "capabilities"
]

EXPECTED_TARGETS = [
    "esp32-c6", "esp8266", "rp2040", "pico-w", "arduino-avr", "stm32", "esp32", "esp32-s3", "host"
]

class TestTargetDefinitions(unittest.TestCase):
    def test_all_expected_targets_exist(self):
        found = []
        for folder in os.listdir(TARGETS_DIR):
            tp = os.path.join(TARGETS_DIR, folder, "target.json")
            if os.path.exists(tp):
                with open(tp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    found.append(data.get("name"))

        for exp in EXPECTED_TARGETS:
            self.assertIn(exp, found, f"Target '{exp}' must be defined in targets/")

    def test_target_schema_validity(self):
        for folder in os.listdir(TARGETS_DIR):
            tp = os.path.join(TARGETS_DIR, folder, "target.json")
            if os.path.exists(tp):
                with open(tp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for field in REQUIRED_TARGET_FIELDS:
                    self.assertIn(field, data, f"Target {folder} missing required field '{field}'")
                self.assertGreater(data["ram_bytes"], 0)
                self.assertGreater(data["flash_bytes"], 0)
                self.assertIsInstance(data["capabilities"], list)
                self.assertIn(data["profile"], ["micro", "standard", "advanced"])

    def test_esp32c6_reference_target(self):
        tp = os.path.join(TARGETS_DIR, "esp32c6", "target.json")
        with open(tp, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["architecture"], "riscv")
        self.assertIn("WIFI", data["capabilities"])
        self.assertIn("BLE", data["capabilities"])
        self.assertEqual(data["output_format"], "bin")

if __name__ == "__main__":
    unittest.main()
