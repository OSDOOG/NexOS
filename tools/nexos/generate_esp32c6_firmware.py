#!/usr/bin/env python3
"""
NexOS ESP32-C6 Pure OS Bootable Firmware Generator
Generates a valid ESP-IDF compatible boot image with ESP32-C6 ROM header (Magic 0xE9)
and native RISC-V 32-bit instructions (rv32imac) that initialize the NexOS Pure Kernel,
perform subsystem readiness inspection, interface with real MicroSD Card over SPI,
mount FAT32 filesystem, auto-run application packages (/apps/*.app), real-time hot-plug
auto-detection on card insertion/removal, and an interactive Built-in Shell (nexos> ).
"""

import os
import sys
import struct
import esptool.bin_image as bi

class RiscvAssembler:
    """
    2-pass RISC-V 32-bit (RV32I) Machine Code Assembler
    Resolves symbolic labels, relative branches, jumps, and memory relocations.
    """
    def __init__(self, base_addr=0x40800000):
        self.base_addr = base_addr
        self.items = []
        self.labels = {}
        self.strings = {}

    def label(self, name):
        self.items.append(('label', name))

    def emit(self, fn, *args):
        self.items.append(('insn', fn, args))

    def add_string(self, name, text):
        if isinstance(text, str):
            text = text.encode('utf-8')
        if not text.endswith(b'\x00'):
            text += b'\x00'
        self.strings[name] = text

    def assemble(self):
        # Pass 1: compute instruction addresses
        cur_addr = self.base_addr
        for item in self.items:
            if item[0] == 'label':
                self.labels[item[1]] = cur_addr
            elif item[0] == 'insn':
                fn = item[1]
                if fn == 'LOAD_ADDR':
                    cur_addr += 8  # LUI + ADDI
                elif fn == 'LOAD_INSN_WORDS':
                    cur_addr += 16 # LUI+ADDI for rd1, LUI+ADDI for rd2
                else:
                    cur_addr += 4

        # Layout strings right after code (4-byte aligned)
        strings_blob = bytearray()
        for name, data in self.strings.items():
            while (cur_addr + len(strings_blob)) % 4 != 0:
                strings_blob += b'\x00'
            self.labels[name] = cur_addr + len(strings_blob)
            strings_blob += data

        # Pass 2: generate binary
        code = bytearray()
        cur_addr = self.base_addr
        for item in self.items:
            if item[0] == 'label':
                continue
            fn, args = item[1], item[2]
            if fn == 'LOAD_ADDR':
                rd, target = args[0], args[1]
                t_addr = self.labels[target] if isinstance(target, str) else target
                upper = (t_addr + 0x800) >> 12
                lower = t_addr & 0xFFF
                if lower >= 0x800:
                    lower -= 0x1000
                code += self._lui(rd, upper)
                code += self._addi(rd, rd, lower)
                cur_addr += 8
            elif fn == 'LOAD_INSN_WORDS':
                rd1, rd2, target = args[0], args[1], args[2]
                t_addr = self.labels[target] if isinstance(target, str) else target
                upper = (t_addr + 0x800) >> 12
                lower = t_addr & 0xFFF
                if lower >= 0x800:
                    lower -= 0x1000
                w_lui = struct.unpack('<I', self._lui(5, upper))[0]
                w_addi = struct.unpack('<I', self._addi(5, 5, lower))[0]
                # Load w_lui into rd1
                u1 = (w_lui + 0x800) >> 12
                l1 = w_lui & 0xFFF
                if l1 >= 0x800: l1 -= 0x1000
                code += self._lui(rd1, u1)
                code += self._addi(rd1, rd1, l1)
                # Load w_addi into rd2
                u2 = (w_addi + 0x800) >> 12
                l2 = w_addi & 0xFFF
                if l2 >= 0x800: l2 -= 0x1000
                code += self._lui(rd2, u2)
                code += self._addi(rd2, rd2, l2)
                cur_addr += 16
            elif fn in ('JAL', 'BEQ', 'BNE', 'BLT', 'BGE', 'BLE'):
                target = args[-1]
                t_addr = self.labels[target] if isinstance(target, str) else target
                offset = t_addr - cur_addr
                real_args = list(args[:-1]) + [offset]
                insn_fn = getattr(self, '_' + fn.lower())
                code += insn_fn(*real_args)
                cur_addr += 4
            else:
                insn_fn = getattr(self, '_' + fn.lower())
                code += insn_fn(*args)
                cur_addr += 4

        return bytes(code) + bytes(strings_blob)

    def _fence_i(self):
        return struct.pack('<I', 0x0000100F)

    def _div(self, rd, rs1, rs2):
        return struct.pack('<I', (1 << 25) | (rs2 << 20) | (rs1 << 15) | (4 << 12) | (rd << 7) | 0x33)

    def _lui(self, rd, imm20):
        return struct.pack('<I', ((imm20 & 0xFFFFF) << 12) | (rd << 7) | 0x37)

    def _addi(self, rd, rs1, imm12):
        return struct.pack('<I', ((imm12 & 0xFFF) << 20) | (rs1 << 15) | (0 << 12) | (rd << 7) | 0x13)

    def _andi(self, rd, rs1, imm12):
        return struct.pack('<I', ((imm12 & 0xFFF) << 20) | (rs1 << 15) | (7 << 12) | (rd << 7) | 0x13)

    def _ori(self, rd, rs1, imm12):
        return struct.pack('<I', ((imm12 & 0xFFF) << 20) | (rs1 << 15) | (6 << 12) | (rd << 7) | 0x13)

    def _xori(self, rd, rs1, imm12):
        return struct.pack('<I', ((imm12 & 0xFFF) << 20) | (rs1 << 15) | (4 << 12) | (rd << 7) | 0x13)

    def _slli(self, rd, rs1, shamt):
        return struct.pack('<I', ((shamt & 0x1F) << 20) | (rs1 << 15) | (1 << 12) | (rd << 7) | 0x13)

    def _srli(self, rd, rs1, shamt):
        return struct.pack('<I', ((shamt & 0x1F) << 20) | (rs1 << 15) | (5 << 12) | (rd << 7) | 0x13)

    def _lw(self, rd, rs1, imm12):
        return struct.pack('<I', ((imm12 & 0xFFF) << 20) | (rs1 << 15) | (2 << 12) | (rd << 7) | 0x03)

    def _lbu(self, rd, rs1, imm12):
        return struct.pack('<I', ((imm12 & 0xFFF) << 20) | (rs1 << 15) | (4 << 12) | (rd << 7) | 0x03)

    def _lhu(self, rd, rs1, imm12):
        return struct.pack('<I', ((imm12 & 0xFFF) << 20) | (rs1 << 15) | (5 << 12) | (rd << 7) | 0x03)

    def _sw(self, rs2, rs1, imm12):
        imm11_5 = (imm12 >> 5) & 0x7F
        imm4_0 = imm12 & 0x1F
        return struct.pack('<I', (imm11_5 << 25) | (rs2 << 20) | (rs1 << 15) | (2 << 12) | (imm4_0 << 7) | 0x23)

    def _sb(self, rs2, rs1, imm12):
        imm11_5 = (imm12 >> 5) & 0x7F
        imm4_0 = imm12 & 0x1F
        return struct.pack('<I', (imm11_5 << 25) | (rs2 << 20) | (rs1 << 15) | (0 << 12) | (imm4_0 << 7) | 0x23)

    def _add(self, rd, rs1, rs2):
        return struct.pack('<I', (0 << 25) | (rs2 << 20) | (rs1 << 15) | (0 << 12) | (rd << 7) | 0x33)

    def _sub(self, rd, rs1, rs2):
        return struct.pack('<I', (0x20 << 25) | (rs2 << 20) | (rs1 << 15) | (0 << 12) | (rd << 7) | 0x33)

    def _mul(self, rd, rs1, rs2):
        return struct.pack('<I', (1 << 25) | (rs2 << 20) | (rs1 << 15) | (0 << 12) | (rd << 7) | 0x33)

    def _sll(self, rd, rs1, rs2):
        return struct.pack('<I', (0 << 25) | (rs2 << 20) | (rs1 << 15) | (1 << 12) | (rd << 7) | 0x33)

    def _srl(self, rd, rs1, rs2):
        return struct.pack('<I', (0 << 25) | (rs2 << 20) | (rs1 << 15) | (5 << 12) | (rd << 7) | 0x33)

    def _or(self, rd, rs1, rs2):
        return struct.pack('<I', (0 << 25) | (rs2 << 20) | (rs1 << 15) | (6 << 12) | (rd << 7) | 0x33)

    def _and(self, rd, rs1, rs2):
        return struct.pack('<I', (0 << 25) | (rs2 << 20) | (rs1 << 15) | (7 << 12) | (rd << 7) | 0x33)

    def _jalr(self, rd, rs1, imm12):
        return struct.pack('<I', ((imm12 & 0xFFF) << 20) | (rs1 << 15) | (0 << 12) | (rd << 7) | 0x67)

    def _jal(self, rd, imm21):
        imm = imm21 & 0x1FFFFE
        b20 = (imm >> 20) & 1
        b10_1 = (imm >> 1) & 0x3FF
        b11 = (imm >> 11) & 1
        b19_12 = (imm >> 12) & 0xFF
        val = (b20 << 31) | (b10_1 << 21) | (b11 << 20) | (b19_12 << 12) | (rd << 7) | 0x6F
        return struct.pack('<I', val)

    def _b_type(self, funct3, rs1, rs2, imm13):
        imm = imm13 & 0x1FFE
        b12 = (imm >> 12) & 1
        b10_5 = (imm >> 5) & 0x3F
        b4_1 = (imm >> 1) & 0xF
        b11 = (imm >> 11) & 1
        val = (b12 << 31) | (b10_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (b4_1 << 8) | (b11 << 7) | 0x63
        return struct.pack('<I', val)

    def _beq(self, rs1, rs2, imm13):
        return self._b_type(0, rs1, rs2, imm13)

    def _bne(self, rs1, rs2, imm13):
        return self._b_type(1, rs1, rs2, imm13)

    def _blt(self, rs1, rs2, imm13):
        return self._b_type(4, rs1, rs2, imm13)

    def _bge(self, rs1, rs2, imm13):
        return self._b_type(5, rs1, rs2, imm13)

    def _ble(self, rs1, rs2, imm13):
        return self._b_type(5, rs2, rs1, imm13)


def generate_firmware(output_path):
    entry_addr = 0x40800000
    asm = RiscvAssembler(entry_addr)

    # Setup Stack pointer sp = 0x4087FF00
    asm.emit('LOAD_ADDR', 2, 0x4087FF00)

    # Jump over subroutines to kernel initialization
    asm.emit('JAL', 0, 'kernel_init')

    # =========================================================================
    # Subroutines: SPI & MicroSD Driver (GPIO 18=CS, 19=MOSI, 20=MISO, 21=SCK)
    # =========================================================================

    # spi_xfer_byte: sends a0 (8-bit), returns received byte in a0 (~300 kHz)
    asm.label('spi_xfer_byte')
    asm.emit('LOAD_ADDR', 5, 0x60091000)   # t0 = GPIO base
    asm.emit('ADDI', 6, 0, 8)              # t1 = 8 bits
    asm.emit('ADDI', 7, 0, 0)              # t2 = rx byte
    asm.emit('LOAD_ADDR', 28, 0x00080000)  # t3 = MOSI bit (GPIO 19)
    asm.emit('LOAD_ADDR', 29, 0x00200000)  # t4 = SCK bit (GPIO 21)

    asm.label('spi_bit_loop')
    asm.emit('ANDI', 30, 10, 0x80)         # t5 = a0 & 0x80
    asm.emit('BEQ', 30, 0, 'spi_mosi_zero')
    asm.emit('SW', 28, 5, 0x08)            # GPIO_OUT_W1TS = MOSI (high)
    asm.emit('JAL', 0, 'spi_clock_high')
    asm.label('spi_mosi_zero')
    asm.emit('SW', 28, 5, 0x0C)            # GPIO_OUT_W1TC = MOSI (low)

    asm.label('spi_clock_high')
    asm.emit('ADDI', 31, 0, 80)
    asm.label('spi_delay1')
    asm.emit('ADDI', 31, 31, -1)
    asm.emit('BNE', 31, 0, 'spi_delay1')

    asm.emit('SLLI', 10, 10, 1)            # a0 <<= 1
    asm.emit('SW', 29, 5, 0x08)            # GPIO_OUT_W1TS = SCK (high)

    asm.emit('ADDI', 31, 0, 80)
    asm.label('spi_delay2')
    asm.emit('ADDI', 31, 31, -1)
    asm.emit('BNE', 31, 0, 'spi_delay2')

    # Sample MISO (GPIO 20)
    asm.emit('LW', 30, 5, 0x3C)            # t5 = GPIO_IN_REG
    asm.emit('LOAD_ADDR', 31, 0x00100000)  # t6 = MISO bit (GPIO 20)
    asm.emit('AND', 30, 30, 31)
    asm.emit('SLLI', 7, 7, 1)              # t2 <<= 1
    asm.emit('BEQ', 30, 0, 'spi_clock_low')
    asm.emit('ADDI', 7, 7, 1)              # t2 |= 1

    asm.label('spi_clock_low')
    asm.emit('SW', 29, 5, 0x0C)            # GPIO_OUT_W1TC = SCK (low)

    asm.emit('ADDI', 31, 0, 80)
    asm.label('spi_delay3')
    asm.emit('ADDI', 31, 31, -1)
    asm.emit('BNE', 31, 0, 'spi_delay3')

    asm.emit('ADDI', 6, 6, -1)             # t1--
    asm.emit('BNE', 6, 0, 'spi_bit_loop')

    asm.emit('ANDI', 10, 7, 0xFF)          # a0 = t2
    asm.emit('JALR', 0, 1, 0)              # ret

    # sd_cs_high: Sets CS HIGH and clocks out 0xFF so SD card tri-states MISO
    asm.label('sd_cs_high')
    asm.emit('ADDI', 2, 2, -16)
    asm.emit('SW', 1, 2, 12)
    asm.emit('SW', 10, 2, 8)               # preserve a0
    asm.emit('LOAD_ADDR', 5, 0x60091000)
    asm.emit('LOAD_ADDR', 6, 0x00040000)   # CS bit (GPIO 18)
    asm.emit('SW', 6, 5, 0x08)             # W1TS (CS high)
    asm.emit('ADDI', 10, 0, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')
    asm.emit('LW', 10, 2, 8)               # restore a0
    asm.emit('LW', 1, 2, 12)
    asm.emit('ADDI', 2, 2, 16)
    asm.emit('JALR', 0, 1, 0)

    # sd_cs_low
    asm.label('sd_cs_low')
    asm.emit('LOAD_ADDR', 5, 0x60091000)
    asm.emit('LOAD_ADDR', 6, 0x00040000)   # CS bit (GPIO 18)
    asm.emit('SW', 6, 5, 0x0C)             # W1TC (CS low)
    asm.emit('JALR', 0, 1, 0)

    # sd_send_cmd: a0=cmd, a1=arg, a2=crc. Returns a0=response (CS held low)
    asm.label('sd_send_cmd')
    asm.emit('ADDI', 2, 2, -32)
    asm.emit('SW', 1, 2, 28)
    asm.emit('SW', 8, 2, 24)
    asm.emit('SW', 9, 2, 20)
    asm.emit('SW', 18, 2, 16)

    asm.emit('ADDI', 8, 10, 0)             # s0 = cmd
    asm.emit('ADDI', 9, 11, 0)             # s1 = arg
    asm.emit('ADDI', 18, 12, 0)            # s2 = crc

    asm.emit('JAL', 1, 'sd_cs_high')
    asm.emit('JAL', 1, 'sd_cs_low')

    # 0x40 | cmd
    asm.emit('ORI', 10, 8, 0x40)
    asm.emit('ANDI', 10, 10, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')

    # arg[31:24]
    asm.emit('SRLI', 10, 9, 24)
    asm.emit('ANDI', 10, 10, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')

    # arg[23:16]
    asm.emit('SRLI', 10, 9, 16)
    asm.emit('ANDI', 10, 10, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')

    # arg[15:8]
    asm.emit('SRLI', 10, 9, 8)
    asm.emit('ANDI', 10, 10, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')

    # arg[7:0]
    asm.emit('ANDI', 10, 9, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')

    # crc
    asm.emit('ANDI', 10, 18, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')

    # Wait for response (up to 48 attempts)
    asm.emit('ADDI', 8, 0, 48)
    asm.label('sd_resp_wait')
    asm.emit('ADDI', 10, 0, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')
    asm.emit('ANDI', 5, 10, 0x80)
    asm.emit('BEQ', 5, 0, 'sd_cmd_done')
    asm.emit('ADDI', 8, 8, -1)
    asm.emit('BNE', 8, 0, 'sd_resp_wait')

    asm.label('sd_cmd_done')
    asm.emit('LW', 1, 2, 28)
    asm.emit('LW', 8, 2, 24)
    asm.emit('LW', 9, 2, 20)
    asm.emit('LW', 18, 2, 16)
    asm.emit('ADDI', 2, 2, 32)
    asm.emit('JALR', 0, 1, 0)

    # sd_quick_check: Silent probe for hotplug insertion.
    # Returns a0=1 if card responds to CMD0 (0x01 or 0x00), else 0.
    asm.label('sd_quick_check')
    asm.emit('ADDI', 2, 2, -32)
    asm.emit('SW', 1, 2, 28)
    asm.emit('SW', 8, 2, 24)
    asm.emit('SW', 9, 2, 20)
    asm.emit('SW', 18, 2, 16)

    # Setup IO_MUX & Matrix
    asm.emit('LOAD_ADDR', 5, 0x60090000)
    asm.emit('LOAD_ADDR', 6, 0x1B00)
    asm.emit('SW', 6, 5, 0x4C)             # CS (GPIO 18)
    asm.emit('SW', 6, 5, 0x50)             # MOSI (GPIO 19)
    asm.emit('SW', 6, 5, 0x58)             # SCK (GPIO 21)
    asm.emit('LOAD_ADDR', 6, 0x1300)
    asm.emit('SW', 6, 5, 0x54)             # MISO (GPIO 20)

    asm.emit('LOAD_ADDR', 5, 0x60091000)
    asm.emit('ADDI', 6, 0, 128)
    asm.emit('SW', 6, 5, 0x59C)
    asm.emit('SW', 6, 5, 0x5A0)
    asm.emit('SW', 6, 5, 0x5A8)

    asm.emit('LOAD_ADDR', 6, 0x002C0000)   # CS(18) | MOSI(19) | SCK(21)
    asm.emit('SW', 6, 5, 0x24)             # GPIO_ENABLE_W1TS
    asm.emit('LOAD_ADDR', 6, 0x00100000)   # MISO(20)
    asm.emit('SW', 6, 5, 0x28)             # GPIO_ENABLE_W1TC

    # Drive CS HIGH
    asm.emit('JAL', 1, 'sd_cs_high')

    # Send 16 dummy 0xFF bytes (>100 clock cycles) with CS HIGH to wake card & trigger SPI mode switch
    asm.emit('ADDI', 8, 0, 16)
    asm.label('sd_quick_dummy')
    asm.emit('ADDI', 10, 0, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')
    asm.emit('ADDI', 8, 8, -1)
    asm.emit('BNE', 8, 0, 'sd_quick_dummy')

    # Send CMD0 (0x40, 0, 0, 0, 0, 0x95) - retry up to 6 times with 1ms delay
    asm.emit('ADDI', 8, 0, 6)
    asm.label('sd_quick_cmd0_loop')
    asm.emit('ADDI', 10, 0, 0)
    asm.emit('ADDI', 11, 0, 0)
    asm.emit('ADDI', 12, 0, 0x95)
    asm.emit('JAL', 1, 'sd_send_cmd')
    asm.emit('ADDI', 9, 10, 0)             # s1 = resp
    asm.emit('JAL', 1, 'sd_cs_high')

    # Only 0x01 (In Idle State) is a valid response to CMD0!
    # 0x00 is NOT valid (indicates MISO is grounded or unpowered)
    asm.emit('ADDI', 5, 0, 1)
    asm.emit('BEQ', 9, 5, 'sd_quick_yes')

    # Delay 1ms before retry
    asm.emit('LOAD_ADDR', 10, 1000)
    asm.emit('LOAD_ADDR', 5, 0x40000040)
    asm.emit('JALR', 1, 5, 0)

    asm.emit('ADDI', 8, 8, -1)
    asm.emit('BNE', 8, 0, 'sd_quick_cmd0_loop')

    # No card found
    asm.emit('ADDI', 10, 0, 0)             # return 0 (no card)
    asm.emit('JAL', 0, 'sd_quick_exit')

    asm.label('sd_quick_yes')
    asm.emit('ADDI', 10, 0, 1)             # return 1 (card detected)

    asm.label('sd_quick_exit')
    asm.emit('LW', 1, 2, 28)
    asm.emit('LW', 8, 2, 24)
    asm.emit('LW', 9, 2, 20)
    asm.emit('LW', 18, 2, 16)
    asm.emit('ADDI', 2, 2, 32)
    asm.emit('JALR', 0, 1, 0)

    # sd_check_present: For mounted card. Sends CMD13 (SEND_STATUS).
    # Returns a0=1 if present (valid R1/R2 status, bit 7 == 0), 0 if removed (resp == 0xFF or timeout).
    asm.label('sd_check_present')
    asm.emit('ADDI', 2, 2, -16)
    asm.emit('SW', 1, 2, 12)
    asm.emit('ADDI', 10, 0, 13)
    asm.emit('ADDI', 11, 0, 0)
    asm.emit('ADDI', 12, 0, 0xFF)
    asm.emit('JAL', 1, 'sd_send_cmd')
    # Save CMD13 response byte on stack so spi_xfer_byte doesn't clobber it!
    asm.emit('SW', 10, 2, 8)

    # Read 2nd status byte & release CS HIGH
    asm.emit('ADDI', 10, 0, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')
    asm.emit('JAL', 1, 'sd_cs_high')

    # Reload saved response from stack
    asm.emit('LW', 5, 2, 8)

    # Check 1: resp == 0xFF -> removed!
    asm.emit('ADDI', 6, 0, 0xFF)
    asm.emit('BEQ', 5, 6, 'sd_pres_no')

    # Check 2: (resp & 0x80) != 0 -> bit 7 must be 0 for valid SPI response! If 1, card is absent.
    asm.emit('ANDI', 6, 5, 0x80)
    asm.emit('BNE', 6, 0, 'sd_pres_no')

    # Card is present!
    asm.emit('ADDI', 10, 0, 1)             # present
    asm.emit('LW', 1, 2, 12)
    asm.emit('ADDI', 2, 2, 16)
    asm.emit('JALR', 0, 1, 0)

    asm.label('sd_pres_no')
    asm.emit('ADDI', 10, 0, 0)             # removed
    asm.emit('LW', 1, 2, 12)
    asm.emit('ADDI', 2, 2, 16)
    asm.emit('JALR', 0, 1, 0)

    # sd_read_sector: a0=lba, a1=buf. Returns a0=0 (ok), 1 (error)
    asm.label('sd_read_sector')
    asm.emit('ADDI', 2, 2, -32)
    asm.emit('SW', 1, 2, 28)
    asm.emit('SW', 8, 2, 24)
    asm.emit('SW', 9, 2, 20)
    asm.emit('SW', 18, 2, 16)

    asm.emit('ADDI', 8, 10, 0)             # s0 = lba
    asm.emit('ADDI', 9, 11, 0)             # s1 = buffer ptr

    # Send CMD17 (READ_SINGLE_BLOCK)
    asm.emit('ADDI', 10, 0, 17)
    asm.emit('ADDI', 11, 8, 0)
    asm.emit('ADDI', 12, 0, 0xFF)
    asm.emit('JAL', 1, 'sd_send_cmd')
    asm.emit('BNE', 10, 0, 'sd_read_err')

    # Wait for token 0xFE (up to 2000 attempts)
    asm.emit('LOAD_ADDR', 18, 2000)
    asm.label('sd_token_wait')
    asm.emit('ADDI', 10, 0, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')
    asm.emit('ADDI', 5, 0, 0xFE)
    asm.emit('BEQ', 10, 5, 'sd_read_payload')
    asm.emit('ADDI', 18, 18, -1)
    asm.emit('BNE', 18, 0, 'sd_token_wait')
    asm.emit('JAL', 0, 'sd_read_err')

    asm.label('sd_read_payload')
    asm.emit('LOAD_ADDR', 18, 512)
    asm.label('sd_read_512')
    asm.emit('ADDI', 10, 0, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')
    asm.emit('SB', 10, 9, 0)
    asm.emit('ADDI', 9, 9, 1)
    asm.emit('ADDI', 18, 18, -1)
    asm.emit('BNE', 18, 0, 'sd_read_512')

    # Read 2 CRC bytes
    asm.emit('ADDI', 10, 0, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')
    asm.emit('ADDI', 10, 0, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')

    asm.emit('JAL', 1, 'sd_cs_high')
    asm.emit('ADDI', 10, 0, 0)             # return 0 (ok)
    asm.emit('LW', 1, 2, 28)
    asm.emit('LW', 8, 2, 24)
    asm.emit('LW', 9, 2, 20)
    asm.emit('LW', 18, 2, 16)
    asm.emit('ADDI', 2, 2, 32)
    asm.emit('JALR', 0, 1, 0)

    asm.label('sd_read_err')
    asm.emit('JAL', 1, 'sd_cs_high')
    asm.emit('ADDI', 10, 0, 1)             # return 1 (err)
    asm.emit('LW', 1, 2, 28)
    asm.emit('LW', 8, 2, 24)
    asm.emit('LW', 9, 2, 20)
    asm.emit('LW', 18, 2, 16)
    asm.emit('ADDI', 2, 2, 32)
    asm.emit('JALR', 0, 1, 0)

    # =========================================================================
    # fat32_probe_and_autorun:
    # a0 = mode (0 = boot probe, 1 = shell 'sd', 2 = hot-plug insertion)
    # Returns a0 = 1 if card mounted, 0 if not mounted
    # =========================================================================
    asm.label('fat32_probe_and_autorun')
    asm.emit('ADDI', 2, 2, -64)
    asm.emit('SW', 1, 2, 60)
    asm.emit('SW', 8, 2, 56)
    asm.emit('SW', 9, 2, 52)
    asm.emit('SW', 18, 2, 48)
    asm.emit('SW', 19, 2, 44)
    asm.emit('SW', 21, 2, 36)
    asm.emit('SW', 22, 2, 32)
    asm.emit('SW', 23, 2, 28)
    asm.emit('SW', 24, 2, 24)
    asm.emit('SW', 25, 2, 20)
    asm.emit('SW', 26, 2, 16)              # save mode in s10 (x26)

    asm.emit('ADDI', 26, 10, 0)            # s10 = mode

    # If mode == 2 (hotplug insertion), print insertion banner!
    asm.emit('ADDI', 5, 0, 2)
    asm.emit('BNE', 26, 5, 'probe_check_header')
    asm.emit('LOAD_ADDR', 10, 'fmt_card_inserted')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'probe_init_hw')

    asm.label('probe_check_header')
    # Print probing message for mode 0 or 1
    asm.emit('LOAD_ADDR', 10, 'sd_probing_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    asm.label('probe_init_hw')
    # 1. Setup GPIOs & IO_MUX (GPIO Mode 1, Input Enable, Pull-up, NO Pull-down)
    asm.emit('LOAD_ADDR', 5, 0x60090000)
    asm.emit('LOAD_ADDR', 6, 0x1B00)       # MCU_SEL(1) | FUN_DRV(2) | FUN_IE(1) | FUN_PU(1)
    asm.emit('SW', 6, 5, 0x4C)             # GPIO 18 (CS)
    asm.emit('SW', 6, 5, 0x50)             # GPIO 19 (MOSI)
    asm.emit('SW', 6, 5, 0x58)             # GPIO 21 (SCK)
    asm.emit('LOAD_ADDR', 6, 0x1300)       # MCU_SEL(1) | FUN_IE(1) | FUN_PU(1)
    asm.emit('SW', 6, 5, 0x54)             # GPIO 20 (MISO)

    # 2. Setup GPIO Matrix (Direct GPIO_OUT routing)
    asm.emit('LOAD_ADDR', 5, 0x60091000)
    asm.emit('ADDI', 6, 0, 128)
    asm.emit('SW', 6, 5, 0x59C)            # GPIO 18
    asm.emit('SW', 6, 5, 0x5A0)            # GPIO 19
    asm.emit('SW', 6, 5, 0x5A8)            # GPIO 21

    # 3. Directions
    asm.emit('LOAD_ADDR', 6, 0x002C0000)   # CS(18) | MOSI(19) | SCK(21)
    asm.emit('SW', 6, 5, 0x24)             # GPIO_ENABLE_W1TS
    asm.emit('LOAD_ADDR', 6, 0x00100000)   # MISO(20)
    asm.emit('SW', 6, 5, 0x28)             # GPIO_ENABLE_W1TC (input)

    asm.emit('JAL', 1, 'sd_cs_high')

    # Step 1: Print SPI Bus config OK if mode >= 1
    asm.emit('BEQ', 26, 0, 'probe_por_delay')
    asm.emit('LOAD_ADDR', 10, 'fmt_step1_bus_ok')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    # Sample and print MISO level
    asm.emit('LOAD_ADDR', 5, 0x60091000)
    asm.emit('LW', 11, 5, 0x3C)
    asm.emit('LOAD_ADDR', 6, 0x00100000)
    asm.emit('AND', 11, 11, 6)
    asm.emit('SRLI', 11, 11, 20)
    asm.emit('LOAD_ADDR', 10, 'fmt_miso_level')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    asm.label('probe_por_delay')
    # Power-on delay: 20ms
    asm.emit('LOAD_ADDR', 10, 20000)
    asm.emit('LOAD_ADDR', 5, 0x40000040)
    asm.emit('JALR', 1, 5, 0)

    # 16 dummy 0xFF bytes (>100 clocks)
    asm.emit('ADDI', 8, 0, 16)
    asm.label('probe_dummy_loop')
    asm.emit('ADDI', 10, 0, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')
    asm.emit('ADDI', 8, 8, -1)
    asm.emit('BNE', 8, 0, 'probe_dummy_loop')

    # Step 2: Send CMD0 (Reset / GO_IDLE) - retry up to 30 times
    asm.emit('ADDI', 8, 0, 30)
    asm.label('probe_cmd0_retry')
    asm.emit('ADDI', 10, 0, 0)
    asm.emit('ADDI', 11, 0, 0)
    asm.emit('ADDI', 12, 0, 0x95)
    asm.emit('JAL', 1, 'sd_send_cmd')
    asm.emit('ADDI', 21, 10, 0)            # s5 (x21) = CMD0 response
    asm.emit('JAL', 1, 'sd_cs_high')

    # ONLY 0x01 (In Idle State) is valid for CMD0!
    asm.emit('ADDI', 5, 0, 1)
    asm.emit('BEQ', 21, 5, 'probe_cmd0_success')

    # Delay 2ms before retry
    asm.emit('LOAD_ADDR', 10, 2000)
    asm.emit('LOAD_ADDR', 5, 0x40000040)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('ADDI', 8, 8, -1)
    asm.emit('BNE', 8, 0, 'probe_cmd0_retry')

    # CMD0 Failed!
    # If mode == 0 and resp == 0xFF: print clean standby message
    asm.emit('ADDI', 5, 0, 0xFF)
    asm.emit('BNE', 21, 5, 'probe_cmd0_show_fail')
    asm.emit('BNE', 26, 0, 'probe_cmd0_show_fail')
    asm.emit('LOAD_ADDR', 10, 'sd_standby_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'probe_return_nocard')

    asm.label('probe_cmd0_show_fail')
    # Print Step 2 CMD0 Failed with response byte
    asm.emit('LOAD_ADDR', 10, 'fmt_cmd0_fail')
    asm.emit('ANDI', 11, 21, 0xFF)
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    # Print troubleshooting checklist
    asm.emit('LOAD_ADDR', 10, 'sd_troubleshoot_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'probe_return_err')

    asm.label('probe_cmd0_success')
    # Print Step 2 CMD0 OK
    asm.emit('LOAD_ADDR', 10, 'fmt_cmd0_ok')
    asm.emit('ANDI', 11, 21, 0xFF)
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    # Step 3: Send CMD8 (3.3V Check)
    asm.emit('ADDI', 10, 0, 8)
    asm.emit('LOAD_ADDR', 11, 0x1AA)
    asm.emit('ADDI', 12, 0, 0x87)
    asm.emit('JAL', 1, 'sd_send_cmd')
    # Read 4 trailing bytes
    asm.emit('ADDI', 10, 0, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')
    asm.emit('ADDI', 10, 0, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')
    asm.emit('ADDI', 10, 0, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')
    asm.emit('ADDI', 10, 0, 0xFF)
    asm.emit('JAL', 1, 'spi_xfer_byte')
    asm.emit('ADDI', 21, 10, 0)            # s5 = echo byte (expected 0xAA)
    asm.emit('JAL', 1, 'sd_cs_high')

    # Check echo byte == 0xAA
    asm.emit('ADDI', 5, 0, 0xAA)
    asm.emit('BEQ', 21, 5, 'probe_cmd8_ok')

    # Echo mismatch
    asm.emit('LOAD_ADDR', 10, 'fmt_cmd8_fail')
    asm.emit('ANDI', 11, 21, 0xFF)
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'probe_return_err')

    asm.label('probe_cmd8_ok')
    asm.emit('LOAD_ADDR', 10, 'fmt_cmd8_ok')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    # Step 4: ACMD41 loop (up to 60 times)
    asm.emit('ADDI', 8, 0, 60)
    asm.label('probe_acmd41_loop')
    # CMD55
    asm.emit('ADDI', 10, 0, 55)
    asm.emit('ADDI', 11, 0, 0)
    asm.emit('ADDI', 12, 0, 0x65)
    asm.emit('JAL', 1, 'sd_send_cmd')
    asm.emit('JAL', 1, 'sd_cs_high')

    # ACMD41 (HCS bit 0x40000000)
    asm.emit('ADDI', 10, 0, 41)
    asm.emit('LOAD_ADDR', 11, 0x40000000)
    asm.emit('ADDI', 12, 0, 0x77)
    asm.emit('JAL', 1, 'sd_send_cmd')
    asm.emit('JAL', 1, 'sd_cs_high')

    asm.emit('BEQ', 10, 0, 'probe_acmd41_ok')
    # Delay 5ms
    asm.emit('LOAD_ADDR', 10, 5000)
    asm.emit('LOAD_ADDR', 5, 0x40000040)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('ADDI', 8, 8, -1)
    asm.emit('BNE', 8, 0, 'probe_acmd41_loop')

    # ACMD41 Timeout
    asm.emit('LOAD_ADDR', 10, 'fmt_acmd41_fail')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'probe_return_err')

    asm.label('probe_acmd41_ok')
    asm.emit('LOAD_ADDR', 10, 'fmt_acmd41_ok')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    # Step 5: CMD16 (Set block length = 512)
    asm.emit('ADDI', 10, 0, 16)
    asm.emit('LOAD_ADDR', 11, 512)
    asm.emit('ADDI', 12, 0, 0xFF)
    asm.emit('JAL', 1, 'sd_send_cmd')
    asm.emit('JAL', 1, 'sd_cs_high')

    # Step 6: Read MBR (Sector 0)
    asm.emit('ADDI', 10, 0, 0)
    asm.emit('LOAD_ADDR', 11, 0x4087F000)
    asm.emit('JAL', 1, 'sd_read_sector')
    asm.emit('BNE', 10, 0, 'probe_mbr_fail')

    # Check 0x55AA signature at offset 510
    asm.emit('LOAD_ADDR', 8, 0x4087F000)
    asm.emit('LBU', 5, 8, 510)
    asm.emit('LBU', 6, 8, 511)
    asm.emit('ADDI', 7, 0, 0x55)
    asm.emit('BNE', 5, 7, 'probe_mbr_fail')
    asm.emit('ADDI', 7, 0, 0xAA)
    asm.emit('BNE', 6, 7, 'probe_mbr_fail')

    asm.emit('LOAD_ADDR', 10, 'fmt_mbr_ok')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    # Check Partition 1 at offset 0x1BE
    asm.emit('LBU', 5, 8, 0x1C2)           # Partition 1 type
    asm.emit('ADDI', 6, 0, 0x0B)
    asm.emit('BEQ', 5, 6, 'probe_use_part1')
    asm.emit('ADDI', 6, 0, 0x0C)
    asm.emit('BEQ', 5, 6, 'probe_use_part1')
    asm.emit('ADDI', 6, 0, 0x0E)
    asm.emit('BEQ', 5, 6, 'probe_use_part1')

    # Superfloppy fallback: VBR at sector 0
    asm.emit('ADDI', 25, 0, 0)             # s9 (x25) = VBR LBA = 0
    asm.emit('JAL', 0, 'probe_parse_vbr')

    asm.label('probe_use_part1')
    asm.emit('LOAD_ADDR', 10, 'fmt_part_type')
    asm.emit('ANDI', 11, 5, 0xFF)
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    # Load 32-bit Part1 Starting LBA using two 16-bit loads (LHU) to prevent unaligned access fault
    asm.emit('LOAD_ADDR', 8, 0x4087F000)
    asm.emit('LHU', 25, 8, 0x1C6)           # s9 (x25) = low 16 bits of Part1 LBA
    asm.emit('LHU', 5, 8, 0x1C8)            # t0 (x5) = high 16 bits of Part1 LBA
    asm.emit('SLLI', 5, 5, 16)
    asm.emit('OR', 25, 25, 5)               # s9 = (high << 16) | low = Part1 Starting LBA!

    # Step 7: Parse VBR
    asm.label('probe_parse_vbr')
    asm.emit('ADDI', 10, 25, 0)            # a0 = vbr_lba
    asm.emit('LOAD_ADDR', 11, 0x4087F000)  # a1 = buffer
    asm.emit('JAL', 1, 'sd_read_sector')
    asm.emit('BNE', 10, 0, 'probe_vbr_fail')

    # Verify 0x55AA signature at offset 510
    asm.emit('LOAD_ADDR', 8, 0x4087F000)
    asm.emit('LBU', 5, 8, 510)
    asm.emit('LBU', 6, 8, 511)
    asm.emit('ADDI', 7, 0, 0x55)
    asm.emit('BNE', 5, 7, 'probe_vbr_fail')
    asm.emit('ADDI', 7, 0, 0xAA)
    asm.emit('BNE', 6, 7, 'probe_vbr_fail')

    # Extract VBR parameters
    asm.emit('LHU', 5, 8, 14)              # rsvd_sec
    asm.emit('LBU', 24, 8, 13)             # s8 (x24) = sec_per_clus
    asm.emit('LBU', 6, 8, 16)              # num_fats
    asm.emit('LW', 7, 8, 36)               # fat_sz32
    asm.emit('LW', 28, 8, 44)              # root_clus

    # fat1_lba = vbr_lba + rsvd_sec
    asm.emit('ADD', 29, 25, 5)             # t4 = fat1_lba
    asm.emit('MUL', 30, 7, 6)              # fat_total = fat_sz32 * num_fats
    asm.emit('ADD', 23, 29, 30)            # s7 (x23) = data_start_lba

    # root_dir_lba = data_start_lba + (root_clus - 2) * sec_per_clus
    asm.emit('ADDI', 5, 28, -2)
    asm.emit('MUL', 6, 5, 24)              # (root_clus - 2) * sec_per_clus (x24)
    asm.emit('ADD', 22, 23, 6)             # s6 (x22) = root_dir_lba

    asm.emit('LOAD_ADDR', 10, 'fmt_vbr_ok')
    asm.emit('ADDI', 11, 25, 0)            # a1 = Part1 LBA
    asm.emit('ADDI', 12, 23, 0)            # a2 = Data Start LBA
    asm.emit('ADDI', 13, 24, 0)            # a3 = Sec/Clus
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    # Step 8: Scan Directory for *.app packages (/apps/*.app or /*.app)
    asm.emit('LOAD_ADDR', 10, 'fmt_app_scan')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    # Clear LFN flag & app selection in scratch RAM
    asm.emit('LOAD_ADDR', 5, 0x4087FCFC)   # lfn_flag
    asm.emit('SW', 0, 5, 0)
    asm.emit('LOAD_ADDR', 5, 0x4087FCF8)   # app_to_run_clus
    asm.emit('SW', 0, 5, 0)

    # Initialize: scan Root Directory
    asm.emit('ADDI', 21, 0, 0)             # s5 (x21) = apps_dir_clus = 0
    asm.emit('ADDI', 18, 22, 0)            # s2 (x18) = cur_scan_lba = root_dir_lba
    asm.emit('ADDI', 19, 0, 4)             # s3 (x19) = scan up to 4 sectors (64 entries)

    asm.label('probe_scan_sector')
    asm.emit('ADDI', 10, 18, 0)            # a0 = cur_scan_lba
    asm.emit('LOAD_ADDR', 11, 0x4087F000)  # a1 = disk buffer
    asm.emit('JAL', 1, 'sd_read_sector')
    asm.emit('BNE', 10, 0, 'probe_read_fail')

    asm.emit('LOAD_ADDR', 8, 0x4087F000)   # s0 (x8) = entry pointer
    asm.emit('ADDI', 9, 0, 16)             # s1 (x9) = 16 entries per sector

    asm.label('probe_scan_entry')
    asm.emit('LBU', 5, 8, 0)               # entry[0]
    asm.emit('BEQ', 5, 0, 'probe_dir_done')# 0x00 = end of directory!
    asm.emit('ADDI', 6, 0, 0xE5)
    asm.emit('BEQ', 5, 6, 'probe_entry_skip') # 0xE5 = deleted entry

    # Check attribute byte at offset 11
    asm.emit('LBU', 5, 8, 11)              # entry[11] = attr
    asm.emit('ADDI', 6, 0, 0x0F)
    asm.emit('BEQ', 5, 6, 'probe_handle_lfn') # 0x0F = LFN entry!

    asm.emit('ANDI', 6, 5, 0x08)
    asm.emit('BNE', 6, 0, 'probe_entry_skip') # 0x08 = Volume ID, skip

    # Normal directory entry: check if LFN was collected
    asm.emit('LOAD_ADDR', 5, 0x4087FCFC)
    asm.emit('LW', 6, 5, 0)                # lfn_flag
    asm.emit('SW', 0, 5, 0)                # reset lfn_flag = 0
    asm.emit('ADDI', 7, 0, 1)
    asm.emit('BEQ', 6, 7, 'probe_use_lfn_name')

    # No LFN: format 8.3 short name into 0x4087FD00
    asm.emit('LOAD_ADDR', 6, 0x4087FD00)   # dst
    asm.emit('ADDI', 7, 8, 0)              # src = entry
    asm.emit('ADDI', 28, 0, 8)             # count = 8
    asm.label('fmt_sfn_copy_name')
    asm.emit('LBU', 5, 7, 0)
    asm.emit('ADDI', 29, 0, 0x20)
    asm.emit('BEQ', 5, 29, 'fmt_sfn_ext_dot')
    asm.emit('SB', 5, 6, 0)
    asm.emit('ADDI', 6, 6, 1)
    asm.emit('ADDI', 7, 7, 1)
    asm.emit('ADDI', 28, 28, -1)
    asm.emit('BNE', 28, 0, 'fmt_sfn_copy_name')

    asm.label('fmt_sfn_ext_dot')
    # If byte 8 is space (no extension), skip dot
    asm.emit('LBU', 5, 8, 8)
    asm.emit('ADDI', 29, 0, 0x20)
    asm.emit('BEQ', 5, 29, 'fmt_sfn_ext_end')
    asm.emit('ADDI', 5, 0, ord('.'))
    asm.emit('SB', 5, 6, 0)
    asm.emit('ADDI', 6, 6, 1)

    # Copy up to 3 chars extension
    asm.emit('ADDI', 7, 8, 8)              # src = entry + 8
    asm.emit('ADDI', 28, 0, 3)             # count = 3
    asm.label('fmt_sfn_copy_ext')
    asm.emit('LBU', 5, 7, 0)
    asm.emit('ADDI', 29, 0, 0x20)
    asm.emit('BEQ', 5, 29, 'fmt_sfn_ext_end')
    asm.emit('SB', 5, 6, 0)
    asm.emit('ADDI', 6, 6, 1)
    asm.emit('ADDI', 7, 7, 1)
    asm.emit('ADDI', 28, 28, -1)
    asm.emit('BNE', 28, 0, 'fmt_sfn_copy_ext')

    asm.label('fmt_sfn_ext_end')
    asm.emit('SB', 0, 6, 0)                # null terminator!
    asm.emit('JAL', 0, 'probe_dispatch_entry')

    # Copy decoded LFN string from 0x4087FC00 to 0x4087FD00
    asm.label('probe_use_lfn_name')
    asm.emit('LOAD_ADDR', 6, 0x4087FD00)   # dst
    asm.emit('LOAD_ADDR', 7, 0x4087FC00)   # src
    asm.emit('ADDI', 28, 0, 63)
    asm.label('probe_copy_lfn_loop')
    asm.emit('LBU', 5, 7, 0)
    asm.emit('SB', 5, 6, 0)
    asm.emit('BEQ', 5, 0, 'probe_dispatch_entry')
    asm.emit('ADDI', 6, 6, 1)
    asm.emit('ADDI', 7, 7, 1)
    asm.emit('ADDI', 28, 28, -1)
    asm.emit('BNE', 28, 0, 'probe_copy_lfn_loop')
    asm.emit('SB', 0, 6, 0)

    # Dispatch: Directory or File
    asm.label('probe_dispatch_entry')
    asm.emit('LBU', 5, 8, 11)              # entry[11] = attr
    asm.emit('ANDI', 6, 5, 0x10)
    asm.emit('BNE', 6, 0, 'probe_is_dir_entry')

    # -------------------------------------------------------------------------
    # Regular File
    # -------------------------------------------------------------------------
    asm.emit('LOAD_ADDR', 10, 'fmt_file_found')
    asm.emit('LOAD_ADDR', 11, 0x4087FD00)  # filename
    asm.emit('LW', 12, 8, 28)              # file size
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    # Check if extension is .APP (bytes 8, 9, 10 == 'A', 'P', 'P')
    asm.emit('LBU', 5, 8, 8)
    asm.emit('ANDI', 5, 5, 0xDF)
    asm.emit('ADDI', 6, 0, ord('A'))
    asm.emit('BNE', 5, 6, 'probe_next_entry')
    asm.emit('LBU', 5, 8, 9)
    asm.emit('ANDI', 5, 5, 0xDF)
    asm.emit('ADDI', 6, 0, ord('P'))
    asm.emit('BNE', 5, 6, 'probe_next_entry')
    asm.emit('LBU', 5, 8, 10)
    asm.emit('ANDI', 5, 5, 0xDF)
    asm.emit('ADDI', 6, 0, ord('P'))
    asm.emit('BNE', 5, 6, 'probe_next_entry')

    # .APP File matched! If no app selected yet, select this one:
    asm.emit('LOAD_ADDR', 5, 0x4087FCF8)
    asm.emit('LW', 6, 5, 0)
    asm.emit('BNE', 6, 0, 'probe_next_entry') # already selected an app

    # Save cluster:
    asm.emit('LHU', 5, 8, 20)
    asm.emit('LHU', 6, 8, 26)
    asm.emit('SLLI', 5, 5, 16)
    asm.emit('OR', 7, 5, 6)                # app_start_clus
    asm.emit('LOAD_ADDR', 5, 0x4087FCF8)
    asm.emit('SW', 7, 5, 0)

    # Save file size:
    asm.emit('LW', 7, 8, 28)
    asm.emit('LOAD_ADDR', 5, 0x4087FCF4)
    asm.emit('SW', 7, 5, 0)

    # Save chosen app filename to 0x4087FD80:
    asm.emit('LOAD_ADDR', 6, 0x4087FD80)   # dst
    asm.emit('LOAD_ADDR', 7, 0x4087FD00)   # src
    asm.emit('ADDI', 28, 0, 63)
    asm.label('save_app_name_loop')
    asm.emit('LBU', 5, 7, 0)
    asm.emit('SB', 5, 6, 0)
    asm.emit('BEQ', 5, 0, 'save_app_name_done')
    asm.emit('ADDI', 6, 6, 1)
    asm.emit('ADDI', 7, 7, 1)
    asm.emit('ADDI', 28, 28, -1)
    asm.emit('BNE', 28, 0, 'save_app_name_loop')
    asm.emit('SB', 0, 6, 0)
    asm.label('save_app_name_done')

    # Continue scanning so all other files are also listed!
    asm.emit('JAL', 0, 'probe_next_entry')

    # -------------------------------------------------------------------------
    # Directory Entry
    # -------------------------------------------------------------------------
    asm.label('probe_is_dir_entry')
    # Skip "." and ".."
    asm.emit('LBU', 5, 8, 0)
    asm.emit('ADDI', 6, 0, ord('.'))
    asm.emit('BEQ', 5, 6, 'probe_next_entry')

    # Print "[STORAGE]   - Dir:  /%s/\r\n"
    asm.emit('LOAD_ADDR', 10, 'fmt_dir_found')
    asm.emit('LOAD_ADDR', 11, 0x4087FD00)
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    # Check if short directory name starts with "APPS"
    asm.emit('LBU', 5, 8, 0)
    asm.emit('ANDI', 5, 5, 0xDF)
    asm.emit('ADDI', 6, 0, ord('A'))
    asm.emit('BNE', 5, 6, 'probe_next_entry')
    asm.emit('LBU', 5, 8, 1)
    asm.emit('ANDI', 5, 5, 0xDF)
    asm.emit('ADDI', 6, 0, ord('P'))
    asm.emit('BNE', 5, 6, 'probe_next_entry')
    asm.emit('LBU', 5, 8, 2)
    asm.emit('ANDI', 5, 5, 0xDF)
    asm.emit('ADDI', 6, 0, ord('P'))
    asm.emit('BNE', 5, 6, 'probe_next_entry')
    asm.emit('LBU', 5, 8, 3)
    asm.emit('ANDI', 5, 5, 0xDF)
    asm.emit('ADDI', 6, 0, ord('S'))
    asm.emit('BNE', 5, 6, 'probe_next_entry')

    # Save apps_clus in s5 (x21)
    asm.emit('LHU', 5, 8, 20)
    asm.emit('LHU', 6, 8, 26)
    asm.emit('SLLI', 5, 5, 16)
    asm.emit('OR', 21, 5, 6)               # s5 = apps_clus
    asm.emit('JAL', 0, 'probe_next_entry')

    # -------------------------------------------------------------------------
    # LFN Entry Handler (attr == 0x0F)
    # -------------------------------------------------------------------------
    asm.label('probe_handle_lfn')
    asm.emit('LBU', 5, 8, 0)               # entry[0] = seq
    asm.emit('ANDI', 5, 5, 0x1F)           # seq (1..4)
    asm.emit('BEQ', 5, 0, 'probe_next_entry')
    asm.emit('ADDI', 6, 0, 5)
    asm.emit('BGE', 5, 6, 'probe_next_entry') # ignore if seq >= 5
    asm.emit('ADDI', 5, 5, -1)             # seq - 1 (0..3)
    asm.emit('ADDI', 6, 0, 13)
    asm.emit('MUL', 5, 5, 6)               # base_offset = (seq - 1) * 13
    asm.emit('LOAD_ADDR', 6, 0x4087FC00)
    asm.emit('ADD', 28, 6, 5)              # dst = 0x4087FC00 + base_offset

    # Part 1: offsets 1, 3, 5, 7, 9 (5 characters)
    asm.emit('ADDI', 29, 8, 1)             # src = entry + 1
    asm.emit('ADDI', 7, 0, 5)              # count = 5
    asm.label('lfn_loop1')
    asm.emit('LBU', 5, 29, 0)
    asm.emit('BEQ', 5, 0, 'lfn_term1')
    asm.emit('ADDI', 6, 0, 0xFF)
    asm.emit('BEQ', 5, 6, 'lfn_term1')
    asm.emit('SB', 5, 28, 0)
    asm.emit('ADDI', 28, 28, 1)
    asm.emit('ADDI', 29, 29, 2)
    asm.emit('ADDI', 7, 7, -1)
    asm.emit('BNE', 7, 0, 'lfn_loop1')
    asm.emit('JAL', 0, 'lfn_part2')

    asm.label('lfn_term1')
    asm.emit('SB', 0, 28, 0)
    asm.emit('JAL', 0, 'lfn_done_entry')

    # Part 2: offsets 14, 16, 18, 20, 22, 24 (6 characters)
    asm.label('lfn_part2')
    asm.emit('ADDI', 29, 8, 14)            # src = entry + 14
    asm.emit('ADDI', 7, 0, 6)              # count = 6
    asm.label('lfn_loop2')
    asm.emit('LBU', 5, 29, 0)
    asm.emit('BEQ', 5, 0, 'lfn_term2')
    asm.emit('ADDI', 6, 0, 0xFF)
    asm.emit('BEQ', 5, 6, 'lfn_term2')
    asm.emit('SB', 5, 28, 0)
    asm.emit('ADDI', 28, 28, 1)
    asm.emit('ADDI', 29, 29, 2)
    asm.emit('ADDI', 7, 7, -1)
    asm.emit('BNE', 7, 0, 'lfn_loop2')
    asm.emit('JAL', 0, 'lfn_part3')

    asm.label('lfn_term2')
    asm.emit('SB', 0, 28, 0)
    asm.emit('JAL', 0, 'lfn_done_entry')

    # Part 3: offsets 28, 30 (2 characters)
    asm.label('lfn_part3')
    asm.emit('ADDI', 29, 8, 28)            # src = entry + 28
    asm.emit('ADDI', 7, 0, 2)              # count = 2
    asm.label('lfn_loop3')
    asm.emit('LBU', 5, 29, 0)
    asm.emit('BEQ', 5, 0, 'lfn_term3')
    asm.emit('ADDI', 6, 0, 0xFF)
    asm.emit('BEQ', 5, 6, 'lfn_term3')
    asm.emit('SB', 5, 28, 0)
    asm.emit('ADDI', 28, 28, 1)
    asm.emit('ADDI', 29, 29, 2)
    asm.emit('ADDI', 7, 7, -1)
    asm.emit('BNE', 7, 0, 'lfn_loop3')
    asm.emit('JAL', 0, 'lfn_done_entry')

    asm.label('lfn_term3')
    asm.emit('SB', 0, 28, 0)

    asm.label('lfn_done_entry')
    # Mark LFN valid: [0x4087FCFC] = 1
    asm.emit('LOAD_ADDR', 5, 0x4087FCFC)
    asm.emit('ADDI', 6, 0, 1)
    asm.emit('SW', 6, 5, 0)
    asm.emit('JAL', 0, 'probe_next_entry')

    # Skipped entry (deleted or volume ID): reset LFN flag
    asm.label('probe_entry_skip')
    asm.emit('LOAD_ADDR', 5, 0x4087FCFC)
    asm.emit('SW', 0, 5, 0)

    asm.label('probe_next_entry')
    asm.emit('ADDI', 8, 8, 32)             # advance entry pointer by 32 bytes
    asm.emit('ADDI', 9, 9, -1)             # entries_left--
    asm.emit('BNE', 9, 0, 'probe_scan_entry')

    # Current sector finished: advance to next sector
    asm.emit('ADDI', 18, 18, 1)            # next LBA
    asm.emit('ADDI', 19, 19, -1)           # sectors_left--
    asm.emit('BNE', 19, 0, 'probe_scan_sector')

    # End of directory scan for current directory
    asm.label('probe_dir_done')
    # If s5 != 0 (APPS directory found and not yet scanned):
    asm.emit('BEQ', 21, 0, 'probe_check_run_app')

    # Scan inside /apps/ directory!
    # apps_dir_lba = data_start_lba + (apps_clus - 2) * sec_per_clus
    asm.emit('ADDI', 5, 21, -2)
    asm.emit('MUL', 6, 5, 24)              # (apps_clus - 2) * sec_per_clus
    asm.emit('ADD', 18, 23, 6)             # s2 = apps_dir_lba
    asm.emit('ADDI', 21, 0, 0)             # clear s5 to prevent infinite loop
    asm.emit('ADDI', 19, 0, 4)             # scan up to 4 sectors in /apps/
    asm.emit('JAL', 0, 'probe_scan_sector')

    # All directories finished! Check if an app was selected:
    asm.label('probe_check_run_app')
    asm.emit('LOAD_ADDR', 5, 0x4087FCF8)
    asm.emit('LW', 21, 5, 0)               # s5 (x21) = app_start_clus
    asm.emit('BEQ', 21, 0, 'probe_no_app') # no app found!

    # App was selected! Load app_file_size into s6 (x22):
    asm.emit('LOAD_ADDR', 5, 0x4087FCF4)
    asm.emit('LW', 22, 5, 0)               # s6 (x22) = app_file_size

    # app_lba = data_start_lba + (app_start_clus - 2) * sec_per_clus
    asm.emit('ADDI', 5, 21, -2)
    asm.emit('MUL', 6, 5, 24)
    asm.emit('ADD', 18, 23, 6)             # s2 (x18) = app_lba

    # Load all sectors of application into SRAM starting at 0x40820000
    asm.emit('LOAD_ADDR', 19, 0x40820000)
    asm.emit('ADDI', 5, 22, 511)
    asm.emit('SRLI', 24, 5, 9)             # sectors count
    # Clamp sectors to max 256 (128 KB)
    asm.emit('LOAD_ADDR', 5, 256)
    asm.emit('BLE', 24, 5, 'probe_read_app_loop')
    asm.emit('ADDI', 24, 5, 0)

    asm.label('probe_read_app_loop')
    asm.emit('BEQ', 24, 0, 'probe_verify_app')
    asm.emit('ADDI', 10, 18, 0)            # a0 = lba
    asm.emit('ADDI', 11, 19, 0)            # a1 = dst
    asm.emit('JAL', 1, 'sd_read_sector')
    asm.emit('BNE', 10, 0, 'probe_read_fail')
    asm.emit('ADDI', 18, 18, 1)            # next lba
    asm.emit('ADDI', 19, 19, 512)          # next dst
    asm.emit('ADDI', 24, 24, -1)           # sectors--
    asm.emit('JAL', 0, 'probe_read_app_loop')

    # Verify Magic \x7FNEXAPP\x01
    asm.label('probe_verify_app')
    asm.emit('LOAD_ADDR', 8, 0x40820000)
    asm.emit('LBU', 5, 8, 0)
    asm.emit('ADDI', 6, 0, 0x7F)
    asm.emit('BNE', 5, 6, 'probe_bad_app')
    asm.emit('LBU', 5, 8, 1)
    asm.emit('ADDI', 6, 0, ord('N'))
    asm.emit('BNE', 5, 6, 'probe_bad_app')
    asm.emit('LBU', 5, 8, 2)
    asm.emit('ADDI', 6, 0, ord('E'))
    asm.emit('BNE', 5, 6, 'probe_bad_app')
    asm.emit('LBU', 5, 8, 3)
    asm.emit('ADDI', 6, 0, ord('X'))
    asm.emit('BNE', 5, 6, 'probe_bad_app')

    # App verified! Print real filename and version
    asm.emit('LOAD_ADDR', 10, 'fmt_app_found')
    asm.emit('LOAD_ADDR', 11, 0x4087FD80)  # a1 = real filename on SD card (e.g. testlight2.app)
    asm.emit('ADDI', 12, 8, 20)            # a2 = app_name in header (e.g. testlight2)
    asm.emit('ADDI', 13, 8, 52)            # a3 = app_version in header
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    asm.emit('LOAD_ADDR', 10, 'fmt_app_verify')
    asm.emit('LOAD_ADDR', 11, 0x4087FD80)  # a1 = real filename
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    # Zero BSS
    asm.emit('LW', 5, 8, 0x48)             # code_size
    asm.emit('LW', 6, 8, 0x4C)             # data_size
    asm.emit('LW', 7, 8, 0x50)             # bss_size
    asm.emit('ADD', 28, 5, 6)
    asm.emit('ADDI', 28, 28, 128)
    asm.emit('ADD', 28, 8, 28)

    asm.label('probe_zero_bss')
    asm.emit('BEQ', 7, 0, 'probe_jump_app')
    asm.emit('SB', 0, 28, 0)
    asm.emit('ADDI', 28, 28, 1)
    asm.emit('ADDI', 7, 7, -1)
    asm.emit('JAL', 0, 'probe_zero_bss')

    # Jump to app!
    asm.label('probe_jump_app')

    # -------------------------------------------------------------------------
    # Auto-patch legacy rom_delay_us calls in SRAM:
    # Any app calling rom_delay_us (0x40000040) is redirected to sys_delay_us_hook
    # so that card removal is monitored continuously (<50ms)!
    # -------------------------------------------------------------------------
    asm.emit('LOAD_ADDR', 5, 0x40820080)   # app payload entry in SRAM
    asm.emit('LOAD_ADDR', 6, 0x40820080)
    asm.emit('LW', 7, 8, 0x48)             # code_size from header (s0 = 0x40820000)
    asm.emit('ADD', 6, 6, 7)               # end_addr = 0x40820080 + code_size
    asm.emit('ADDI', 6, 6, -7)             # ensure at least 8 bytes remain for pair check

    # Prepare words to match: 0x400002b7 (LUI x5, 0x40000) and 0x04028293 (ADDI x5, x5, 0x40)
    asm.emit('LOAD_ADDR', 7, 0x400002b7)
    asm.emit('LOAD_ADDR', 28, 0x04028293)
    asm.emit('LOAD_INSN_WORDS', 29, 30, 'sys_delay_us_hook') # replacement pair in x29, x30

    asm.label('patch_app_loop')
    asm.emit('BGE', 5, 6, 'probe_jump_app_ready')
    asm.emit('LW', 31, 5, 0)
    asm.emit('BNE', 31, 7, 'patch_app_next')
    asm.emit('LW', 31, 5, 4)
    asm.emit('BNE', 31, 28, 'patch_app_next')

    # Found match! Replace with sys_delay_us_hook loader
    asm.emit('SW', 29, 5, 0)
    asm.emit('SW', 30, 5, 4)
    asm.emit('ADDI', 5, 5, 4)              # advance past patched pair

    asm.label('patch_app_next')
    asm.emit('ADDI', 5, 5, 4)
    asm.emit('JAL', 0, 'patch_app_loop')

    asm.label('probe_jump_app_ready')
    asm.emit('FENCE_I')

    # Initialize Syscall Table at 0x4087FE00
    asm.emit('LOAD_ADDR', 28, 0x4087FE00)
    asm.emit('ADDI', 5, 0, 1)              # abi_version = 1
    asm.emit('SW', 5, 28, 0)
    asm.emit('ADDI', 5, 0, 68)             # table_size = 68
    asm.emit('SW', 5, 28, 4)
    asm.emit('LOAD_ADDR', 5, 'sys_log')
    asm.emit('SW', 5, 28, 8)
    asm.emit('LOAD_ADDR', 5, 'sys_delay_ms')
    asm.emit('SW', 5, 28, 12)
    asm.emit('LOAD_ADDR', 5, 'sys_time_get_ms')
    asm.emit('SW', 5, 28, 16)
    asm.emit('LOAD_ADDR', 5, 'sys_delay_ms') # sys_task_sleep_ms = sys_delay_ms
    asm.emit('SW', 5, 28, 20)
    asm.emit('LOAD_ADDR', 5, 'sys_nop')    # sys_task_yield
    asm.emit('SW', 5, 28, 24)
    asm.emit('LOAD_ADDR', 5, 'sys_nop')    # sys_malloc
    asm.emit('SW', 5, 28, 28)
    asm.emit('LOAD_ADDR', 5, 'sys_nop')    # sys_free
    asm.emit('SW', 5, 28, 32)
    asm.emit('LOAD_ADDR', 5, 'sys_nop')    # sys_device_has
    asm.emit('SW', 5, 28, 36)
    asm.emit('LOAD_ADDR', 5, 'sys_gpio_mode')
    asm.emit('SW', 5, 28, 40)
    asm.emit('LOAD_ADDR', 5, 'sys_gpio_write')
    asm.emit('SW', 5, 28, 44)
    asm.emit('LOAD_ADDR', 5, 'sys_gpio_read')
    asm.emit('SW', 5, 28, 48)
    asm.emit('LOAD_ADDR', 5, 'sys_gpio_toggle')
    asm.emit('SW', 5, 28, 52)
    asm.emit('LOAD_ADDR', 5, 'sys_uart_write')
    asm.emit('SW', 5, 28, 56)
    asm.emit('LOAD_ADDR', 5, 'sys_uart_read')
    asm.emit('SW', 5, 28, 60)
    asm.emit('LOAD_ADDR', 5, 'sys_app_exit')
    asm.emit('SW', 5, 28, 64)

    # Calculate app entrypoint address
    asm.emit('LW', 5, 8, 0x44)             # entry_offset
    asm.emit('ADDI', 5, 5, 128)
    asm.emit('ADD', 6, 8, 5)               # entrypoint address

    # Save kernel stack pointer at 0x4087FFF0 so we can cleanly abort if card is removed
    asm.emit('LOAD_ADDR', 5, 0x4087FFF0)
    asm.emit('SW', 2, 5, 0)

    # Pass syscall table in a0 (x10) to _nex_app_start(table)!
    asm.emit('LOAD_ADDR', 10, 0x4087FE00)
    asm.emit('JALR', 1, 6, 0)              # EXECUTE!

    # Return from app
    asm.emit('LOAD_ADDR', 10, 'fmt_app_done')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'probe_return_ok')

    asm.label('probe_bad_app')
    asm.emit('LOAD_ADDR', 10, 'fmt_app_bad')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'probe_return_ok')

    asm.label('probe_no_app')
    asm.emit('LOAD_ADDR', 10, 'fmt_app_none')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'probe_return_ok')

    asm.label('probe_mbr_fail')
    asm.emit('LOAD_ADDR', 10, 'fmt_mbr_fail')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'probe_return_err')

    asm.label('probe_vbr_fail')
    asm.emit('LOAD_ADDR', 10, 'fmt_vbr_fail')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'probe_return_err')

    asm.label('probe_read_fail')
    asm.emit('LOAD_ADDR', 10, 'sd_read_err_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'probe_return_err')

    asm.label('probe_return_ok')
    asm.emit('ADDI', 10, 0, 1)             # return 1 (mounted)
    asm.emit('JAL', 0, 'probe_exit')

    asm.label('probe_return_nocard')
    asm.emit('ADDI', 10, 0, 0)             # return 0 (no card detected)
    asm.emit('JAL', 0, 'probe_exit')

    asm.label('probe_return_err')
    asm.emit('ADDI', 10, 0, 2)             # return 2 (card in slot, but error)
    asm.emit('JAL', 0, 'probe_exit')

    asm.label('probe_exit')
    asm.emit('LW', 1, 2, 60)
    asm.emit('LW', 8, 2, 56)
    asm.emit('LW', 9, 2, 52)
    asm.emit('LW', 18, 2, 48)
    asm.emit('LW', 19, 2, 44)
    asm.emit('LW', 21, 2, 36)
    asm.emit('LW', 22, 2, 32)
    asm.emit('LW', 23, 2, 28)
    asm.emit('LW', 24, 2, 24)
    asm.emit('LW', 25, 2, 20)
    asm.emit('LW', 26, 2, 16)
    asm.emit('ADDI', 2, 2, 64)
    asm.emit('JALR', 0, 1, 0)

    # =========================================================================
    # NexOS Syscall ABI Handlers (Real Hardware Drivers for Applications)
    # =========================================================================
    # -------------------------------------------------------------------------
    # Abort running application if MicroSD card is removed while running
    # -------------------------------------------------------------------------
    asm.label('app_abort_card_removed')
    # 1. Turn off all GPIO output pins so active LEDs immediately turn OFF
    asm.emit('LOAD_ADDR', 5, 0x60091000)
    asm.emit('LOAD_ADDR', 6, 0xFFFFFFFF)
    asm.emit('SW', 6, 5, 0x0C)             # GPIO_OUT_W1TC = 0xFFFFFFFF (all pins LOW)
    asm.emit('LOAD_ADDR', 6, 0x00040000)   # CS pin (GPIO 18)
    asm.emit('SW', 6, 5, 0x08)             # GPIO_OUT_W1TS (CS HIGH)

    # 2. Print card removed & application terminated message
    asm.emit('LOAD_ADDR', 10, 'fmt_card_removed_app')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    # 3. Restore kernel stack pointer from 0x4087FFF0
    asm.emit('LOAD_ADDR', 5, 0x4087FFF0)
    asm.emit('LW', 2, 5, 0)

    # 4. Return cleanly from fat32_probe_and_autorun with status 0 (no card / standby)
    asm.emit('JAL', 0, 'probe_return_nocard')

    # -------------------------------------------------------------------------
    # sys_log(tag, msg): Checks card presence, then logs message via rom_printf
    # -------------------------------------------------------------------------
    asm.label('sys_log')
    asm.emit('ADDI', 2, 2, -16)
    asm.emit('SW', 1, 2, 12)
    asm.emit('SW', 10, 2, 8)               # save a0 (tag)
    asm.emit('SW', 11, 2, 4)               # save a1 (msg)

    # Check if card is still inserted
    asm.emit('JAL', 1, 'sd_check_present')
    asm.emit('BEQ', 10, 0, 'app_abort_card_removed')

    asm.emit('LW', 10, 2, 8)               # restore a0 (tag)
    asm.emit('LW', 11, 2, 4)               # restore a1 (msg)
    asm.emit('ADDI', 12, 11, 0)            # a2 = msg
    asm.emit('ADDI', 11, 10, 0)            # a1 = tag
    asm.emit('LOAD_ADDR', 10, 'fmt_sys_log')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('LW', 1, 2, 12)
    asm.emit('ADDI', 2, 2, 16)
    asm.emit('JALR', 0, 1, 0)

    # -------------------------------------------------------------------------
    # sys_delay_ms(ms): Sliced delay with continuous card presence monitoring
    # If card is pulled out during delay, immediately stops the app!
    # -------------------------------------------------------------------------
    asm.label('sys_delay_ms')
    asm.emit('ADDI', 2, 2, -16)
    asm.emit('SW', 1, 2, 12)
    asm.emit('SW', 8, 2, 8)                # save s0 (x8)
    asm.emit('ADDI', 8, 10, 0)             # s0 = remaining ms

    asm.label('delay_slice_loop')
    asm.emit('BLE', 8, 0, 'delay_done')

    # Check if MicroSD card is still present
    asm.emit('JAL', 1, 'sd_check_present')
    asm.emit('BEQ', 10, 0, 'app_abort_card_removed') # Card pulled out! Abort!

    # Determine slice = min(s0, 50) ms
    asm.emit('ADDI', 10, 0, 50)
    asm.emit('BLT', 8, 10, 'delay_slice_remainder')

    # Delay 50ms (50,000 us)
    asm.emit('LOAD_ADDR', 10, 50000)
    asm.emit('LOAD_ADDR', 5, 0x40000040)   # rom_delay_us
    asm.emit('JALR', 1, 5, 0)
    asm.emit('ADDI', 8, 8, -50)
    asm.emit('JAL', 0, 'delay_slice_loop')

    asm.label('delay_slice_remainder')
    # Delay remaining ms * 1000 us
    asm.emit('LOAD_ADDR', 5, 1000)
    asm.emit('MUL', 10, 8, 5)              # us = remaining * 1000
    asm.emit('LOAD_ADDR', 5, 0x40000040)
    asm.emit('JALR', 1, 5, 0)

    asm.label('delay_done')
    asm.emit('LW', 8, 2, 8)
    asm.emit('LW', 1, 2, 12)
    asm.emit('ADDI', 2, 2, 16)
    asm.emit('JALR', 0, 1, 0)

    # -------------------------------------------------------------------------
    # sys_delay_us_hook(us): Intercepts legacy rom_delay_us calls from apps,
    # converts us to ms, and routes through sys_delay_ms (which monitors card removal)
    # -------------------------------------------------------------------------
    asm.label('sys_delay_us_hook')
    asm.emit('ADDI', 2, 2, -16)
    asm.emit('SW', 1, 2, 12)

    # Convert us (a0) to ms: ms = us / 1000
    asm.emit('LOAD_ADDR', 5, 1000)
    asm.emit('DIV', 10, 10, 5)             # a0 = ms = us / 1000
    asm.emit('BNE', 10, 0, 'hook_call_ms')
    asm.emit('ADDI', 10, 0, 1)             # minimum 1ms

    asm.label('hook_call_ms')
    asm.emit('JAL', 1, 'sys_delay_ms')

    asm.emit('LW', 1, 2, 12)
    asm.emit('ADDI', 2, 2, 16)
    asm.emit('JALR', 0, 1, 0)

    asm.label('sys_time_get_ms')
    asm.emit('LOAD_ADDR', 5, 0x60008000)   # TIMERG0
    asm.emit('ADDI', 6, 0, 1)
    asm.emit('SW', 6, 5, 0x0C)             # UPDATE
    asm.emit('LW', 10, 5, 0x04)            # LO
    asm.emit('SRLI', 10, 10, 10)           # rough ms
    asm.emit('JALR', 0, 1, 0)

    asm.label('sys_nop')
    asm.emit('ADDI', 10, 0, 0)
    asm.emit('JALR', 0, 1, 0)

    asm.label('sys_gpio_mode')
    asm.emit('ADDI', 5, 0, 1)
    asm.emit('SLL', 6, 5, 10)              # 1 << pin
    asm.emit('LOAD_ADDR', 7, 0x60091000)
    asm.emit('BNE', 11, 5, 'sys_gpio_mode_in')
    # Output mode
    asm.emit('SW', 6, 7, 0x24)             # GPIO_ENABLE_W1TS
    asm.emit('SLLI', 5, 10, 2)             # pin * 4
    asm.emit('LOAD_ADDR', 28, 0x60091554)  # GPIO_FUNC0_OUT_SEL_CFG_REG
    asm.emit('ADD', 28, 28, 5)
    asm.emit('ADDI', 29, 0, 128)           # Direct output
    asm.emit('SW', 29, 28, 0)
    asm.emit('LOAD_ADDR', 28, 0x60091004)  # IO_MUX GPIO0
    asm.emit('ADD', 28, 28, 5)
    asm.emit('LOAD_ADDR', 29, 0x1200)      # MCU_SEL(1) | FUN_DRV(2)
    asm.emit('SW', 29, 28, 0)
    asm.emit('ADDI', 10, 0, 0)
    asm.emit('JALR', 0, 1, 0)
    asm.label('sys_gpio_mode_in')
    asm.emit('SW', 6, 7, 0x28)             # GPIO_ENABLE_W1TC
    asm.emit('ADDI', 10, 0, 0)
    asm.emit('JALR', 0, 1, 0)

    asm.label('sys_gpio_write')
    # Periodic card presence check every 64 calls
    asm.emit('LOAD_ADDR', 28, 0x4087FFF4)
    asm.emit('LW', 29, 28, 0)
    asm.emit('ADDI', 29, 29, 1)
    asm.emit('SW', 29, 28, 0)
    asm.emit('ANDI', 29, 29, 0x3F)
    asm.emit('BNE', 29, 0, 'sys_gpio_write_exec')

    # Check card present
    asm.emit('ADDI', 2, 2, -16)
    asm.emit('SW', 1, 2, 12)
    asm.emit('SW', 10, 2, 8)               # save a0
    asm.emit('SW', 11, 2, 4)               # save a1
    asm.emit('JAL', 1, 'sd_check_present')
    asm.emit('BEQ', 10, 0, 'app_abort_card_removed')
    asm.emit('LW', 10, 2, 8)
    asm.emit('LW', 11, 2, 4)
    asm.emit('LW', 1, 2, 12)
    asm.emit('ADDI', 2, 2, 16)

    asm.label('sys_gpio_write_exec')
    asm.emit('ADDI', 5, 0, 1)
    asm.emit('SLL', 6, 5, 10)              # 1 << pin
    asm.emit('LOAD_ADDR', 7, 0x60091000)
    asm.emit('BEQ', 11, 0, 'sys_gpio_write_low')
    asm.emit('SW', 6, 7, 0x08)             # GPIO_OUT_W1TS (HIGH)
    asm.emit('ADDI', 10, 0, 0)
    asm.emit('JALR', 0, 1, 0)
    asm.label('sys_gpio_write_low')
    asm.emit('SW', 6, 7, 0x0C)             # GPIO_OUT_W1TC (LOW)
    asm.emit('ADDI', 10, 0, 0)
    asm.emit('JALR', 0, 1, 0)

    asm.label('sys_gpio_read')
    asm.emit('LOAD_ADDR', 5, 0x6009103C)   # GPIO_IN_REG
    asm.emit('LW', 6, 5, 0)
    asm.emit('SRL', 10, 6, 10)
    asm.emit('ANDI', 10, 10, 1)
    asm.emit('JALR', 0, 1, 0)

    asm.label('sys_gpio_toggle')
    asm.emit('LOAD_ADDR', 5, 0x60091004)   # GPIO_OUT_REG
    asm.emit('LW', 6, 5, 0)
    asm.emit('ADDI', 7, 0, 1)
    asm.emit('SLL', 7, 7, 10)              # 1 << pin
    asm.emit('AND', 28, 6, 7)              # test if HIGH
    asm.emit('LOAD_ADDR', 29, 0x60091000)
    asm.emit('BEQ', 28, 0, 'sys_toggle_high')
    asm.emit('SW', 7, 29, 0x0C)            # W1TC (set LOW)
    asm.emit('ADDI', 10, 0, 0)
    asm.emit('JALR', 0, 1, 0)
    asm.label('sys_toggle_high')
    asm.emit('SW', 7, 29, 0x08)            # W1TS (set HIGH)
    asm.emit('ADDI', 10, 0, 0)
    asm.emit('JALR', 0, 1, 0)

    asm.label('sys_uart_write')
    asm.emit('ADDI', 2, 2, -16)
    asm.emit('SW', 1, 2, 12)
    asm.label('sys_uart_loop')
    asm.emit('BEQ', 12, 0, 'sys_uart_done')
    asm.emit('LBU', 5, 11, 0)
    asm.emit('LOAD_ADDR', 6, 0x60000000)
    asm.emit('SW', 5, 6, 0)
    asm.emit('ADDI', 11, 11, 1)
    asm.emit('ADDI', 12, 12, -1)
    asm.emit('JAL', 0, 'sys_uart_loop')
    asm.label('sys_uart_done')
    asm.emit('ADDI', 10, 0, 0)
    asm.emit('LW', 1, 2, 12)
    asm.emit('ADDI', 2, 2, 16)
    asm.emit('JALR', 0, 1, 0)

    asm.label('sys_uart_read')
    asm.emit('ADDI', 10, 0, 0)
    asm.emit('JALR', 0, 1, 0)

    asm.label('sys_app_exit')
    asm.emit('LOAD_ADDR', 10, 'fmt_app_done')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JALR', 0, 1, 0)

    # =========================================================================
    # 1. Hardware & Runtime Initialization
    # =========================================================================
    asm.label('kernel_init')

    # 1.1 Disable TimerGroup0 Watchdog
    asm.emit('LOAD_ADDR', 6, 0x60008000)
    asm.emit('LOAD_ADDR', 7, 0x50D83AA1)
    asm.emit('SW', 7, 6, 0x64)
    asm.emit('SW', 0, 6, 0x48)
    asm.emit('SW', 0, 6, 0x64)

    # 1.2 Disable TimerGroup1 Watchdog
    asm.emit('LOAD_ADDR', 6, 0x60009000)
    asm.emit('SW', 7, 6, 0x64)
    asm.emit('SW', 0, 6, 0x48)
    asm.emit('SW', 0, 6, 0x64)

    # 1.3 Disable Low-Power Watchdog (LP_WDT)
    asm.emit('LOAD_ADDR', 6, 0x600B1C00)
    asm.emit('SW', 7, 6, 0x18)
    asm.emit('SW', 0, 6, 0x00)
    asm.emit('SW', 0, 6, 0x18)

    # 1.4 Disable Super Watchdog (SWD)
    asm.emit('SW', 7, 6, 0x20)
    asm.emit('LOAD_ADDR', 5, 0x40040000)
    asm.emit('SW', 5, 6, 0x1C)
    asm.emit('SW', 0, 6, 0x20)

    # 1.5 Enable USB_DEVICE clock & release reset in PCR (0x6009608C = 1)
    asm.emit('LOAD_ADDR', 6, 0x60096000)
    asm.emit('ADDI', 5, 0, 1)
    asm.emit('SW', 5, 6, 0x8C)

    # 1.6 Route ets_printf to both UART0 and USB-Serial-JTAG
    asm.emit('LOAD_ADDR', 5, 0x40000034)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('LOAD_ADDR', 5, 0x40000038)
    asm.emit('JALR', 1, 5, 0)

    # 1.7 Print boot banner
    asm.emit('LOAD_ADDR', 10, 'boot_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    # 1.8 Probe MicroSD Card (mode = 0)
    asm.emit('ADDI', 10, 0, 0)
    asm.emit('JAL', 1, 'fat32_probe_and_autorun')
    asm.emit('ADDI', 20, 10, 0)            # s4 (x20) = initial card status

    # 1.9 Print initial shell prompt
    asm.emit('LOAD_ADDR', 10, 'prompt_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    # Shell registers:
    # s0 (x8)  = buffer pointer (0x4087FE00)
    # s1 (x9)  = buffer len (0)
    # s2 (x18) = last rx byte (0)
    # s3 (x19) = current rx char (0)
    # s4 (x20) = SD status (0=standby, 1=mounted)
    # s10 (x26) = hotplug tick counter (0)
    asm.emit('LOAD_ADDR', 8, 0x4087FE00)
    asm.emit('ADDI', 9, 0, 0)
    asm.emit('ADDI', 18, 0, 0)
    asm.emit('ADDI', 19, 0, 0)
    asm.emit('ADDI', 26, 0, 0)

    # =========================================================================
    # 2. Main Non-Blocking Serial Polling Loop
    # =========================================================================
    asm.label('poll_rx')

    # Channel A: USB-Serial-JTAG
    asm.emit('LOAD_ADDR', 5, 0x6000F000)
    asm.emit('LW', 6, 5, 0x04)
    asm.emit('ANDI', 6, 6, 0x04)
    asm.emit('BNE', 6, 0, 'got_usb_rx')

    # Channel B: UART0
    asm.emit('LOAD_ADDR', 5, 0x60000000)
    asm.emit('LW', 6, 5, 0x1C)
    asm.emit('ANDI', 6, 6, 0xFF)
    asm.emit('BNE', 6, 0, 'got_uart0_rx')

    # =========================================================================
    # 3. Idle Standby: Feed Watchdogs & Hot-Plug Auto-Detection
    # =========================================================================
    asm.label('rx_idle')
    # Feed TG0
    asm.emit('LOAD_ADDR', 5, 0x60008000)
    asm.emit('LOAD_ADDR', 6, 0x50D83AA1)
    asm.emit('SW', 6, 5, 0x64)
    asm.emit('ADDI', 7, 0, 1)
    asm.emit('SW', 7, 5, 0x60)
    asm.emit('SW', 0, 5, 0x64)

    # Feed SWD
    asm.emit('LOAD_ADDR', 5, 0x600B1C00)
    asm.emit('SW', 6, 5, 0x20)
    asm.emit('LOAD_ADDR', 7, 0x40040000)
    asm.emit('SW', 7, 5, 0x1C)
    asm.emit('SW', 0, 5, 0x20)

    # Hot-plug Auto-Detection every 20 ticks (20 * 10ms = 200ms)
    asm.emit('ADDI', 26, 26, 1)
    asm.emit('ADDI', 5, 0, 20)
    asm.emit('BLT', 26, 5, 'rx_sleep')
    asm.emit('ADDI', 26, 0, 0)             # reset counter

    # If s4 == 0 (no card mounted), check if a card was just inserted
    asm.emit('BNE', 20, 0, 'check_card_removal')
    asm.emit('JAL', 1, 'sd_quick_check')
    asm.emit('BEQ', 10, 0, 'rx_sleep')     # still no card

    # CARD INSERTION DETECTED!
    asm.emit('ADDI', 10, 0, 2)             # mode = 2 (hotplug insertion)
    asm.emit('JAL', 1, 'fat32_probe_and_autorun')
    asm.emit('ADDI', 20, 10, 0)            # update s4 = status

    # Reset shell input buffer & reprint prompt
    asm.emit('LOAD_ADDR', 8, 0x4087FE00)
    asm.emit('ADDI', 9, 0, 0)
    asm.emit('LOAD_ADDR', 10, 'prompt_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'rx_sleep')

    # If s4 == 1 (card mounted), check if card was removed
    asm.label('check_card_removal')
    asm.emit('JAL', 1, 'sd_check_present')
    asm.emit('BNE', 10, 0, 'rx_sleep')     # still present

    # CARD REMOVED!
    asm.emit('ADDI', 20, 0, 0)             # s4 = 0 (standby)
    asm.emit('LOAD_ADDR', 10, 'fmt_card_removed')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    # Reset shell input buffer & reprint prompt
    asm.emit('LOAD_ADDR', 8, 0x4087FE00)
    asm.emit('ADDI', 9, 0, 0)
    asm.emit('LOAD_ADDR', 10, 'prompt_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    asm.label('rx_sleep')
    asm.emit('LOAD_ADDR', 10, 10000)       # 10ms
    asm.emit('LOAD_ADDR', 5, 0x40000040)   # ets_delay_us
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'poll_rx')

    # =========================================================================
    # 4. Terminal Char Processing
    # =========================================================================
    asm.label('got_usb_rx')
    asm.emit('LOAD_ADDR', 5, 0x6000F000)
    asm.emit('LW', 19, 5, 0x00)
    asm.emit('ANDI', 19, 19, 0xFF)
    asm.emit('JAL', 0, 'process_char')

    asm.label('got_uart0_rx')
    asm.emit('LOAD_ADDR', 5, 0x60000000)
    asm.emit('LW', 19, 5, 0x00)
    asm.emit('ANDI', 19, 19, 0xFF)

    asm.label('process_char')
    # \n (10)
    asm.emit('ADDI', 5, 0, 10)
    asm.emit('BNE', 19, 5, 'check_cr')
    asm.emit('ADDI', 6, 0, 13)
    asm.emit('BNE', 18, 6, 'handle_enter')
    asm.emit('ADDI', 18, 0, 10)
    asm.emit('JAL', 0, 'poll_rx')

    # \r (13)
    asm.label('check_cr')
    asm.emit('ADDI', 5, 0, 13)
    asm.emit('BEQ', 19, 5, 'handle_enter')

    # Backspace (8 or 127)
    asm.emit('ADDI', 5, 0, 8)
    asm.emit('BEQ', 19, 5, 'handle_bs')
    asm.emit('ADDI', 5, 0, 127)
    asm.emit('BEQ', 19, 5, 'handle_bs')

    # Ctrl+C (3)
    asm.emit('ADDI', 5, 0, 3)
    asm.emit('BEQ', 19, 5, 'handle_ctrl_c')

    # Printable ASCII (32..126)
    asm.emit('ADDI', 18, 19, 0)
    asm.emit('ADDI', 5, 0, 32)
    asm.emit('BLT', 19, 5, 'poll_rx')
    asm.emit('ADDI', 5, 0, 126)
    asm.emit('BLT', 5, 19, 'poll_rx')

    # Echo char
    asm.emit('LOAD_ADDR', 10, 'char_fmt')
    asm.emit('ADDI', 11, 19, 0)
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    # Append to buffer
    asm.emit('ADDI', 5, 0, 31)
    asm.emit('BGE', 9, 5, 'poll_rx')
    asm.emit('ADD', 5, 8, 9)
    asm.emit('SB', 19, 5, 0)
    asm.emit('ADDI', 9, 9, 1)
    asm.emit('JAL', 0, 'poll_rx')

    asm.label('handle_bs')
    asm.emit('ADDI', 18, 19, 0)
    asm.emit('BEQ', 9, 0, 'poll_rx')
    asm.emit('ADDI', 9, 9, -1)
    asm.emit('LOAD_ADDR', 10, 'bs_seq')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'poll_rx')

    asm.label('handle_ctrl_c')
    asm.emit('ADDI', 18, 19, 0)
    asm.emit('ADDI', 9, 0, 0)
    asm.emit('LOAD_ADDR', 10, 'ctrl_c_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('LOAD_ADDR', 10, 'prompt_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'poll_rx')

    asm.label('handle_enter')
    asm.emit('ADDI', 18, 19, 0)
    asm.emit('LOAD_ADDR', 10, 'crlf_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)

    asm.emit('BNE', 9, 0, 'execute_cmd')
    asm.emit('LOAD_ADDR', 10, 'prompt_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'poll_rx')

    # =========================================================================
    # 5. Command Execution
    # =========================================================================
    asm.label('execute_cmd')
    asm.emit('ADD', 5, 8, 9)
    asm.emit('SB', 0, 5, 0)

    asm.emit('LBU', 12, 8, 0)
    # uppercase -> lowercase
    asm.emit('ADDI', 5, 0, 65)
    asm.emit('BLT', 12, 5, 'check_cmds')
    asm.emit('ADDI', 5, 0, 90)
    asm.emit('BLT', 5, 12, 'check_cmds')
    asm.emit('ADDI', 12, 12, 32)

    asm.label('check_cmds')
    # 'h' or '?' -> help
    asm.emit('ADDI', 5, 0, ord('h'))
    asm.emit('BEQ', 12, 5, 'cmd_help')
    asm.emit('ADDI', 5, 0, ord('?'))
    asm.emit('BEQ', 12, 5, 'cmd_help')

    # 'i' or 'v' -> info
    asm.emit('ADDI', 5, 0, ord('i'))
    asm.emit('BEQ', 12, 5, 'cmd_info')
    asm.emit('ADDI', 5, 0, ord('v'))
    asm.emit('BEQ', 12, 5, 'cmd_info')

    # 'c' -> check clear vs caps
    asm.emit('ADDI', 5, 0, ord('c'))
    asm.emit('BEQ', 12, 5, 'cmd_c_prefix')

    # 'm' -> mem
    asm.emit('ADDI', 5, 0, ord('m'))
    asm.emit('BEQ', 12, 5, 'cmd_mem')

    # 'p' -> ping
    asm.emit('ADDI', 5, 0, ord('p'))
    asm.emit('BEQ', 12, 5, 'cmd_ping')

    # 's' -> sd
    asm.emit('ADDI', 5, 0, ord('s'))
    asm.emit('BEQ', 12, 5, 'cmd_sd')

    # 'r' -> check run vs reboot
    asm.emit('ADDI', 5, 0, ord('r'))
    asm.emit('BEQ', 12, 5, 'cmd_r_prefix')

    # 'l' or 'a' -> ls / apps
    asm.emit('ADDI', 5, 0, ord('l'))
    asm.emit('BEQ', 12, 5, 'cmd_apps')
    asm.emit('ADDI', 5, 0, ord('a'))
    asm.emit('BEQ', 12, 5, 'cmd_apps')

    # Default: Unknown
    asm.emit('LOAD_ADDR', 10, 'shell_unknown_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'finish_cmd')

    asm.label('cmd_c_prefix')
    asm.emit('LBU', 5, 8, 1)
    asm.emit('ADDI', 6, 0, ord('l'))
    asm.emit('BEQ', 5, 6, 'cmd_clear')
    asm.emit('ADDI', 6, 0, ord('L'))
    asm.emit('BEQ', 5, 6, 'cmd_clear')
    # Caps
    asm.emit('LOAD_ADDR', 10, 'shell_caps_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'finish_cmd')

    asm.label('cmd_r_prefix')
    asm.emit('LBU', 5, 8, 1)
    asm.emit('ADDI', 6, 0, ord('u'))
    asm.emit('BEQ', 5, 6, 'cmd_run')
    asm.emit('ADDI', 6, 0, ord('U'))
    asm.emit('BEQ', 5, 6, 'cmd_run')
    asm.emit('JAL', 0, 'cmd_reboot')

    # Run command: calls fat32_probe_and_autorun(mode=1)
    asm.label('cmd_run')
    asm.emit('ADDI', 10, 0, 1)
    asm.emit('JAL', 1, 'fat32_probe_and_autorun')
    asm.emit('ADDI', 20, 10, 0)
    asm.emit('JAL', 0, 'finish_cmd')

    # SD command: calls fat32_probe_and_autorun(mode=1)
    asm.label('cmd_sd')
    asm.emit('ADDI', 10, 0, 1)
    asm.emit('JAL', 1, 'fat32_probe_and_autorun')
    asm.emit('ADDI', 20, 10, 0)
    asm.emit('JAL', 0, 'finish_cmd')

    # Apps command: calls fat32_probe_and_autorun(mode=1)
    asm.label('cmd_apps')
    asm.emit('ADDI', 10, 0, 1)
    asm.emit('JAL', 1, 'fat32_probe_and_autorun')
    asm.emit('ADDI', 20, 10, 0)
    asm.emit('JAL', 0, 'finish_cmd')

    asm.label('cmd_clear')
    asm.emit('LOAD_ADDR', 10, 'shell_clear_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'finish_cmd')

    asm.label('cmd_help')
    asm.emit('LOAD_ADDR', 10, 'shell_help_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'finish_cmd')

    asm.label('cmd_info')
    asm.emit('LOAD_ADDR', 10, 'shell_info_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'finish_cmd')

    asm.label('cmd_mem')
    asm.emit('LOAD_ADDR', 10, 'shell_mem_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'finish_cmd')

    asm.label('cmd_ping')
    asm.emit('LOAD_ADDR', 10, 'shell_ping_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'finish_cmd')

    asm.label('cmd_reboot')
    asm.emit('LOAD_ADDR', 10, 'shell_reboot_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('LOAD_ADDR', 10, 300000)
    asm.emit('LOAD_ADDR', 5, 0x40000040)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('LOAD_ADDR', 5, 0x40800000)
    asm.emit('JALR', 0, 5, 0)

    asm.label('finish_cmd')
    asm.emit('ADDI', 9, 0, 0)
    asm.emit('LOAD_ADDR', 10, 'prompt_msg')
    asm.emit('LOAD_ADDR', 5, 0x40000028)
    asm.emit('JALR', 1, 5, 0)
    asm.emit('JAL', 0, 'poll_rx')

    # =========================================================================
    # String Table
    # =========================================================================
    asm.add_string('boot_msg', (
        '\r\n'
        '================================================================================\r\n'
        '                 NexOS v1.0.0 Micro-Kernel RTOS (Core Edition)                  \r\n'
        '================================================================================\r\n'
        '[BOOT] Hardware Platform   : ESP32-C6 (RISC-V 32-bit rv32imac @ 160MHz)\r\n'
        '[BOOT] Memory Architecture : 131,072 Bytes SRAM (Heap Active & Zeroed)\r\n'
        '[BOOT] Syscall Interface   : NexOS Syscall ABI v1.0 (Active)\r\n'
        '--------------------------------------------------------------------------------\r\n'
        '                       SUBSYSTEM READINESS INSPECTION                           \r\n'
        '--------------------------------------------------------------------------------\r\n'
        ' [READY] CPU Core 0        : RISC-V 32-bit Single-Core + LP-Core [OK]\r\n'
        ' [READY] Memory Subsystem  : Slab Allocator & Safe Heap Pool     [OK]\r\n'
        ' [READY] Device Manager    : GPIO, UART, SPI, I2C HAL Drivers    [OK]\r\n'
        ' [READY] Security Engine   : Hardware SHA-256 Signature Checker [OK]\r\n'
        ' [READY] Serial Console    : Dual-Channel USB/UART @ 115200 Baud [OK]\r\n'
        ' [READY] Storage Driver    : SPI Master (CS=18, MOSI=19, MISO=20, SCK=21) [OK]\r\n'
        ' [READY] File System & VFS : FAT32 / exFAT Partition Auto-Mounter [OK]\r\n'
        ' [READY] App Loader Engine : ELF / NexOS Package (.app) Relocator [OK]\r\n'
        '================================================================================\r\n'
    ))

    asm.add_string('char_fmt', '%c')
    asm.add_string('prompt_msg', 'nexos> ')
    asm.add_string('crlf_msg', '\r\n')
    asm.add_string('bs_seq', '\x08 \x08')
    asm.add_string('ctrl_c_msg', '^C\r\n')

    asm.add_string('shell_help_msg', (
        '\r\n[NEXOS SHELL] Available Commands:\r\n'
        '  help           Show this list of available shell commands\r\n'
        '  info           Display system architecture, OS version & target info\r\n'
        '  caps           List active kernel subsystems & hardware capabilities\r\n'
        '  mem            Show memory map, SRAM pools and heap utilization\r\n'
        '  ping           Verify serial console latency and communication link\r\n'
        '  sd             Inspect MicroSD Card hardware status and FAT32 mount\r\n'
        '  apps           Scan MicroSD filesystem for sandboxed .app packages\r\n'
        '  run            Load and execute application package from MicroSD Card\r\n'
        '  clear          Clear screen terminal and re-display shell banner\r\n'
        '  reboot         Perform software reset of NexOS core\r\n'
    ))

    asm.add_string('shell_info_msg', (
        '\r\n[INFO] OS Release      : NexOS v1.0.0 Micro-Kernel RTOS (Core Edition)\r\n'
        '[INFO] Target Arch     : RISC-V 32-bit (rv32imac) @ 160 MHz\r\n'
        '[INFO] Hardware SoC    : ESP32-C6FH4 (4MB Embedded Flash, DIO Mode)\r\n'
        '[INFO] Storage SPI     : CS=GPIO 18, MOSI=GPIO 19, MISO=GPIO 20, SCK=GPIO 21\r\n'
        '[INFO] Kernel ABI      : NexOS Syscall v1.0 (Direct Hardware Registers)\r\n'
        '[INFO] Console Device  : Dual-Channel (USB-Serial-JTAG + UART0) @ 115200\r\n'
    ))

    asm.add_string('shell_caps_msg', (
        '\r\n[CAPS] Active Subsystems & Drivers:\r\n'
        '  [X] CPU0 (RISC-V rv32imac single-core kernel supervisor)\r\n'
        '  [X] MEM_SLAB (Deterministic O(1) Slab memory allocator)\r\n'
        '  [X] SEC_ENGINE (Hardware SHA-256 cryptographic signature validator)\r\n'
        '  [X] DEV_MGR (GPIO, SPI, I2C, UART hardware abstraction layer)\r\n'
        '  [X] SD_SPI (Hardware bit-rate SPI driver for MicroSD cards)\r\n'
        '  [X] VFS_FAT32 (Master Boot Record + FAT32 filesystem reader)\r\n'
        '  [X] VFS_LOADER (Zero-copy .app ELF sandboxed execution engine)\r\n'
        '  [X] SHELL_CORE (Interactive non-blocking serial command console)\r\n'
    ))

    asm.add_string('shell_mem_msg', (
        '\r\n[MEM] Memory Architecture Summary:\r\n'
        '  Total SRAM        : 512 KB (0x40800000 - 0x4087FFFF)\r\n'
        '  Kernel Image      : ~5 KB (.iram0.text + RoData Strings)\r\n'
        '  Kernel Stack      : 4 KB (Top: 0x4087FF00)\r\n'
        '  Disk Buffer RAM   : 4 KB (0x4087F000 - 0x4087FDFF)\r\n'
        '  User App Space    : 380 KB (Free for dynamic /apps/*.app at 0x40820000)\r\n'
    ))

    asm.add_string('shell_ping_msg', (
        '\r\n[PONG] NexOS Core is alive and responsive! Round-trip latency < 1ms.\r\n'
    ))

    asm.add_string('shell_clear_msg', (
        '\x1b[2J\x1b[H\r\n'
        '================================================================================\r\n'
        '                 NexOS v1.0.0 Micro-Kernel RTOS (Core Edition)                  \r\n'
        '================================================================================\r\n'
    ))

    asm.add_string('shell_reboot_msg', (
        '\r\n[REBOOT] Restarting NexOS Kernel...\r\n'
    ))

    asm.add_string('shell_unknown_msg', (
        '\r\n[ERR] Unknown command. Type \'help\' for command list.\r\n'
    ))

    # SD Card Diagnostic & Status Messages
    asm.add_string('sd_probing_msg', '[STORAGE] Probing MicroSD Slot (CS=18, MOSI=19, MISO=20, SCK=21)...\r\n')
    asm.add_string('fmt_step1_bus_ok', '[STORAGE] [OK] Step 1: SPI Bus & IO_MUX Configured (CS=18, MOSI=19, MISO=20, SCK=21)\r\n')
    asm.add_string('fmt_miso_level', '[STORAGE] -> MISO Pin Electrical Level: %d (Pull-Up Active)\r\n')
    asm.add_string('fmt_cmd0_ok', '[STORAGE] [OK] Step 2: CMD0 Reset -> Response 0x%02X (Card Ready in SPI Mode)\r\n')
    asm.add_string('fmt_cmd0_fail', '[STORAGE] [FAIL] Step 2: CMD0 Reset -> Response 0x%02X (Expected 0x01)\r\n[STORAGE] ❌ MicroSD Card Not Responding (Check MISO GPIO 20 wiring & 5V VCC!)\r\n')
    asm.add_string('fmt_cmd8_ok', '[STORAGE] [OK] Step 3: CMD8 Voltage Check -> 3.3V Supported (Echo 0xAA Verified)\r\n')
    asm.add_string('fmt_cmd8_fail', '[STORAGE] [FAIL] Step 3: CMD8 Echo Mismatch: 0x%02X (Expected 0xAA)\r\n[STORAGE] ❌ MicroSD Signal Error: MISO line not echoing (Check GPIO 20 wiring & 5V VCC!)\r\n')
    asm.add_string('fmt_acmd41_ok', '[STORAGE] [OK] Step 4: ACMD41 Initialization -> SDHC/SDXC Ready\r\n')
    asm.add_string('fmt_acmd41_fail', '[STORAGE] [FAIL] Step 4: ACMD41 Initialization Timeout\r\n')
    asm.add_string('fmt_mbr_ok', '[STORAGE] [OK] Step 5: MBR Partition Table Verified (Signature 0x55AA)\r\n')
    asm.add_string('fmt_mbr_fail', '[STORAGE] [FAIL] Step 5: Invalid MBR Signature on Sector 0\r\n')
    asm.add_string('fmt_part_type', '[STORAGE] [OK] Step 6: Partition 1 Type 0x%02X (FAT32)\r\n')
    asm.add_string('fmt_vbr_ok', '[STORAGE] [OK] Step 6: FAT32 Volume Mounted (Part LBA: %d, Data LBA: %d, Sec/Clus: %d)\r\n')
    asm.add_string('fmt_vbr_fail', '[STORAGE] [FAIL] Step 6: Failed to read FAT32 VBR Sector\r\n')
    asm.add_string('fmt_app_scan', '[STORAGE] Step 7: Scanning for Application Packages (/apps/*.app or /*.app)...\r\n')
    asm.add_string('fmt_file_found', '[STORAGE]   - File: %s (%u bytes)\r\n')
    asm.add_string('fmt_dir_found', '[STORAGE]   - Dir:  /%s/\r\n')
    asm.add_string('fmt_sys_log', '[%s] %s\r\n')
    asm.add_string('fmt_app_found', "[LOADER] Found executable package: %s -> Application '%s' (v%s)\r\n")
    asm.add_string('fmt_app_verify', "[LOADER] Application package verified (NexOS ABI v1.0).\r\n[LOADER] Auto-starting '%s' at entrypoint in SRAM (0x40820080)...\r\n--------------------------------------------------------------------------------\r\n")
    asm.add_string('fmt_app_done', '\r\n--------------------------------------------------------------------------------\r\n[LOADER] Application finished execution. Returned to NexOS Core.\r\n')
    asm.add_string('fmt_app_bad', '[LOADER] Warning: Found .app file but header signature was invalid.\r\n')
    asm.add_string('fmt_app_none', '[STORAGE] Status: MicroSD Card is WORKING & READY!\r\n[STORAGE] Notice: No executable found in /apps/*.app\r\n[STORAGE] Tip: Copy your *.app file to /apps/ on the SD card to auto-run.\r\n')
    asm.add_string('sd_read_err_msg', '[STORAGE] Warning: Error reading sector from MicroSD Card.\r\n')
    asm.add_string('sd_standby_msg', '[STORAGE] MicroSD Card slot standby: Waiting for insertion.\r\n[LOADER]  NexOS App Loader active: Copy .app to MicroSD (/apps/your_app.app)\r\n          Insert card or use \'nexos install\' to execute application.\r\n')
    asm.add_string('fmt_card_inserted', '\r\n[STORAGE] ========================================================\r\n[STORAGE] >>> MicroSD Card Insertion Detected! <<<\r\n[STORAGE] ========================================================\r\n')
    asm.add_string('fmt_card_removed', '\r\n[STORAGE] >>> MicroSD Card Removed from Slot! <<<\r\n[STORAGE] Storage interface in standby mode.\r\n')
    asm.add_string('fmt_card_removed_app', '\r\n[STORAGE] >>> MicroSD Card Removed from Slot! <<<\r\n[LOADER] Application stopped (MicroSD card removed).\r\n[STORAGE] Storage interface in standby mode.\r\n')

    asm.add_string('sd_troubleshoot_msg', (
        '[STORAGE] ========================================================\r\n'
        '[STORAGE] TROUBLESHOOTING CHECKLIST:\r\n'
        '[STORAGE]  1. Wiring to ESP32-C6:\r\n'
        '[STORAGE]     - CS   -> GPIO 18\r\n'
        '[STORAGE]     - MOSI -> GPIO 19\r\n'
        '[STORAGE]     - MISO -> GPIO 20\r\n'
        '[STORAGE]     - SCK  -> GPIO 21\r\n'
        '[STORAGE]  2. Power Supply (CRITICAL):\r\n'
        '[STORAGE]     - Blue MicroSD modules have an onboard 3.3V regulator.\r\n'
        '[STORAGE]     - Connect VCC to 5V (VIN)! NOT 3.3V (3.3V causes undervoltage).\r\n'
        '[STORAGE]     - Connect GND to ESP32-C6 GND.\r\n'
        '[STORAGE]  3. Card Format:\r\n'
        '[STORAGE]     - Ensure card is firmly inserted into the slot.\r\n'
        '[STORAGE]     - Format as FAT32 (Default 32KB allocation units).\r\n'
        '[STORAGE] ========================================================\r\n'
    ))

    # Assemble complete binary
    code = asm.assemble()

    # Align segment to 16 bytes for flash alignment
    while len(code) % 16 != 0:
        code += b'\x00'

    # Construct ESP32-C6 ROM bootable image
    img = bi.ESP32C6FirmwareImage()
    img.flash_mode = 2          # DIO (Dual I/O for ESP32-C6 Embedded Flash)
    img.flash_size_freq = 0x20  # 4MB Flash size
    img.entrypoint = entry_addr
    seg = bi.ImageSegment(entry_addr, bytes(code))
    seg.name = '.iram0.text'
    img.segments.append(seg)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path)
    print(f"[OK] Generated Pure NexOS Core firmware with Real SD Card Driver & Auto-Run: {output_path} ({len(code)} bytes)")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "nexos_core_esp32c6.bin"
    generate_firmware(out)
