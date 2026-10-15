#!/usr/bin/env python3
"""UDIF reconstruction v2 — empirical mish layout:
  header 204 bytes: sig@0, ver@4, sectorNumber@8, sectorCount@0x10,
  dataOffset@0x18, misc@0x20..0x40, blockCount@0x40, misc@0x44/0x48, zeros to 0xCC
  chunks at 0xCC, 40 bytes each: type u32, comment u32, sector u64,
  sectors u64, compOffset u64, compLen u64
Chunk types sniffed+verified against data (zlib 78xx, bzip2 'BZh', lzfse 'bvx').
"""
import struct
import zlib
import json
import plistlib

SRC = "/home/z/my-project/research/downloads/DRW-mac-installer.dmg"
OUT = "/home/z/my-project/research/extracted/mac-installer/disk-image.bin"
REPORT = "/home/z/my-project/research/inventory/dmg-udif-report.json"

data = open(SRC, "rb").read()
koly = data[-512:]
assert koly[:4] == b"koly"
(xml_offset, xml_length) = struct.unpack_from(">QQ", koly, 0xD8)
(sector_count,) = struct.unpack_from(">Q", koly, 0x1EC)
data_fork_offset, data_fork_length = struct.unpack_from(">QQ", koly, 0x18)
print(f"sector_count={sector_count} data_fork={data_fork_offset}+{data_fork_length}")
print(f"image size should be {sector_count * 512}")

pl = plistlib.loads(data[xml_offset:xml_offset + xml_length])
blkx = pl["resource-fork"]["blkx"]
print(f"blkx partitions: {len(blkx)}")

def parse_mish(blob):
    (sig, version) = struct.unpack_from(">4sI", blob, 0)
    assert sig == b"mish"
    sector_number, sector_count, data_offset = struct.unpack_from(">QQQ", blob, 8)
    block_count = struct.unpack_from(">I", blob, 0x40)[0]
    entries = []
    p = 0xCC
    for i in range(block_count):
        if p + 40 > len(blob):
            raise ValueError(f"chunk {i} overruns blob ({p + 40} > {len(blob)})")
        ctype, comment, sec, secs, off, ln = struct.unpack_from(">IIQQQQ", blob, p)
        entries.append(dict(type=ctype, sector=sec, sectors=secs, offset=off, length=ln))
        p += 40
    return sector_number, sector_count, data_offset, entries

image = bytearray(sector_count * 512)
TYPE_NAMES = {0: "zero", 1: "raw", 2: "ignore", 0x7FFFFFFE: "comment",
              0xFFFFFFFF: "terminator", 0x80000003: "adc", 0x80000004: "zlib?",
              0x80000005: "bzip2?", 0x80000006: "lzfse?", 0x80000007: "lzma?"}

report = []
problems = []
for bi, entry in enumerate(blkx):
    blob = entry["Data"]
    sn, sc, doff, entries = parse_mish(blob)
    print(f"\nblkx[{bi}] {entry.get('Name')!r}: partition sectors [{sn}..{sn + sc}) ({sc} sectors), {len(entries)} chunks")
    r = {"name": entry.get("Name"), "sector_number": sn, "sector_count": sc,
         "data_offset": doff, "chunks": []}
    for e in entries:
        t = e["type"]
        tname = TYPE_NAMES.get(t, hex(t))
        dest = (sn + e["sector"]) * 512
        length = e["sectors"] * 512
        src = data_fork_offset + doff + e["offset"]
        status = None
        if t == 0xFFFFFFFF or t == 0x7FFFFFFE:
            status = "meta"
        elif t in (0, 2):
            status = f"{TYPE_NAMES[t]} ({length} B)"
        elif t in (1,):
            image[dest:dest + e["length"]] = data[src:src + e["length"]]
            status = "raw ok"
        else:
            raw = data[src:src + e["length"]]
            algo = None
            try:
                if raw[:1] == b"\x78":
                    out = zlib.decompress(raw)
                    algo = "zlib"
                elif raw[:3] == b"BZh":
                    import bz2
                    out = bz2.decompress(raw)
                    algo = "bzip2"
                elif raw[:4] in (b"bvx-", b"bvx2", b"bvxn"):
                    algo = "lzfse (unsupported)"
                    out = b""
                    problems.append(f"lzfse chunk in blkx[{bi}]")
                else:
                    algo = f"unknown magic {raw[:4].hex()}"
                    out = b""
            except Exception as ex:
                problems.append(f"blkx[{bi}] chunk@{src}: {ex}")
                out = b""
            if algo == "zlib" or algo == "bzip2":
                if len(out) != length:
                    problems.append(
                        f"blkx[{bi}] chunk outlen {len(out)} != expected {length} ({algo})")
                image[dest:dest + len(out)] = out
                status = f"{algo} ok ({len(out)} B)"
            else:
                status = algo
        r["chunks"].append({"type": hex(t), "type_name": tname, "sector": e["sector"],
                            "sectors": e["sectors"], "src": src, "len": e["length"],
                            "status": status})
        print(f"   chunk type={tname:<10} sector={e['sector']:>8} sectors={e['sectors']:>8} "
              f"src={src:>9} len={e['length']:>9} -> {status}")
    report.append(r)

print("\n--- problems ---")
for p in problems[:20]:
    print(" ", p)
print(f"({len(problems)} problems)")

with open(OUT, "wb") as f:
    f.write(image)
with open(REPORT, "w") as f:
    json.dump(report, f, indent=1)
print(f"\nwrote {OUT} ({len(image)} bytes) and {REPORT}")
