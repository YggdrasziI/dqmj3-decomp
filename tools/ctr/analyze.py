#!/usr/bin/env python3
"""
Bootstraps symbols.txt from the original code image.

This discovers function boundaries (and the ARM/Thumb state of each function) by
walking control flow, then labels every piece of data that code or other data points
at. It only ever needs to run when starting a new version from scratch: the result
is checked in as config/<version>/symbols.txt and maintained by hand from then on.

Existing symbols are preserved: names, sizes and types already present in
symbols.txt win over anything the analysis comes up with. With --regenerate only
symbols that were given a name are preserved, which is the way to pick up
improvements to the analysis itself.

Usage:
    python tools/ctr/analyze.py config/jpn/config.toml [--dry-run] [--regenerate]
"""

import argparse
import bisect
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ctr import arm
from ctr.image import Image, VersionConfig
from ctr.symbols import TYPE_FUNCTION, TYPE_OBJECT, SplitRange, Splits, Symbol, SymbolTable

ENTRY_NAME = "__ctr_start"
AUTO_NAME = re.compile(r"^(?:(?:fn|lbl)_[0-9A-F]{8}|__ctr_start)$")


def is_arm_terminator(insn: int) -> bool:
    """An instruction that never falls through to the next one."""
    if arm.arm_cond(insn) != arm.COND_AL:
        return False
    return (
        arm.arm_is_b(insn)
        or arm.arm_is_bx(insn)
        or arm.arm_is_ldm_pc(insn)
        or arm.arm_is_load_to_pc(insn)
        or arm.arm_dp_writes_pc(insn)
    )


def is_thumb_prologue(insn: int) -> bool:
    """push {..., lr} (0xB5xx) or push {...} (0xB4xx)"""
    return (insn & 0xFE00) == 0xB400


def is_arm_prologue(insn: int) -> bool:
    """push {..., lr}"""
    return (insn & 0xFFFF4000) == 0xE92D4000


class Discovery:
    """
    Finds function boundaries.

    Calls are the only fully trustworthy evidence of a function entry, but most of the
    game is only reachable through vtables, and treating every word in the data
    sections that happens to look like a code address as a pointer drowns the result
    in noise. Instead the text section is tiled: starting at the entry point, each
    function's extent is derived from its own control flow (the instructions it can
    reach plus the literal pools, jump tables and inline strings it references), and
    whatever follows it is the next function.
    """

    def __init__(self, image: Image) -> None:
        self.image = image
        self.config = image.config
        self.text = self.config.section(".text")
        # Function entry -> is Thumb
        self.functions: Dict[int, bool] = {}
        self.starts: List[int] = []
        self.infos: Dict[int, arm.FunctionInfo] = {}
        self.dirty: Set[int] = set()
        self.analyzer = arm.Analyzer(
            image.u32, image.u16, self.text.address, self.text.end, self.is_function
        )

    def is_function(self, addr: int) -> bool:
        return addr in self.functions

    def in_text(self, addr: int) -> bool:
        return self.text.address <= addr < self.text.end

    def add_function(self, addr: int, thumb: bool) -> bool:
        if addr in self.functions or not self.in_text(addr):
            return False
        if addr & (1 if thumb else 3):
            return False
        self.functions[addr] = thumb
        i = bisect.bisect_left(self.starts, addr)
        self.starts.insert(i, addr)
        self.dirty.add(addr)
        # The function that used to cover this address now ends earlier
        if i > 0:
            self.dirty.add(self.starts[i - 1])
        return True

    def limit_of(self, addr: int) -> int:
        i = bisect.bisect_right(self.starts, addr)
        return self.starts[i] if i < len(self.starts) else self.text.end

    def owner_of(self, addr: int) -> Optional[int]:
        i = bisect.bisect_right(self.starts, addr) - 1
        return self.starts[i] if i >= 0 else None

    def settle(self) -> None:
        """Analyze until no function is out of date, following every call found."""
        while self.dirty:
            addr = self.dirty.pop()
            info = self.analyzer.analyze(addr, self.limit_of(addr), self.functions[addr])
            self.infos[addr] = info
            for ref in info.branches:
                if ref.kind == arm.KIND_CALL:
                    self.add_function(ref.target, ref.target_thumb)
                elif not self.is_reached_midway(ref.target):
                    # A branch out of the function is a tail call
                    self.add_function(ref.target, ref.target_thumb)
            if not info.thumb:
                self.split_at_prologues(info)
                self.split_at_tail_calls(info)

    def split_at_prologues(self, info: arm.FunctionInfo) -> None:
        """
        `push {..., lr}` right after a call can only be the start of the next function:
        the function that made the call (which does not return) already saved lr.
        """
        for addr in info.code:
            if addr == info.start or not is_arm_prologue(self.image.u32(addr)):
                continue
            prev = self.image.u32(addr - 4)
            if (addr - 4) in info.code and arm.arm_is_bl(prev) and arm.arm_cond(prev) == arm.COND_AL:
                self.add_function(addr, False)

    def split_at_tail_calls(self, info: arm.FunctionInfo) -> None:
        """
        armlink puts a function that is tail called right behind its caller where it
        can, and then overwrites the branch between them with `mov r0, r0`. The same
        instruction also replaces calls to empty functions, but a call needs lr to be
        saved, so the two can be told apart: after the epilogue has restored lr, or
        before the function has saved it, it can only have been a tail call.
        """
        saved_lr = False
        restored_lr = False  # lr popped and no branch seen since: a tail call is next
        for addr in sorted(info.code):
            insn = self.image.u32(addr)
            if arm.arm_saves_lr(insn):
                saved_lr, restored_lr = True, False
            elif arm.arm_restores_lr(insn):
                restored_lr = True
            elif (insn >> 25) & 7 == 5 or arm.arm_is_bx(insn) or arm.arm_dp_writes_pc(insn):
                restored_lr = False
            if insn != arm.ARM_MOV_R0_R0 or addr + 4 >= info.limit:
                continue
            if restored_lr or not saved_lr:
                self.add_function(addr + 4, False)
                break

    def is_reached_midway(self, addr: int) -> bool:
        """`addr` is an instruction of a known function that its predecessor falls into."""
        owner = self.owner_of(addr)
        if owner is None or owner == addr:
            return False
        info = self.infos.get(owner)
        if info is None or addr not in info.code:
            return False
        step = 2 if info.thumb else 4
        prev = addr - step
        if prev not in info.code:
            return False
        if info.thumb:
            insn = self.image.u16(prev)
            return not (
                arm.thumb_is_b(insn) or arm.thumb_is_pop_pc(insn) or arm.thumb_is_bx(insn)
            )
        return not is_arm_terminator(self.image.u32(prev))

    def string_words(self, info: arm.FunctionInfo) -> Set[int]:
        """Words occupied by NUL-terminated strings the function addresses with `adr`."""
        words: Set[int] = set()
        for target in info.adr_targets:
            if target in info.code:
                continue
            cur = target
            while cur < info.limit and self.image.u8(cur) != 0:
                cur += 1
            words.update(range(target & ~3, min(info.limit, cur + 1), 4))
        return words

    def extent(self, info: arm.FunctionInfo) -> int:
        """
        End of the contiguous run of code and data the function owns. Everything a
        function reaches is laid out without gaps, so the first word that is neither
        is normally where the next function begins.

        The exception is a data island: a table in the middle of a function that is
        addressed relative to pc and branched over. Those are recognised by not being
        decodable as a function of their own.
        """
        strings = self.string_words(info)
        data = info.data_words
        step = 2 if info.thumb else 4
        code_addrs = sorted(info.code)
        addr = info.start
        while addr < info.limit:
            if addr in info.code:
                addr += step
            elif (addr & ~3) in data or (addr & ~3) in strings:
                addr = (addr & ~3) + 4
            elif (
                info.thumb
                and addr & 2
                and self.image.u16(addr) == 0
                and ((addr + 2) in data or (addr + 2) in strings)
            ):
                addr += 2  # literal pool alignment
            else:
                i = bisect.bisect_right(code_addrs, addr)
                if i == len(code_addrs):
                    break
                resume = code_addrs[i]
                trial = self.analyzer.analyze(addr, resume, info.thumb)
                if trial.code and not trial.suspicious and self.image.u32(addr & ~3) != 0:
                    break
                addr = resume
        return min(addr, info.limit)

    def guess_thumb(self, addr: int, prev_thumb: bool) -> bool:
        """
        Decide between ARM and Thumb for code nothing calls directly.

        Thumb code read as ARM words has an effectively random condition field, so it
        rarely survives decoding and is conditional far more often than compiled ARM
        code. Hand-written ARM assembly in the C library is heavily conditional too,
        so a function following ARM code is only taken to be Thumb on hard evidence.
        """
        if addr & 3:
            return True
        limit = self.limit_of(addr)
        as_arm = self.analyzer.analyze(addr, limit, False)
        as_thumb = self.analyzer.analyze(addr, limit, True)
        arm_ok = bool(as_arm.code) and not as_arm.suspicious
        thumb_ok = bool(as_thumb.code) and not as_thumb.suspicious
        if arm_ok != thumb_ok:
            if thumb_ok and not prev_thumb and not is_thumb_prologue(self.image.u16(addr)):
                # Data islands in .text (pointer tables, UTF-16 strings) decode as
                # plausible Thumb. After ARM code, only a Thumb prologue is evidence.
                return False
            return thumb_ok
        if not arm_ok:
            return prev_thumb
        if not prev_thumb:
            return False
        always = sum(1 for a in as_arm.code if arm.arm_cond(self.image.u32(a)) == arm.COND_AL)
        return always * 2 < len(as_arm.code)

    def is_thumb_entry_veneer(self, start: int) -> bool:
        """`add ip, pc, #1; bx ip`: the ARM-state entry of the Thumb function that follows."""
        return (
            not self.functions[start]
            and start + 8 <= self.text.end
            and self.image.u32(start) == 0xE28FC001
            and self.image.u32(start + 4) == 0xE12FFF1C
        )

    def next_function(self, prev: int, addr: int) -> Tuple[int, bool]:
        """Find where the function after `prev` starts and which state it is in."""
        prev_thumb = self.functions[prev]
        if addr in self.functions:
            return addr, self.functions[addr]
        if self.is_thumb_entry_veneer(prev) and addr == prev + 8:
            return addr, True
        if prev_thumb and addr & 2:
            if self.image.u16(addr) in (0x0000, 0xFFFF):
                # Padding up to the alignment of an ARM function
                addr += 2
                if addr in self.functions:
                    return addr, self.functions[addr]
                return addr, self.guess_thumb(addr, False)
            return addr, True
        if not prev_thumb:
            addr = (addr + 3) & ~3
            while addr < self.text.end and self.image.u32(addr) == 0:
                addr += 4
        if addr >= self.text.end or addr in self.functions:
            return addr, self.functions.get(addr, False)
        return addr, self.guess_thumb(addr, prev_thumb)

    def run(self) -> None:
        self.add_function(self.text.address, False)
        self.settle()
        print(f"  call graph from the entry point: {len(self.functions)} functions")

        prev = self.text.address
        addr, thumb = prev, False
        while addr < self.text.end:
            if addr not in self.functions:
                trial = self.analyzer.analyze(addr, self.limit_of(addr), thumb)
                if trial.suspicious or not trial.code:
                    # Not code: a table or other data island that belongs to the
                    # previous function. Keep looking for where code resumes.
                    addr += 2 if thumb else 4
                    if addr in self.functions:
                        thumb = self.functions[addr]
                    continue
            self.add_function(addr, thumb)
            self.settle()
            prev = addr
            end = self.extent(self.infos[addr])
            addr, thumb = self.next_function(prev, max(end, addr + (2 if thumb else 4)))
        print(f"  tiling .text: {len(self.functions)} functions")

    def function_size(self, start: int) -> int:
        info = self.infos[start]
        limit = info.limit
        end = self.extent(info)
        # Leave alignment padding between functions out of the symbol
        if end < limit and limit - end < 4:
            pad = self.image.read(end, limit - end)
            if all(b in (0x00, 0xFF) for b in pad):
                return end - start
        return limit - start


def discover_data(image: Image, disc: Discovery, owned: List[SplitRange]) -> Set[int]:
    """
    Addresses in the data sections that are referenced from code or from other data.

    Nothing is labelled inside the ranges that units own (`owned`). What is in there
    is up to the unit, and data without a symbol, such as a long string literal, has
    to stay that way.
    """
    config = image.config
    data_sections = [s for s in config.sections if s.kind != "code"]
    lo = min(s.address for s in data_sections)
    hi = max(s.end for s in data_sections)
    labels: Set[int] = set()

    def consider(value: int) -> None:
        # Strings in the merged pools are not symbols: they are found by their contents
        if lo <= value < hi and config.section_at(value) is not None:
            if config.string_pool_at(value) is None and not any(r.contains(value) for r in owned):
                labels.add(value)

    for info in disc.infos.values():
        for addr, size in info.pool.items():
            if size == 4:
                consider(image.u32(addr))
    for section in data_sections:
        if section.kind == "bss":
            continue
        for addr in range(section.address, section.end - 3, 4):
            if config.string_pool_at(addr) is not None:
                continue
            value = image.u32(addr)
            if value & 3 == 0:
                consider(value)
    for section in data_sections:
        labels.add(section.address)
    for pool in config.string_pools:
        # Whatever follows a pool starts a new object
        after = (pool.end + 3) & ~3
        consider(after)
    return labels


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    parser.add_argument("config", type=Path, help="path to config.toml")
    parser.add_argument("--dry-run", action="store_true", help="do not write symbols.txt")
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="discard every automatically named symbol and analyze again, keeping the named ones",
    )
    args = parser.parse_args()

    config = VersionConfig(args.config)
    image = Image.load(config)

    existing = SymbolTable.load(config.symbols_path) if config.symbols_path.is_file() else SymbolTable()
    if args.regenerate:
        existing = SymbolTable(s for s in existing if not AUTO_NAME.match(s.name))

    print("Discovering functions...")
    disc = Discovery(image)
    for sym in existing:
        if sym.is_function:
            disc.add_function(sym.address, sym.thumb)
    disc.run()

    symbols: Dict[int, Symbol] = {}
    kept: List[Symbol] = list(existing)  # every existing symbol survives, aliases included
    for sym in existing:
        symbols.setdefault(sym.address, sym)

    text = config.section(".text")
    thumb_count = 0
    for start in disc.starts:
        thumb = disc.functions[start]
        thumb_count += thumb
        if start in symbols:
            continue
        name = ENTRY_NAME if start == text.address else f"fn_{start:08X}"
        symbols[start] = Symbol(
            name, ".text", start, TYPE_FUNCTION, disc.function_size(start), "global", thumb
        )

    print("Labelling data...")
    owned: List[SplitRange] = []
    if config.splits_path.is_file():
        for unit in Splits.load(config.splits_path).units:
            owned += [r for r in unit.ranges if config.section(r.section).kind != "code"]
    # Data that already has a name is not labelled again either
    for sym in existing:
        if not sym.is_function and sym.size and not AUTO_NAME.match(sym.name):
            owned.append(SplitRange(sym.section, sym.address, sym.end))
    boundaries = sorted({r.start for r in owned} | {r.end for r in owned})
    labels = sorted(discover_data(image, disc, owned))
    for i, addr in enumerate(labels):
        if addr in symbols:
            continue
        section = config.section_at(addr)
        assert section is not None
        end = section.end
        if i + 1 < len(labels) and labels[i + 1] < end:
            end = labels[i + 1]
        for pool in config.string_pools:
            if addr < pool.address < end:
                end = pool.address
        for boundary in boundaries:
            if addr < boundary < end:
                end = boundary
        symbols[addr] = Symbol(f"lbl_{addr:08X}", section.name, addr, TYPE_OBJECT, end - addr, "global")

    table = SymbolTable(kept + [s for a, s in symbols.items() if s not in kept])
    functions = [s for s in table if s.is_function]
    code_bytes = sum(s.size for s in functions)
    suspicious = sum(1 for info in disc.infos.values() if info.suspicious)
    print(
        f"{len(functions)} functions ({thumb_count} Thumb) covering "
        f"{code_bytes / text.size:.2%} of .text, {len(table) - len(functions)} data symbols"
    )
    if suspicious:
        print(f"{suspicious} functions have control flow that could not be followed cleanly")

    if not args.dry_run:
        table.save(config.symbols_path)
        print(f"Wrote {config.symbols_path}")


if __name__ == "__main__":
    main()
