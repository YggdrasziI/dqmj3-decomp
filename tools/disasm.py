#!/usr/bin/env python3
"""
Prints the disassembly of functions of the original image.

Finds the split object (build/<version>/delink/) of the unit that holds each symbol and
disassembles it with objdiff-cli. Relocation targets are shown by name, and literal
pool words that hold text are shown as strings. Run `ninja split` first.

Usage:
    python tools/disasm.py fn_002546FC [fn_001446A0 ...] [--version jpn]
"""

import argparse
import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from ctr.image import VersionConfig  # noqa: E402
from ctr.symbols import Splits, SymbolTable  # noqa: E402
from ctr.units import object_name, resolve_units  # noqa: E402


def text_of(words):
    data = b"".join(struct.pack("<I", w) for w in words)
    return data.split(b"\0")[0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("symbols", nargs="+")
    parser.add_argument("--version", default="jpn")
    args = parser.parse_args()

    config = VersionConfig(ROOT / "config" / args.version / "config.toml")
    symbols = SymbolTable.load(ROOT / config.symbols_path)
    splits = Splits.load(ROOT / config.splits_path)
    units = resolve_units(config, splits, symbols)
    objdiff = ROOT / "build" / "tools" / ("objdiff-cli.exe" if sys.platform == "win32" else "objdiff-cli")
    by_name = {s.name: s for s in symbols}

    for name in args.symbols:
        sym = by_name.get(name)
        if sym is None:
            print(f"{name}: not in symbols.txt")
            continue
        unit = next((u for u in units if any(r.start <= sym.address < r.end for r in u.ranges)), None)
        obj = ROOT / "build" / args.version / "delink" / object_name(unit)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "d.json"
            subprocess.run([str(objdiff), "diff", "-1", str(obj), "-o", str(out), "--format", "json", name],
                           check=True, capture_output=True)
            data = json.loads(out.read_text())
        side = data["left"]
        names = [s.get("name", "?") for s in side["symbols"]]
        fn = next(s for s in side["symbols"] if s.get("name") == name)
        mode = " (thumb)" if sym.thumb else ""
        print(f"{name} @ 0x{sym.address:08X}, 0x{sym.size:X} bytes{mode}, unit {unit.name}")
        pool = []
        for ins in fn.get("instructions", []):
            i = ins["instruction"]
            off = int(i.get("address", 0))
            text = i["formatted"]
            rel = i.get("relocation")
            if rel is not None:
                target = names[rel["target_symbol"]] if rel["target_symbol"] < len(names) else "?"
                text = f"{text}    ; {rel['type_name']} {target}"
            if text.startswith(".word 0x"):
                pool.append(int(text.split()[1], 16))
                continue
            if pool:
                print(f"           .ascii {text_of(pool)!r}")
                pool = []
            print(f"  {sym.address + off:08X}  {text}")
        if pool:
            print(f"           .ascii {text_of(pool)!r}")
        print()


if __name__ == "__main__":
    main()
