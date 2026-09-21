#!/usr/bin/env python3
"""
NexOS Master Test Runner
Executes all unit, architectural compliance, target specification, and integration tests.
"""

import sys
import os
import unittest

def main():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(test_dir, ".."))
    sys.path.insert(0, repo_root)

    print("================================================================================")
    print("                      RUNNING NEXOS COMPREHENSIVE TEST SUITE                    ")
    print("================================================================================")

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=test_dir, pattern="test_*.py", top_level_dir=repo_root)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("================================================================================")
    if result.wasSuccessful():
        print(f" ALL NEXOS SYSTEM TESTS PASSED SUCCESSFULLY! ({result.testsRun} tests run, 100% compliance)")
        sys.exit(0)
    else:
        print(f" TESTS FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
        sys.exit(1)

if __name__ == "__main__":
    main()
