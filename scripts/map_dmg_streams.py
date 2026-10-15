#!/usr/bin/env python3
"""Precisely map zlib stream boundaries in the pseudo-dmg."""
import zlib

SRC = "/home/z/my-project/research/downloads/DRW-mac-installer.dmg"
data = open(SRC, "rb").read()
n = len(data)

pos = 0
boundaries = []
total_out = 0
while pos < n:
    d = zlib.decompressobj()
    out = d.decompress(data[pos:])
    if not d.eof:
        print(f"stream at {pos}: ran to end of file without eof, output {len(out)}")
        total_out += len(out)
        boundaries.append((pos, n, len(out)))
        break
    consumed = (n - pos) - len(d.unused_data)
    boundaries.append((pos, pos + consumed, len(out)))
    total_out += len(out)
    pos += consumed
    # peek at what follows
    if pos < n:
        nxt = data[pos:pos + 16]
        print(f"stream ends at {pos}; next 16 bytes: {nxt.hex()}  {nxt!r}")

print()
print("boundaries (start, end, out_size):")
for b in boundaries:
    print(f"  {b[0]:>9} - {b[1]:>9}  out={b[2]:>9}")
print(f"total input consumed: {pos} of {n}")
print(f"total output so far: {total_out}")
