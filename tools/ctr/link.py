#!/usr/bin/env python3
"""
Links compiled objects into a code image.

Every address range a linked unit claims in splits.txt is filled from that unit's
compiled object. Everything else is copied from the original image. The result is
only identical to the original if the compiled code is.

Usage:
    python tools/ctr/link.py config/jpn/config.toml -o build/jpn/code.bin \\
        [--map build/jpn/code.map] <unit>=<object> ...

Arguments may also be read from a response file with @<file>.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ctr.image import Image, VersionConfig
from ctr.linker import LinkContext, LinkError, PlacedObject
from ctr.symbols import Splits, SymbolTable, Unit


PADDING = b"\xff"


def describe(symbols: SymbolTable, addr: int) -> str:
    sym = symbols.containing(addr)
    if sym is None:
        return f"0x{addr:08X}"
    if sym.address == addr:
        return f"{sym.name} (0x{addr:08X})"
    return f"{sym.name}+0x{addr - sym.address:X} (0x{addr:08X})"


def link_unit(
    ctx: LinkContext, unit: Unit, path: Path, out: bytearray, map_lines: List[str]
) -> Tuple[int, List[str]]:
    """Returns the number of bytes linked and a list of mismatch descriptions."""
    config, image = ctx.config, ctx.image
    obj = PlacedObject(ctx, path, unit)

    # Nothing from the original image survives inside a linked unit's ranges. What the
    # object does not fill is alignment padding, for which armlink used 0xFF.
    for rng in unit.ranges:
        if config.section(rng.section).kind == "bss":
            continue
        start, end = image.offset(rng.start), image.offset(rng.end)
        out[start:end] = PADDING * (end - start)

    covered: List[Tuple[int, int]] = []
    linked = 0
    for placement in sorted(obj.placements.values(), key=lambda p: p.address):
        if not placement.owned:
            continue
        section = placement.section
        start, end = placement.address, placement.address + section.size
        for c_start, c_end in covered:
            if start < c_end and c_start < end:
                raise LinkError(
                    f"{path}: section {section.name} at 0x{start:08X} overlaps another section"
                )
        covered.append((start, end))
        map_lines.append(f"{start:08X} {section.size:08X} {unit.name}({section.name})")
        if config.section_at(start).kind == "bss":
            continue
        data = obj.relocate(placement)
        out[image.offset(start) : image.offset(end)] = data
        linked += len(data)

    for section in obj.removed:
        map_lines.append(f"-------- {section.size:08X} {unit.name}({section.name}) removed")

    # Explain what does not match, in terms a contributor can act on
    problems = []
    for rng in unit.ranges:
        if config.section(rng.section).kind == "bss":
            continue
        original = image.read(rng.start, rng.end - rng.start)
        built = out[image.offset(rng.start) : image.offset(rng.end)]
        if original == built:
            continue
        reported = set()
        for i, (a, b) in enumerate(zip(original, built)):
            if a == b:
                continue
            addr = rng.start + i
            sym = ctx.symbols.containing(addr)
            key = sym.name if sym is not None else addr & ~0xF
            if key in reported:
                continue
            reported.add(key)
            provided = any(s <= addr < e for s, e in covered)
            reason = "differs" if provided else "is not provided by the object"
            problems.append(f"{unit.name}: {describe(ctx.symbols, addr)} {reason}")
    return linked, problems


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    parser.add_argument("config", type=Path, help="path to config.toml")
    parser.add_argument("-o", "--out", type=Path, required=True, help="output code.bin")
    parser.add_argument("--map", type=Path, help="write a link map")
    parser.add_argument("units", nargs="*", metavar="UNIT=OBJECT", help="units to link")
    # Positionals after options: Python before 3.13 leaves "units" empty otherwise
    args = parser.parse_intermixed_args()

    specs: List[str] = []
    for spec in args.units:
        if spec.startswith("@"):
            specs += Path(spec[1:]).read_text().split()
        else:
            specs.append(spec)

    config = VersionConfig(args.config)
    image = Image.load(config)
    symbols = SymbolTable.load(config.symbols_path)
    splits = Splits.load(config.splits_path)
    ctx = LinkContext(config, image, symbols)

    out = bytearray(image.data)
    map_lines: List[str] = []
    problems: List[str] = []
    total = 0
    try:
        for spec in specs:
            name, _, path = spec.partition("=")
            unit = splits.unit(name)
            if unit is None:
                raise LinkError(f"{name} has no entry in {config.splits_path}")
            linked, unit_problems = link_unit(ctx, unit, Path(path), out, map_lines)
            total += linked
            problems += unit_problems
    except LinkError as e:
        raise SystemExit(f"error: {e}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(out)
    if args.map:
        args.map.write_text("\n".join(sorted(map_lines)) + "\n")

    print(f"Linked {len(specs)} units ({total} bytes from compiled objects) into {args.out}")
    if problems:
        print(f"{len(problems)} symbols do not match the original:", file=sys.stderr)
        for problem in problems[:50]:
            print(f"  {problem}", file=sys.stderr)
        if len(problems) > 50:
            print(f"  ... and {len(problems) - 50} more", file=sys.stderr)


if __name__ == "__main__":
    main()
