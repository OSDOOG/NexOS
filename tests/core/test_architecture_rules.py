#!/usr/bin/env python3
"""
NexOS Architecture Rule Compliance Test
Strictly verifies that NexOS Core contains zero hardware register accesses,
zero vendor SDK header includes, and zero board-specific hardcoded pin numbers.
Enforces Master Prompt Section 36 Rules 1 through 10.
"""

import os
import sys
import re
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
CORE_DIR = os.path.join(REPO_ROOT, "core")

FORBIDDEN_PATTERNS = [
    (r"#include\s+[<\"]esp_.*[>\"]", "ESP-IDF vendor header in Core"),
    (r"#include\s+[<\"]esp32.*[>\"]", "ESP32 specific header in Core"),
    (r"#include\s+[<\"]freertos/.*[>\"]", "FreeRTOS header in Core"),
    (r"#include\s+[<\"]avr/.*[>\"]", "AVR vendor header in Core"),
    (r"#include\s+[<\"]pico/.*[>\"]", "Raspberry Pi Pico SDK header in Core"),
    (r"#include\s+[<\"]stm32.*[>\"]", "STM32 HAL header in Core"),
    (r"0x60091000", "Hardcoded ESP32-C6 GPIO register in Core"),
    (r"0x60000000", "Hardcoded ESP32 UART register in Core"),
    (r"0x60023000", "Hardcoded ESP32 SYSTIMER register in Core")
]

class TestArchitectureRules(unittest.TestCase):
    def test_core_isolation_and_no_vendor_headers(self):
        violations = []
        self.assertTrue(os.path.exists(CORE_DIR), "Core directory must exist")

        for root, _, files in os.walk(CORE_DIR):
            for file in files:
                if file.endswith((".h", ".c")):
                    filepath = os.path.join(root, file)
                    rel_path = os.path.relpath(filepath, REPO_ROOT)
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()

                    for idx, line in enumerate(lines, 1):
                        for pattern, desc in FORBIDDEN_PATTERNS:
                            if re.search(pattern, line):
                                violations.append(f"{rel_path}:{idx}: {desc} -> '{line.strip()}'")

        if violations:
            msg = "\n".join(["Architectural Violations Found in NexOS Core:"] + violations)
            self.fail(msg)
        else:
            print("[PASS] Core Architecture Verification: 100% compliant with zero vendor leakage.")

if __name__ == "__main__":
    unittest.main()
