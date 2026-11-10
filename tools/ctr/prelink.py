#!/usr/bin/env python3
"""
Prepares a compiled object for comparison in objdiff.

The objects split out of the original image contain code as armlink left it. One of
the things armlink did cannot be undone when splitting: calls to functions that are
empty or a single instruction were replaced by `mov r0, r0` or by that instruction
(armlink --inline), and nothing records which function used to be called.

So the same transformation is applied to the compiled object instead. Its other
relocations are left alone, which keeps the comparison symbolic.

The other thing armlink did that shows in the data is removing virtual functions
that are never called. Their vtable entries are 0 in the original, so entries that
point to a function symbols.txt does not know are cleared here as well.

Usage:
    python tools/ctr/prelink.py config/jpn/config.toml [--unit <unit>] <in.o> -o <out.o>
"""

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ctr.image import Image, VersionConfig
from ctr.linker import LinkContext, LinkError, PlacedObject, Placement
from ctr.symbols import Splits, SymbolTable

SH_SIZE_OFFSET = 20  # sh_size within Elf32_Shdr
REL_ENTRY_SIZE = 8
MAX_BATCH_SIZE = 64


def load_context(config_path: Path) -> tuple[VersionConfig, LinkContext]:
    """Load immutable image/symbol inputs once for a CLI invocation or batch."""
    config = VersionConfig(config_path)
    image = Image.load(config)
    symbols = SymbolTable.load(config.symbols_path)
    return config, LinkContext(config, image, symbols)


def load_unit(unit_name: Optional[str], unit_splits: Optional[Path], config: VersionConfig):
    if unit_name is None:
        return None
    unit = Splits.load(unit_splits or config.splits_path).unit(unit_name)
    if unit is None:
        raise ValueError(f"no unit named {unit_name}")
    return unit


def validate_batch_jobs(batch: dict) -> List[dict]:
    jobs = batch.get("jobs")
    if not isinstance(jobs, list) or not 1 <= len(jobs) <= MAX_BATCH_SIZE:
        raise ValueError(f"batch jobs must contain 1..{MAX_BATCH_SIZE} entries")
    required = {"unit", "input", "unit_splits", "output"}
    for index, job in enumerate(jobs):
        if not isinstance(job, dict) or not required.issubset(job):
            raise ValueError(f"batch job {index} must contain {', '.join(sorted(required))}")
        if any(not isinstance(job[key], str) or not job[key] for key in required):
            raise ValueError(f"batch job {index} fields must be nonempty strings")
    outputs = [str(Path(job["output"]).resolve()) for job in jobs]
    if len(outputs) != len(set(outputs)):
        raise ValueError("batch contains duplicate output paths")
    inputs = {str(Path(job["input"]).resolve()) for job in jobs}
    if inputs.intersection(outputs):
        raise ValueError("batch output path collides with an input path")
    stamp = batch.get("stamp")
    if stamp is not None:
        if not isinstance(stamp, str) or not stamp:
            raise ValueError("batch success stamp must be a nonempty path")
        stamp_path = str(Path(stamp).resolve())
        if stamp_path in set(outputs) or stamp_path in inputs:
            raise ValueError("batch success stamp must not collide with an object path")
    return jobs


def prepare_object(
    ctx: LinkContext, input_path: Path, output_path: Path, unit
) -> int:
    """Apply armlink transformations to one object using a fresh placement."""
    obj = PlacedObject(ctx, input_path, unit, strict=False)

    data = bytearray(input_path.read_bytes())
    removed: Dict[int, Set[int]] = {}
    count = 0
    for section in obj.elf.sections:
        if not section.is_code or not section.relocs:
            continue
        placement = obj.placements.get(section.index)
        if placement is None:
            # Calls can be resolved without knowing where the caller ends up
            placement = Placement(section, 0, False)
        for reloc, insn in obj.inlined_calls(placement):
            struct.pack_into("<I", data, section.offset + reloc.offset, insn)
            rel_index, entry = reloc.origin
            removed.setdefault(rel_index, set()).add(entry)
            count += 1

    for section in obj.elf.sections:
        for reloc in obj.removed_virtuals(section):
            struct.pack_into("<I", data, section.offset + reloc.offset, 0)
            rel_index, entry = reloc.origin
            removed.setdefault(rel_index, set()).add(entry)

    # Drop the relocations of the calls that no longer exist
    for rel_index, entries in removed.items():
        rel = obj.elf.sections[rel_index]
        total = len(rel.data) // REL_ENTRY_SIZE
        kept = b"".join(
            rel.data[i * REL_ENTRY_SIZE : (i + 1) * REL_ENTRY_SIZE]
            for i in range(total)
            if i not in entries
        )
        data[rel.offset : rel.offset + len(rel.data)] = kept.ljust(len(rel.data), b"\0")
        header = obj.elf.shoff + rel_index * obj.elf.shentsize
        struct.pack_into("<I", data, header + SH_SIZE_OFFSET, len(kept))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)
    return count


def run_batch(config_path: Path, manifest_path: Path) -> int:
    batch = json.loads(manifest_path.read_text(encoding="utf-8"))
    jobs = validate_batch_jobs(batch)
    stamp = batch.get("stamp")
    if stamp:
        Path(stamp).unlink(missing_ok=True)
    config, ctx = load_context(config_path)
    total_inline = 0
    for job in jobs:
        unit_name = job["unit"]
        try:
            unit = load_unit(unit_name, Path(job["unit_splits"]), config)
            total_inline += prepare_object(
                ctx, Path(job["input"]), Path(job["output"]), unit
            )
        except (LinkError, ValueError) as exc:
            raise SystemExit(f"{unit_name}: {exc}") from None

    # The success stamp is created only after every output has been written.
    # Its presence lets the multi-output Ninja edge distinguish a completed
    # shard from a partial run after an error.
    if stamp:
        stamp_path = Path(stamp)
        stamp_path.parent.mkdir(parents=True, exist_ok=True)
        stamp_path.write_text("prelink batch complete\n", encoding="utf-8")
    print(f"prepared {len(jobs)} objects; inlined {total_inline} calls")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    parser.add_argument("config", type=Path, help="path to config.toml")
    parser.add_argument("input", type=Path, nargs="?", help="object compiled by armcc")
    parser.add_argument("-o", "--out", type=Path, help="output object")
    parser.add_argument("--unit", help="name of the unit in splits.txt")
    parser.add_argument("--unit-splits", type=Path, help="split descriptor for this unit only")
    parser.add_argument("--batch-manifest", type=Path, help="bounded JSON manifest for a prelink shard")
    args = parser.parse_args()

    try:
        if args.batch_manifest:
            if args.input or args.out or args.unit or args.unit_splits:
                raise ValueError("--batch-manifest cannot be combined with single-object arguments")
            run_batch(args.config, args.batch_manifest)
            return
        if args.input is None or args.out is None:
            raise ValueError("single-object mode requires input and -o/--out")
        config, ctx = load_context(args.config)
        unit = load_unit(args.unit, args.unit_splits, config)
        prepare_object(ctx, args.input, args.out, unit)
    except (LinkError, ValueError, OSError, json.JSONDecodeError) as e:
        raise SystemExit(f"error: {e}") from None


if __name__ == "__main__":
    main()
