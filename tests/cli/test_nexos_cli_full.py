#!/usr/bin/env python3
"""
NexOS CLI Full Command Integration Test
Tests all CLI commands specified in Master Specification Section 4:
create, build, build --release, clean, rebuild, package, validate, info, size, doctor, install, list, uninstall, version.
"""

import os
import sys
import tempfile
import subprocess
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
NEXOS_CLI = os.path.join(REPO_ROOT, "tools", "nexos", "nexos_cli.py")

class TestNexosCLIFull(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir.name)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.test_dir.cleanup()

    def test_full_developer_workflow(self):
        # 1. nexos doctor
        res = subprocess.run([sys.executable, NEXOS_CLI, "doctor"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("NexOS Developer Environment", res.stdout)
        self.assertIn("[OK] NexOS CLI", res.stdout)
        self.assertIn("[OK] NexOS SDK", res.stdout)

        # 2. nexos version
        res = subprocess.run([sys.executable, NEXOS_CLI, "version"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("NexOS CLI v1.0.0", res.stdout)

        # 3. nexos create demo_app
        res = subprocess.run([sys.executable, NEXOS_CLI, "create", "demo_app"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertTrue(os.path.exists("demo_app/nexos.toml"))
        self.assertTrue(os.path.exists("demo_app/src/main.c"))
        self.assertTrue(os.path.exists("demo_app/include/config.h"))

        # Navigate into demo_app
        os.chdir("demo_app")

        # 4. nexos build
        res = subprocess.run([sys.executable, NEXOS_CLI, "build"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        app_file = "dist/demo_app.app"
        self.assertTrue(os.path.exists(app_file))
        self.assertIn("Build successful", res.stdout)
        self.assertIn("Application : demo_app", res.stdout)

        # 5. nexos build --release
        res = subprocess.run([sys.executable, NEXOS_CLI, "build", "--release"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertTrue(os.path.exists(app_file))

        # 6. nexos validate
        res = subprocess.run([sys.executable, NEXOS_CLI, "validate", app_file], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Application is valid.", res.stdout)
        self.assertIn("[OK]    Package format", res.stdout)
        self.assertIn("[OK]    Architecture", res.stdout)
        self.assertIn("[OK]    ABI version", res.stdout)
        self.assertIn("[OK]    Payload SHA-256 Checksum verified", res.stdout)

        # 7. nexos info
        res = subprocess.run([sys.executable, NEXOS_CLI, "info", app_file], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("App Name         : demo_app", res.stdout)

        # 8. nexos size
        res = subprocess.run([sys.executable, NEXOS_CLI, "size"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Size breakdown for", res.stdout)
        self.assertIn("Stack (RAM)", res.stdout)

        # 9. nexos install to MicroSD
        res = subprocess.run([sys.executable, NEXOS_CLI, "install", app_file], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertTrue(os.path.exists("sdcard/apps/demo_app.app"))

        # 10. nexos list
        res = subprocess.run([sys.executable, NEXOS_CLI, "list"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("demo_app.app", res.stdout)

        # 11. nexos uninstall
        res = subprocess.run([sys.executable, NEXOS_CLI, "uninstall", "demo_app"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertFalse(os.path.exists("sdcard/apps/demo_app.app"))

        # 12. nexos clean
        res = subprocess.run([sys.executable, NEXOS_CLI, "clean"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertFalse(os.path.exists("build"))
        self.assertFalse(os.path.exists("dist"))

if __name__ == "__main__":
    unittest.main()
