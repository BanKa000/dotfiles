#!/usr/bin/env python3
"""Generate a generic 1920x1080@60 HDMI EDID (base block + CEA-861 extension)."""
import sys


def checksum(block):
    block[127] = (-sum(block[:127])) & 0xFF
    return block


base = bytearray(128)
base[0:8] = bytes([0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00])
base[8:10] = bytes([0x31, 0xD8])          # manufacturer "LNX"
base[16] = 1                               # week
base[17] = 2026 - 1990                     # year
base[18:20] = bytes([1, 3])                # EDID 1.3
base[20] = 0x80                            # digital input
base[21:23] = bytes([80, 45])              # 80x45 cm
base[23] = 0x78                            # gamma 2.2
base[24] = 0x0A                            # RGB, preferred timing in DTD1
base[25:35] = bytes([0xEE, 0x91, 0xA3, 0x54, 0x4C, 0x99, 0x26, 0x0F, 0x50, 0x54])
base[35:38] = bytes([0x20, 0x00, 0x00])    # 640x480@60
base[38:54] = bytes([0xD1, 0xC0] + [0x01, 0x01] * 7)  # 1920x1080@60
# DTD 1: 1920x1080@60, 148.5 MHz (CEA VIC 16)
base[54:72] = bytes([0x02, 0x3A, 0x80, 0x18, 0x71, 0x38, 0x2D, 0x40,
                     0x58, 0x2C, 0x45, 0x00, 0x20, 0xC2, 0x31, 0x00, 0x00, 0x1E])
# Range limits: 56-75 Hz, 30-83 kHz, 170 MHz
base[72:90] = bytes([0, 0, 0, 0xFD, 0, 56, 75, 30, 83, 17, 0x00, 0x0A] + [0x20] * 6)
# Monitor name
name = b"Forced HDMI\n".ljust(13, b" ")
base[90:108] = bytes([0, 0, 0, 0xFC, 0]) + name
# Dummy descriptor
base[108:126] = bytes([0, 0, 0, 0x10, 0] + [0] * 13)
base[126] = 1                              # one extension
checksum(base)

blocks = bytes([
    0x42, 0x90, 0x04,                      # video: VIC16 (native), VIC4
    0x23, 0x09, 0x07, 0x07,                # audio: LPCM 2ch 32/44.1/48 kHz
    0x83, 0x01, 0x00, 0x00,                # speakers: FL/FR
    0x65, 0x03, 0x0C, 0x00, 0x10, 0x00,    # HDMI VSDB, phys addr 1.0.0.0
])
cea = bytearray(128)
cea[0:4] = bytes([0x02, 0x03, 4 + len(blocks), 0x40])  # basic audio
cea[4:4 + len(blocks)] = blocks
checksum(cea)

sys.stdout.buffer.write(bytes(base + cea))
