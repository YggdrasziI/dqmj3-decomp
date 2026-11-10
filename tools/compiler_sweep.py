#!/usr/bin/env python3
"""
Compiles reference sources with armcc builds and finds their functions in code.bin.

Used to identify the compiler (and the flags) the game and its libraries were built
with: a function that compiles to the exact bytes found in the game, relocations
aside, is evidence for the build and flags that produced it. A function found with
some builds and not others narrows the build down.

Sources come either from files given on the command line (compiled with --flags), or
from another project that uses the same configure.py layout (BigRed's, decomp-toolkit's):
`--project <dir>` lists its objects with their own flags.

Usage:
    python tools/compiler_sweep.py --project <dir> [--filter nn/] [--builds 4.1/b894,...]
    python tools/compiler_sweep.py [--flags "..."] [-I dir] <source> ...

Matching rules:
  - each function is taken from its own section (armcc --split_sections), literal
    pool included;
  - relocated words are masked: data words entirely, ARM branches except for their
    condition and opcode (so that `b` and `bl` stay apart). A call that armlink
    replaced with `mov r0, r0` or with the called instruction is therefore not found;
  - only functions of at least --min-size bytes with at least 3 unmasked words are
    searched, at 4-byte (ARM) or 2-byte (Thumb) alignment in .text;
  - a function found at more than one address is counted as ambiguous, not a match;
    a name that two sources define and that is found at two addresses is a conflict.

Compilers are expected in build/compilers/<build>/bin/armcc.exe (downloaded with
tools/download_tool.py armcc when missing).
"""

import argparse
import json
import os
import re
import runpy
import shlex
import subprocess
import sys
import tempfile
import types
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from ctr import elf  # noqa: E402
from ctr.image import Image, VersionConfig  # noqa: E402

ALL_BUILDS = [
    "4.0/b771", "4.0/b821", "4.0/b865", "4.0/b902",
    "4.1/b561", "4.1/b713", "4.1/b791", "4.1/b844", "4.1/b894", "4.1/b921",
    "4.1/b1049", "4.1/b1440", "4.1/b1454", "5.04/b82",
]
DEFAULT_FLAGS = ("--cpp --arm --cpu=MPCore --fpmode=fast --apcs=/interwork --split_sections "
                 "-O3 -Otime --no_rtti --no_rtti_data --signed_chars")


def armcc_path(build: str) -> Path:
    exe = ROOT / "build" / "compilers" / build / "bin" / "armcc.exe"
    if not exe.is_file():
        subprocess.run([sys.executable, str(ROOT / "tools" / "download_tool.py"), "armcc",
                        "--tag", build, str(exe)], check=True)
    return exe


def project_objects(project: Path) -> List[Tuple[Path, List[str]]]:
    """(source, flags) of every object of a configure.py project, without running a build."""
    captured = {}

    def capture(config):
        captured["config"] = config

    sys.path.insert(0, str(project))
    old_argv, old_cwd = sys.argv, os.getcwd()
    try:
        os.chdir(project)
        sys.argv = [str(project / "configure.py")]
        # Load the project's own tools.project, then replace what would write files
        for name in [m for m in sys.modules if m == "tools" or m.startswith("tools.")]:
            del sys.modules[name]
        import importlib
        proj = importlib.import_module("tools.project")
        proj.generate_build = capture
        runpy.run_path(str(project / "configure.py"), run_name="__main__")
    finally:
        sys.argv = old_argv
        os.chdir(old_cwd)
        sys.path.remove(str(project))
        for name in [m for m in sys.modules if m == "tools" or m.startswith("tools.")]:
            del sys.modules[name]
    config = captured["config"]
    out = []
    for lib in config.libs:
        src_dir = project / lib.get("src_dir", "src")
        for obj in lib["objects"]:
            # Same resolution as tools/project.py (ResolvedObject)
            flags = list(obj.options.get("cflags", lib.get("cflags", config.cflags)))
            flags += list(obj.options.get("extra_cflags", []))
            # Include directories are relative to the project: make them absolute
            kept, it = [], iter(flags)
            for f in it:
                if f == "-I":
                    f = "-I" + next(it, "")
                if f.startswith("-I"):
                    path = Path(f[2:])
                    kept.append(f"-I{path if path.is_absolute() else project / path}")
                else:
                    kept.append(f)
            out.append((src_dir / obj.name, kept))
    return out


def compile_one(armcc: Path, source: Path, flags: List[str], includes: List[Path],
                out: Path) -> Optional[str]:
    system = armcc.parent.parent / "include"
    cmd = [str(armcc), "-c", *flags, *[f"-I{p}" for p in includes], f"-J{system}", str(source), "-o", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        lines = [l for l in (r.stdout + r.stderr).splitlines() if "Error" in l]
        return lines[0].strip() if lines else "error"
    return None


def functions_of(path: Path, min_size: int):
    """(name, thumb, pattern bytes, mask) for each function alone in its section."""
    obj = elf.ElfFile.load(path)
    by_section: Dict[int, list] = {}
    for sym in obj.symbols:
        if sym.type == elf.STT_FUNC and sym.is_defined and 0 < sym.shndx < len(obj.sections):
            by_section.setdefault(sym.shndx, []).append(sym)
    for shndx, syms in by_section.items():
        if len(syms) != 1:
            continue
        sym = syms[0]
        sec = obj.sections[shndx]
        if not sec.is_code or sym.value & ~1:
            continue
        data = bytearray(sec.data)
        if len(data) < min_size:
            continue
        mask = bytearray(b"\xff" * len(data))
        for rel in sec.relocs:
            if rel.type in (elf.R_ARM_CALL, elf.R_ARM_JUMP24, elf.R_ARM_PC24):
                # Keep the condition and opcode: a `b` must not match a `bl`
                masked = range(rel.offset, rel.offset + 3)
            elif rel.type in (elf.R_ARM_THM_CALL, elf.R_ARM_THM_JUMP24):
                masked = range(rel.offset, rel.offset + 4)
            else:
                masked = range(rel.offset & ~3, (rel.offset & ~3) + 4)
            for i in masked:
                if i < len(data):
                    mask[i] = 0
        if sum(1 for i in range(0, len(mask) - 3, 4) if mask[i:i + 4] == b"\xff\xff\xff\xff") < 3:
            continue
        yield sym.name, bool(sym.value & 1), bytes(data), bytes(mask)


def find(text: bytes, base: int, data: bytes, mask: bytes, thumb: bool) -> List[int]:
    parts = []
    for b, m in zip(data, mask):
        parts.append(re.escape(bytes([b])) if m else b".")
    pattern = re.compile(b"".join(parts), re.DOTALL)
    align = 2 if thumb else 4
    hits = []
    pos = 0
    while True:
        m = pattern.search(text, pos)
        if not m:
            break
        if m.start() % align == 0:
            hits.append(base + m.start())
            if len(hits) > 1:
                break
        pos = m.start() + 1
    return hits


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("sources", nargs="*", type=Path)
    parser.add_argument("--project", type=Path, help="configure.py project to take sources and flags from")
    parser.add_argument("--filter", action="append", default=[],
                        help="only sources whose path contains this (repeatable)")
    parser.add_argument("--flags", default=DEFAULT_FLAGS, help="flags for sources given on the command line")
    parser.add_argument("-I", dest="includes", action="append", type=Path, default=[])
    parser.add_argument("--builds", default=",".join(ALL_BUILDS))
    parser.add_argument("--min-size", type=int, default=16)
    parser.add_argument("--config", type=Path, default=ROOT / "config" / "jpn" / "config.toml")
    parser.add_argument("--json", type=Path, help="write the per-function results here")
    parser.add_argument("-j", "--jobs", type=int, default=os.cpu_count() or 4)
    args = parser.parse_args()

    if args.project:
        project = args.project.resolve()
        units = project_objects(project)
        includes = [project / "include", project / "src", *args.includes]
    else:
        units = [(s.resolve(), shlex.split(args.flags)) for s in args.sources]
        includes = args.includes
    if args.filter:
        units = [u for u in units if any(f in u[0].as_posix() for f in args.filter)]
    units = [u for u in units if u[0].is_file()]
    if not units:
        sys.exit("no sources")

    config = VersionConfig(args.config)
    image = Image.load(config)
    text = config.section(".text")
    text_bytes = image.read(text.address, text.size)

    builds = [b.strip() for b in args.builds.split(",") if b.strip()]
    results: Dict[str, Dict[str, object]] = {}  # function -> build -> address | "ambiguous" | "conflict" | None
    failures: Dict[str, int] = {}

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for build in builds:
            armcc = armcc_path(build)
            outdir = tmp / build.replace("/", "_")
            outdir.mkdir()

            def work(i_unit):
                i, (source, flags) = i_unit
                out = outdir / f"{i}.o"
                err = compile_one(armcc, source, flags, includes, out)
                if err:
                    return source, err, []
                found = []
                for name, thumb, data, mask in functions_of(out, args.min_size):
                    hits = find(text_bytes, text.address, data, mask, thumb)
                    found.append((name, len(data), hits))
                return source, None, found

            failed = 0
            with ThreadPoolExecutor(args.jobs) as pool:
                for source, err, found in pool.map(work, enumerate(units)):
                    if err:
                        if not failed:
                            print(f"  first failure: {source.name}: {err}", flush=True)
                        failed += 1
                        continue
                    for name, size, hits in found:
                        entry = results.setdefault(name, {"size": size, "source": str(source), "sizes": {}})
                        new = f"0x{hits[0]:08X}" if len(hits) == 1 else "ambiguous" if hits else None
                        # Several sources can define one name (inline and template copies,
                        # static functions): keep a hit, and flag two different ones
                        old = entry.get(build)
                        if old is not None and new != old:
                            if new is None:
                                continue
                            if old != "ambiguous" and new != "ambiguous":
                                new = "conflict"
                        # The size can differ between builds; "size" is the first one seen
                        entry["sizes"][build] = size
                        entry.setdefault("sources", {})[build] = str(source)
                        entry[build] = new
            failures[build] = failed
            matched = sum(1 for r in results.values() if isinstance(r.get(build), str) and r[build].startswith("0x"))
            print(f"{build:10} {matched:5} functions found ({failed} sources failed to compile)", flush=True)

    # Functions that tell builds apart
    found_any = {n: r for n, r in results.items()
                 if any(isinstance(r.get(b), str) and r[b].startswith("0x") for b in builds)}
    print(f"\n{len(found_any)} functions found with at least one build, of {len(results)} compiled")
    discriminating = {n: r for n, r in found_any.items()
                      if not all(isinstance(r.get(b), str) and r[b].startswith("0x") for b in builds)}
    print(f"{len(discriminating)} of them are not found with every build:")
    for name, r in sorted(discriminating.items(), key=lambda kv: kv[1]["source"]):
        yes = [b for b in builds if isinstance(r.get(b), str) and r[b].startswith("0x")]
        addr = r[yes[0]]
        print(f"  {addr} {name} ({r['size']} bytes, {Path(r['source']).name}): {' '.join(yes)}")
    if args.json:
        args.json.write_text(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
