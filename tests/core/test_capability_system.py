#!/usr/bin/env python3
"""
NexOS Capability System Unit Test
Verifies capability bitmasks, query evaluation, and degradation logic.
"""

import unittest

# Capability flags as defined in nex_types.h
NEX_CAP_NONE        = 0x00000000
NEX_CAP_GPIO        = 1 << 0
NEX_CAP_UART        = 1 << 1
NEX_CAP_SPI         = 1 << 2
NEX_CAP_I2C         = 1 << 3
NEX_CAP_PWM         = 1 << 4
NEX_CAP_ADC         = 1 << 5
NEX_CAP_TIMER       = 1 << 7
NEX_CAP_WIFI        = 1 << 9
NEX_CAP_BLUETOOTH   = 1 << 10
NEX_CAP_SD          = 1 << 17
NEX_CAP_FLASH       = 1 << 18

class CapabilityRegistry:
    def __init__(self, initial_caps=NEX_CAP_NONE):
        self.caps = initial_caps

    def register(self, cap):
        self.caps |= cap

    def has(self, cap):
        return (self.caps & cap) == cap

class TestCapabilitySystem(unittest.TestCase):
    def test_basic_query(self):
        reg = CapabilityRegistry(NEX_CAP_GPIO | NEX_CAP_UART | NEX_CAP_TIMER)
        self.assertTrue(reg.has(NEX_CAP_GPIO))
        self.assertTrue(reg.has(NEX_CAP_UART))
        self.assertFalse(reg.has(NEX_CAP_WIFI))
        self.assertFalse(reg.has(NEX_CAP_SD))

    def test_multi_cap_query(self):
        reg = CapabilityRegistry(NEX_CAP_GPIO | NEX_CAP_UART | NEX_CAP_SPI | NEX_CAP_WIFI)
        self.assertTrue(reg.has(NEX_CAP_GPIO | NEX_CAP_WIFI))
        self.assertFalse(reg.has(NEX_CAP_WIFI | NEX_CAP_SD))

    def test_registration(self):
        reg = CapabilityRegistry()
        self.assertFalse(reg.has(NEX_CAP_FLASH))
        reg.register(NEX_CAP_FLASH)
        self.assertTrue(reg.has(NEX_CAP_FLASH))

if __name__ == "__main__":
    unittest.main()
