#!/usr/bin/env python3
"""
NexOS Application Package (.nex) Unit Test
Tests packaging lifecycle, manifest generation, checksum validation, and inspection.
"""

import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools", "packaging"))
import nex_pack

class TestPackageSystem(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.app_dir = os.path.join(self.test_dir.name, "test_app")
        os.makedirs(self.app_dir, exist_ok=True)

        # Create sample manifest
        with open(os.path.join(self.app_dir, "nexos.json"), "w", encoding="utf-8") as f:
            f.write('{"name":"test_app","version":"1.2.0","author":"Tester","required_capabilities":["GPIO"]}')

        with open(os.path.join(self.app_dir, "main.c"), "w", encoding="utf-8") as f:
            f.write('#include <nexos.h>\nvoid app_main(void) {}')

        self.pkg_out = os.path.join(self.test_dir.name, "test_app.nex")

    def tearDown(self):
        self.test_dir.cleanup()

    def test_create_and_inspect_package(self):
        ok = nex_pack.create_package(self.app_dir, self.pkg_out, target="esp32-c6")
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(self.pkg_out))
        self.assertGreater(os.path.getsize(self.pkg_out), 0)

        # Inspect
        ok_inspect = nex_pack.inspect_package(self.pkg_out)
        self.assertTrue(ok_inspect)

if __name__ == "__main__":
    unittest.main()
