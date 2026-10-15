#!/usr/bin/env python3
"""Definitive analysis of the pseudo-dmg: concatenated zlib streams with
possible non-zlib gaps. Correct consumed accounting; scans across gaps.

Output: full payload to dmg-payload.bin, plus a JSON stream map.
"""
import zlib
import json

SRC = "/home/z/my-project/research/downloads/DRW-mac-installer.dmg"
OUT = "/home/z/my-project/research/extracted/mac-installer/dmg-payload.bin"
MAP = "/home/z/my-project/research/inventory/dmg-stream-map.json"

data = open(SRC, "rb").read()
n = len(data)

def parse_stream_at(offset):
    """Decompress the zlib stream starting exactly at offset.
    Returns (output_bytes, consumed) or None if no clean stream here."""
    d = zlib.decompressobj()
    try:
        out = d.decompress(data[offset:])
    except zlib.error:
        return None
    if not d.eof:
        return None
    consumed = (n - offset) - len(d.unused_data)
    if consumed <= 0:
        return None
    return out, consumed

out_parts = []
stream_map = []
pos = 0
gap_total = 0

while pos < n:
    res = parse_stream_at(pos)
    if res is None:
        # scan forward for next clean stream start
        found = None
        i = pos
        while i < n - 1:
            if data[i] == 0x78 and data[i + 1] in (0x01, 0x5E, 0x9C, 0xDA):
                r = parse_stream_at(i)
                if r is not None:
                    found = (i, r)
                    break
            i += 1
        if found is None:
            print(f"no further streams after {pos}; {n - pos} bytes remain undecoded")
            stream_map.append({"type": "tail", "start": pos, "end": n, "size": n - pos})
            break
        i, (o, c) = found
        gap = i - pos
        gap_total += gap
        print(f"GAP: {pos}..{i} ({gap} bytes) hex[0:48]={data[pos:pos+48].hex()}")
        stream_map.append({"type": "gap", "start": pos, "end": i, "size": gap})
        pos = i
        continue
    out, consumed = res
    out_parts.append(out)
    stream_map.append({"type": "zlib", "start": pos, "end": pos + consumed,
                       "in_size": consumed, "out_size": len(out)})
    print(f"stream [{pos:>8} .. {pos + consumed:>8}] in={consumed:>8} out={len(out):>8}")
    pos += consumed

payload = b"".join(out_parts)
print()
print(f"payload size: {len(payload)}")
print(f"gap bytes total: {gap_total}")
print(f"input decoded: {pos}/{n}")

with open(OUT, "wb") as f:
    f.write(payload)
with open(MAP, "w") as f:
    json.dump(stream_map, f, indent=1)
print(f"wrote {OUT} and {MAP}")
