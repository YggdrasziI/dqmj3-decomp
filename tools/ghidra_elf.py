#!/usr/bin/env python3
"""
Writes the original code.bin as an ELF executable for Ghidra.

The segments and their addresses come from config/<version>/config.toml (the
extended header of the game): one PT_LOAD per section, `.bss` without file data.
The ELF holds no symbols: tools/ghidra_sync.py applies symbols.txt after import, so
the same script both fills a new project and updates an existing one.

Usage:
    python tools/ghidra_elf.py [--version jpn] [-o build/jpn/code.elf]
"""

import argparse
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from ctr.image import Image, VersionConfig  # noqa: E402

ET_EXEC, EM_ARM, PT_LOAD = 2, 40, 1
PF_X, PF_W, PF_R = 1, 2, 4
SHT_PROGBITS, SHT_STRTAB, SHT_NOBITS = 1, 3, 8
SHF_WRITE, SHF_ALLOC, SHF_EXECINSTR = 1, 2, 4
EF_ARM_EABI_VER5 = 0x05000000

FLAGS = {  # section kind -> (segment flags, section flags)
    "code": (PF_R | PF_X, SHF_ALLOC | SHF_EXECINSTR),
    "rodata": (PF_R, SHF_ALLOC),
    "data": (PF_R | PF_W, SHF_ALLOC | SHF_WRITE),
    "bss": (PF_R | PF_W, SHF_ALLOC | SHF_WRITE),
}


def build(config: VersionConfig, image: Image) -> bytes:
    sections = [s for s in config.sections]
    ehsize, phentsize, shentsize = 52, 32, 40
    phoff = ehsize
    data_start = phoff + phentsize * len(sections)
    data_start = (data_start + 0xFFF) & ~0xFFF

    body = bytearray()
    placed = []  # (section, file offset, file size)
    for s in sections:
        if s.kind == "bss":
            placed.append((s, data_start + len(body), 0))
            continue
        while len(body) % 0x1000:
            body.append(0)
        offset = data_start + len(body)
        body += image.read(s.address, s.size)
        placed.append((s, offset, s.size))

    shstr = bytearray(b"\0")
    names = []
    for s in sections:
        names.append(len(shstr))
        shstr += s.name.encode() + b"\0"
    shstr_name = len(shstr)
    shstr += b".shstrtab\0"

    shstr_off = data_start + len(body)
    shoff = (shstr_off + len(shstr) + 3) & ~3

    out = bytearray(data_start)
    out += body
    out += shstr
    out += b"\0" * (shoff - len(out))
    # Section headers: null, the image sections, .shstrtab
    out += b"\0" * shentsize
    for (s, offset, size), name in zip(placed, names):
        stype = SHT_NOBITS if s.kind == "bss" else SHT_PROGBITS
        out += struct.pack("<IIIIIIIIII", name, stype, FLAGS[s.kind][1], s.address, offset,
                           s.size, 0, 0, 4, 0)
    out += struct.pack("<IIIIIIIIII", shstr_name, SHT_STRTAB, 0, 0, shstr_off, len(shstr), 0, 0, 1, 0)

    ident = b"\x7fELF" + bytes([1, 1, 1, 0]) + bytes(8)
    struct.pack_into("<16sHHIIIIIHHHHHH", out, 0, ident, ET_EXEC, EM_ARM, 1, config.base, phoff, shoff,
                     EF_ARM_EABI_VER5, ehsize, phentsize, len(sections), shentsize, len(sections) + 2,
                     len(sections) + 1)
    for i, (s, offset, size) in enumerate(placed):
        struct.pack_into("<IIIIIIII", out, phoff + i * phentsize, PT_LOAD, offset, s.address, s.address,
                         size, s.size, FLAGS[s.kind][0], 0x1000)
    return bytes(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--version", default="jpn")
    parser.add_argument("-o", "--out", type=Path)
    args = parser.parse_args()
    config = VersionConfig(ROOT / "config" / args.version / "config.toml")
    image = Image.load(config)
    out = args.out or ROOT / "build" / args.version / "code.elf"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(build(config, image))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
