#!/usr/bin/env python3
"""
Splits the original code image into one relocatable object per translation unit.

These objects are what decompiled code is compared against in objdiff. To make that
comparison meaningful they are shaped like the objects armcc produces:

  - every function lives in its own `i.<name>` section (armcc --split_sections)
  - calls, literal pool entries and switch tables are turned back into relocations
    against named symbols, so that code can be compared independent of where the
    linker placed things
  - `$a`/`$t`/`$d` mapping symbols mark code and data inside functions
  - a pointer into one of the merged string pools becomes a reference to a
    `.conststring` section that holds just the strings the data refers to

The objects are never linked. The link step (link.py) takes the bytes of everything
that is not decompiled straight from the original image.

Usage:
    python tools/ctr/split.py config/jpn/config.toml -o build/jpn/delink
"""

import argparse
import struct
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ctr import arm, elf
from ctr.image import Image, VersionConfig
from ctr.strpool import StringPool
from ctr.symbols import TYPE_FUNCTION, TYPE_OBJECT, SplitRange, Splits, Symbol, SymbolTable, Unit
from ctr.units import object_name, resolve_units

# Names armcc gives the sections it puts data in
DATA_SECTION_NAMES = {"rodata": ".constdata", "data": ".data", "bss": ".bss"}
DATA_SECTION_FLAGS = {
    "rodata": elf.SHF_ALLOC,
    "data": elf.SHF_ALLOC | elf.SHF_WRITE,
    "bss": elf.SHF_ALLOC | elf.SHF_WRITE,
}

SWITCH_SYMBOL = "__switch$$"
INIT_ARRAY = ".init_array"
VTABLE_PREFIX = "_ZTV"


def arm_branch_with_addend(insn: int, addend: int) -> int:
    """Re-encode a B/BL so it holds `addend` the way a REL relocation expects."""
    return (insn & 0xFF000000) | (((addend - 8) >> 2) & 0x00FFFFFF)


def thumb_bl_with_addend(addend: int) -> Tuple[int, int]:
    offset = addend - 4
    return 0xF000 | ((offset >> 12) & 0x7FF), 0xF800 | ((offset >> 1) & 0x7FF)


class StringSection:
    """
    Rebuilds the string section of a compiled object from pointers into a merged pool:
    every distinct string once, in the order the data refers to them.
    """

    def __init__(self, writer: elf.ElfWriter, pool: StringPool) -> None:
        self.pool = pool
        self.section = writer.add_section(
            elf.Section(
                pool.name,
                elf.SHT_PROGBITS,
                elf.SHF_ALLOC | elf.SHF_MERGE | elf.SHF_STRINGS,
                align=pool.char_size,
                entsize=pool.char_size,
            )
        )
        self.symbol = writer.add_symbol(
            elf.Symbol(pool.name, type=elf.STT_SECTION, shndx=self.section.index)
        )
        self.offsets: Dict[bytes, int] = {}
        self.data = bytearray()

    def add(self, contents: bytes) -> int:
        offset = self.offsets.get(contents)
        if offset is None:
            offset = self.offsets[contents] = len(self.data)
            self.data += contents + bytes(self.pool.char_size)
        return offset

    def finish(self) -> None:
        self.section.data = bytes(self.data)


def own_inline_string_addend(image, info, start: int, end: int, value: int):
    """Recognize an ADR-proven string inside this function, never a code label."""
    if not start <= value < end or value not in info.adr_targets:
        return None
    contents = image.read(value, end - value)
    terminator = contents.find(b'\0')
    if terminator <= 0 or any(not 32 <= byte <= 126 for byte in contents[:terminator]):
        return None
    step = 2 if info.thumb else 4
    if any(addr in info.code for addr in range(value & ~(step - 1), value + terminator + 1, step)):
        return None
    return value - start


class Splitter:
    def __init__(self, config: VersionConfig, image: Image, symbols: SymbolTable) -> None:
        self.config = config
        self.image = image
        self.symbols = symbols
        self.text = config.section(".text")
        self.function_addrs = {s.address for s in symbols if s.is_function}
        self.string_pools = [StringPool(image, pool) for pool in config.string_pools]
        # Ranges of the unit being built, and the section symbols of its data sections
        self.unit_ranges: List[SplitRange] = []
        self.range_symbols: Dict[int, elf.Symbol] = {}
        self.analyzer = arm.Analyzer(
            image.u32,
            image.u16,
            self.text.address,
            self.text.end,
            lambda addr: addr in self.function_addrs,
        )

    def string_literal_at(self, value: int) -> Optional[Tuple[StringPool, bytes]]:
        """
        The pool and contents of the string literal a word points to. A pointer that
        armlink's rule (StringPool.locate) would not reproduce, or one into padding,
        is left to be resolved like any other pointer.
        """
        for pool in self.string_pools:
            if pool.contains(value):
                contents = pool.string_at(value)
                if contents is not None and pool.locate(contents) == value:
                    return pool, contents
                return None
        return None

    def resolve_pointer(self, value: int) -> Optional[Tuple[Union[Symbol, SplitRange], int]]:
        """Symbol and addend a word refers to, if it looks like an address."""
        if self.text.contains(value & ~1):
            sym = self.symbols.first_at(value & ~1)
            if sym is not None and sym.is_function and sym.thumb == bool(value & 1):
                return sym, 0
            return None
        section = self.config.section_at(value)
        if section is None or section.kind == "code":
            return None
        sym = self.symbols.containing(value)
        if sym is not None:
            return sym, value - sym.address
        # Data without a symbol, such as a long string literal. The compiler refers
        # to that relative to the section it is in.
        for rng in self.unit_ranges:
            if rng.contains(value) and rng.section == section.name:
                return rng, value - rng.start
        return None

    def build(self, unit: Unit) -> elf.ElfWriter:
        writer = elf.ElfWriter()
        defined: Dict[Tuple[str, int], elf.Symbol] = {}

        def bind_of(sym: Symbol) -> int:
            return {"local": elf.STB_LOCAL, "weak": elf.STB_WEAK}.get(sym.scope, elf.STB_GLOBAL)

        def reference(sym: Symbol) -> elf.Symbol:
            local = defined.get((sym.name, sym.address))
            if local is not None:
                return local
            return writer.undefined(sym.name, elf.STT_FUNC if sym.is_function else elf.STT_OBJECT)

        pending = []  # relocations are resolved once every symbol of the unit is defined
        # Data ranges are cut up so that every vtable gets a section of its own
        pieces: List[Tuple[SplitRange, Optional[str]]] = []
        for rng in sorted(unit.ranges, key=lambda r: r.start):
            if self.config.section(rng.section).kind == "code":
                pieces.append((rng, None))
            else:
                pieces += self.data_pieces(rng)
        self.unit_ranges = [piece for piece, _ in pieces]
        self.range_symbols = {}

        for rng, section_name in pieces:
            section = self.config.section(rng.section)
            if section.kind == "code":
                in_range = self.symbols.in_range(rng.start, rng.end)
                emitted: Dict[int, elf.Symbol] = {}
                for sym in in_range:
                    if not sym.size:
                        continue
                    if sym.end > rng.end:
                        raise ValueError(
                            f"{unit.name}: {sym.name} [0x{sym.address:08X}, 0x{sym.end:08X}) "
                            f"extends past the end of its range at 0x{rng.end:08X}"
                        )
                    if sym.is_function:
                        self.emit_function(writer, sym, defined, pending, bind_of(sym))
                    else:
                        self.emit_text_data(writer, sym, defined, bind_of(sym))
                    emitted[sym.address] = defined[(sym.name, sym.address)]
                # A function symbol without a size is another name for the function at
                # its address. The compiler emits constructors and destructors like
                # that: one body, and a second symbol that has no size.
                for sym in in_range:
                    first = emitted.get(sym.address)
                    if sym.size or not sym.is_function or first is None:
                        continue
                    defined[(sym.name, sym.address)] = writer.add_symbol(
                        elf.Symbol(sym.name, first.value, 0, bind_of(sym), elf.STT_FUNC, shndx=first.shndx)
                    )
            else:
                self.emit_data(writer, section.kind, rng, defined, pending, bind_of, section_name)

        for out_section, offset, rtype, target in pending:
            if isinstance(target, SplitRange):
                symbol = self.range_symbols[target.start]
            else:
                symbol = reference(target)
            out_section.relocs.append(elf.Reloc(offset, rtype, symbol))
        return writer

    def emit_function(self, writer, sym: Symbol, defined, pending, bind: int) -> None:
        start, end = sym.address, sym.end
        info = self.analyzer.analyze(start, end, sym.thumb)
        data = bytearray(self.image.read(start, end - start))
        section = writer.add_section(
            elf.Section(
                "i." + sym.name,
                elf.SHT_PROGBITS,
                elf.SHF_ALLOC | elf.SHF_EXECINSTR,
                align=2 if sym.thumb and start & 2 else 4,
            )
        )
        index = section.index

        # Mapping symbols
        step = 2 if sym.thumb else 4
        code_marker = "$t" if sym.thumb else "$a"
        state = None
        addr = start
        while addr < end:
            kind = code_marker if addr in info.code else "$d"
            if kind != state:
                writer.add_symbol(elf.Symbol(kind, addr - start, shndx=index))
                state = kind
            addr += step

        # armcc excludes a trailing pool only when it contains solely LDR
        # literals. Mixed pools (for example inline strings or VFP constants)
        # remain part of the function symbol, even if they end in LDR literals.
        size_end = end
        code_end = max(info.code, default=start - step) + step
        pool_start = (code_end + 3) & ~3
        if pool_start < end and all(addr in info.ldr_pool for addr in range(pool_start, end, 4)):
            while size_end - 4 >= start and (size_end - 4) in info.ldr_pool:
                size_end -= 4
        if sym.thumb and size_end < end and size_end - 2 >= start:
            if (size_end - 2) not in info.code and self.image.u16(size_end - 2) == 0:
                size_end -= 2  # pool alignment

        defined[(sym.name, sym.address)] = writer.add_symbol(
            elf.Symbol(
                sym.name,
                1 if sym.thumb else 0,
                size_end - start,
                bind,
                elf.STT_FUNC,
                shndx=index,
            )
        )

        # Calls and tail calls
        for ref in info.branches:
            target = self.symbols.first_at(ref.target)
            if target is None or not target.is_function:
                continue
            off = ref.addr - start
            if ref.thumb:
                if ref.kind != arm.KIND_CALL:
                    continue
                hi, lo = thumb_bl_with_addend(0)
                struct.pack_into("<HH", data, off, hi, lo)
                pending.append((section, off, elf.R_ARM_THM_CALL, target))
            else:
                insn = self.image.u32(ref.addr)
                if arm.arm_is_blx_imm(insn):
                    # The linker turned `bl` into `blx` because the callee is Thumb
                    insn = 0xEB000000
                struct.pack_into("<I", data, off, arm_branch_with_addend(insn, 0))
                # Only an unconditional call gets R_ARM_CALL: a linker may not turn a
                # conditional `bl` into `blx`.
                unconditional = arm.arm_cond(insn) == arm.COND_AL
                if ref.kind == arm.KIND_CALL and unconditional:
                    rtype = elf.R_ARM_CALL
                else:
                    rtype = elf.R_ARM_JUMP24
                pending.append((section, off, rtype, target))

        # A tail call to the function that follows: armlink overwrote the branch
        last = end - 4
        if not sym.thumb and last in info.code and self.image.u32(last) == arm.ARM_MOV_R0_R0:
            target = self.symbols.first_at(end)
            if target is not None and target.is_function and not target.thumb:
                struct.pack_into("<I", data, last - start, arm_branch_with_addend(0xEA000000, 0))
                pending.append((section, last - start, elf.R_ARM_JUMP24, target))

        # Literal pool entries holding addresses
        own_section_symbol = None
        for addr in info.ldr_pool:
            value = self.image.u32(addr)
            resolved = self.resolve_pointer(value)
            if resolved is None:
                addend = own_inline_string_addend(self.image, info, start, end, value)
                if addend is not None:
                    if own_section_symbol is None:
                        own_section_symbol = writer.add_symbol(
                            elf.Symbol(section.name, type=elf.STT_SECTION, shndx=index))
                    struct.pack_into("<I", data, addr - start, addend)
                    section.relocs.append(elf.Reloc(addr - start, elf.R_ARM_ABS32, own_section_symbol))
                continue
            target, addend = resolved
            struct.pack_into("<I", data, addr - start, addend)
            pending.append((section, addr - start, elf.R_ARM_ABS32, target))

        # Switch tables hold absolute addresses of code in the same function
        for sw in info.switches:
            label = writer.add_symbol(
                elf.Symbol(SWITCH_SYMBOL, sw.label - start, type=elf.STT_FUNC, shndx=index)
            )
            for i in range(sw.count):
                entry = sw.table + i * 4
                addend = (self.image.u32(entry) - sw.label) & 0xFFFFFFFF
                struct.pack_into("<I", data, entry - start, addend)
                section.relocs.append(elf.Reloc(entry - start, elf.R_ARM_ABS32, label))

        section.data = bytes(data)

    def emit_text_data(self, writer, sym: Symbol, defined, bind: int) -> None:
        """Data that lives in .text without belonging to a function."""
        section = writer.add_section(
            elf.Section(
                ".text",
                elf.SHT_PROGBITS,
                elf.SHF_ALLOC | elf.SHF_EXECINSTR,
                data=self.image.read(sym.address, sym.size),
                align=4,
            )
        )
        writer.add_symbol(elf.Symbol("$d", 0, shndx=section.index))
        defined[(sym.name, sym.address)] = writer.add_symbol(
            elf.Symbol(sym.name, 0, sym.size, bind, elf.STT_OBJECT, shndx=section.index)
        )

    def data_pieces(self, rng: SplitRange) -> List[Tuple[SplitRange, Optional[str]]]:
        """
        Parts of a data range that the compiler emits as separate sections, with the
        name of the section. Vtables are in `.constdata__ZTV<class>`.
        """
        init_array = self.config.init_array
        if init_array is not None and rng.start < init_array.end and init_array.address < rng.end:
            # The static initializer table: armcc emits each file's entry in .init_array
            lo, hi = max(rng.start, init_array.address), min(rng.end, init_array.end)
            pieces = []
            for part, name in (
                (SplitRange(rng.section, rng.start, lo), None),
                (SplitRange(rng.section, lo, hi), INIT_ARRAY),
                (SplitRange(rng.section, hi, rng.end), None),
            ):
                if part.end > part.start:
                    pieces += [(part, name)] if name else self.data_pieces(part)
            return pieces
        pieces: List[Tuple[SplitRange, Optional[str]]] = []
        cursor = rng.start
        for sym in self.symbols.in_range(rng.start, rng.end):
            if not sym.name.startswith(VTABLE_PREFIX) or not sym.size or sym.end > rng.end:
                continue
            if sym.address < cursor:
                continue
            if sym.address > cursor:
                pieces.append((SplitRange(rng.section, cursor, sym.address), None))
            pieces.append((SplitRange(rng.section, sym.address, sym.end), ".constdata_" + sym.name))
            cursor = sym.end
        if cursor < rng.end:
            pieces.append((SplitRange(rng.section, cursor, rng.end), None))
        return pieces

    def emit_init_array(self, writer, rng: SplitRange, pending) -> None:
        """
        Entries of the static initializer table, as the compiler emits them: a word of 0
        with an R_ARM_TARGET1 relocation against the initializer. armlink wrote the
        offset from the entry to the function instead (see linker.py).
        """
        section = elf.Section(INIT_ARRAY, elf.SHT_INIT_ARRAY, elf.SHF_ALLOC, align=4)
        data = bytearray(rng.end - rng.start)
        for addr in range(rng.start, rng.end - 3, 4):
            target = (addr + struct.unpack_from("<I", self.image.read(addr, 4))[0]) & 0xFFFFFFFF
            resolved = self.resolve_pointer(target)
            if resolved is None or resolved[1]:
                raise ValueError(f"{INIT_ARRAY} entry at 0x{addr:08X} points to 0x{target:08X}, "
                                 "which is not the start of a function in symbols.txt")
            pending.append((section, addr - rng.start, elf.R_ARM_TARGET1, resolved[0]))
        section.data = bytes(data)
        writer.add_section(section)
        writer.add_symbol(elf.Symbol("$d", 0, shndx=section.index))

    def emit_data(
        self, writer, kind: str, rng: SplitRange, defined, pending, bind_of, name: Optional[str] = None
    ) -> None:
        size = rng.end - rng.start
        if name == INIT_ARRAY:
            self.emit_init_array(writer, rng, pending)
            return
        section = elf.Section(
            name or DATA_SECTION_NAMES[kind],
            elf.SHT_NOBITS if kind == "bss" else elf.SHT_PROGBITS,
            DATA_SECTION_FLAGS[kind],
            align=4,
        )
        if kind == "bss":
            section.size = size
        else:
            data = bytearray(self.image.read(rng.start, size))
            data += b"\0" * (size - len(data))
        writer.add_section(section)
        self.range_symbols[rng.start] = writer.add_symbol(
            elf.Symbol(section.name, type=elf.STT_SECTION, shndx=section.index)
        )

        for sym in self.symbols.in_range(rng.start, rng.end):
            typ = elf.STT_NOTYPE
            if sym.type == TYPE_OBJECT:
                typ = elf.STT_OBJECT
            elif sym.type == TYPE_FUNCTION:
                typ = elf.STT_FUNC
            defined[(sym.name, sym.address)] = writer.add_symbol(
                elf.Symbol(
                    sym.name,
                    sym.address - rng.start,
                    min(sym.size, rng.end - sym.address),
                    bind_of(sym),
                    typ,
                    shndx=section.index,
                )
            )

        if kind == "bss":
            return
        # String sections the compiler would have emitted next to this data
        strings: Dict[str, StringSection] = {}
        first = (rng.start + 3) & ~3
        for addr in range(first, rng.end - 3, 4):
            off = addr - rng.start
            value = struct.unpack_from("<I", data, off)[0]
            literal = self.string_literal_at(value)
            if literal is not None:
                pool, contents = literal
                literals = strings.get(pool.name)
                if literals is None:
                    literals = strings[pool.name] = StringSection(writer, pool)
                struct.pack_into("<I", data, off, literals.add(contents))
                section.relocs.append(elf.Reloc(off, elf.R_ARM_ABS32, literals.symbol))
                continue
            resolved = self.resolve_pointer(value)
            if resolved is None:
                continue
            target, addend = resolved
            struct.pack_into("<I", data, off, addend)
            pending.append((section, off, elf.R_ARM_ABS32, target))
        section.data = bytes(data)
        for literals in strings.values():
            literals.finish()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    parser.add_argument("config", type=Path, help="path to config.toml")
    parser.add_argument("-o", "--out", type=Path, required=True, help="output directory")
    parser.add_argument("--stamp", type=Path, help="file to touch when done")
    args = parser.parse_args()

    config = VersionConfig(args.config)
    image = Image.load(config)
    try:
        symbols = SymbolTable.load(config.symbols_path)
        splits = Splits.load(config.splits_path)
        units = resolve_units(config, splits, symbols)
    except ValueError as e:
        raise SystemExit(f"error: {e}")

    splitter = Splitter(config, image, symbols)
    written = 0
    for unit in units:
        try:
            writer = splitter.build(unit)
        except ValueError as e:
            raise SystemExit(f"error: {e}")
        written += writer.write(args.out / object_name(unit))
    if args.stamp:
        args.stamp.parent.mkdir(parents=True, exist_ok=True)
        args.stamp.write_text("")
    print(f"Split {config.object} into {len(units)} units ({written} updated)")


if __name__ == "__main__":
    main()
