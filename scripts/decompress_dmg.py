#!/usr/bin/env python3
"""Decompress the mislabeled 'dmg' file: raw zlib stream(s) -> payload, then identify it."""
import zlib

SRC = "/home/z/my-project/research/downloads/DRW-mac-installer.dmg"
OUT = "/home/z/my-project/research/extracted/mac-installer/dmg-payload.bin"

data = open(SRC, "rb").read()
print(f"input: {len(data)} bytes, first bytes: {data[:8].hex()}")

# Handle possibly-concatenated zlib streams
out = bytearray()
pos = 0
streams = 0
while pos < len(data):
    d = zlib.decompressobj()
    try:
        chunk = d.decompress(data[pos:])
        out.extend(chunk)
        while d.unconsumed_tail:
            out.extend(d.decompress(d.unconsumed_tail))
        pos += len(data[pos:]) - len(d.unused_data)
        streams += 1
        if not d.eof:
            print(f"stream {streams} ended without eof marker at pos {pos}")
            break
        if pos >= len(data) or data[pos:pos+1] == b"":
            break
        # skip any padding zero bytes between streams
        while pos < len(data) and data[pos] == 0:
            pos += 1
        if pos >= len(data):
            break
        # if next bytes are not a zlib header, stop
        if data[pos] != 0x78:
            print(f"non-zlib byte 0x{data[pos]:02x} at offset {pos}; stopping")
            break
    except zlib.error as e:
        print(f"zlib error at pos {pos}: {e}")
        break

print(f"decompressed: {len(out)} bytes from {streams} zlib stream(s)")
with open(OUT, "wb") as f:
    f.write(bytes(out))
print(f"wrote {OUT}")
print(f"payload head hex: {bytes(out[:16]).hex()}")
