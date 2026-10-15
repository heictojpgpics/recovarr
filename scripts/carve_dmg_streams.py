#!/usr/bin/env python3
"""Robustly carve concatenated zlib streams out of the pseudo-dmg file.

Strategy: greedily decompress from current position. When a stream ends
(zlib eof), continue from unused_data. If the next byte is not a valid zlib
stream start, scan forward one byte at a time until a position yields a
cleanly-terminating zlib stream. Concatenate all decompressed output.
"""
import zlib

SRC = "/home/z/my-project/research/downloads/DRW-mac-installer.dmg"
OUT = "/home/z/my-project/research/extracted/mac-installer/dmg-payload.bin"

data = open(SRC, "rb").read()
n = len(data)
print(f"input: {n} bytes")

out = bytearray()
pos = 0
stream_no = 0
skipped_total = 0

def try_stream(buf, offset):
    """Try to decompress a zlib stream starting exactly at offset.
    Returns (decompressed_bytes, bytes_consumed) or None."""
    d = zlib.decompressobj()
    try:
        first = d.decompress(buf[offset:offset + 65536])
        if first == b"" and not d.eof:
            return None
    except zlib.error:
        return None
    # feed the rest in chunks to avoid huge memory spikes
    chunks = [first]
    p = offset + 65536
    while p < len(buf) and not d.eof:
        try:
            chunks.append(d.decompress(buf[p:p + 1 << 20]))
        except zlib.error:
            return None
        p += 1 << 20
    if not d.eof:
        return None
    consumed = (len(buf) - offset) - len(d.unused_data)
    return b"".join(chunks), consumed

while pos < n:
    res = try_stream(data, pos)
    if res is None:
        # scan forward for next stream start
        nxt = None
        scan = pos
        while scan < n - 2:
            if data[scan] == 0x78 and data[scan + 1] in (0x01, 0x5e, 0x9c, 0xda):
                r = try_stream(data, scan)
                if r is not None:
                    nxt = scan
                    break
            scan += 1
        if nxt is None:
            print(f"no further zlib stream found after offset {pos}")
            break
        skipped_total += nxt - pos
        print(f"gap: skipped {nxt - pos} bytes ({pos:#x} -> {nxt:#x})")
        pos = nxt
        continue
    payload, consumed = res
    stream_no += 1
    out.extend(payload)
    pos += consumed

print(f"streams decoded: {stream_no}")
print(f"total skipped (inter-stream) bytes: {skipped_total}")
print(f"decompressed size: {len(out)}")
print(f"coverage: consumed {pos} of {n} input bytes ({100.0 * pos / n:.1f}%)")

with open(OUT, "wb") as f:
    f.write(bytes(out))
print(f"wrote {OUT}")
