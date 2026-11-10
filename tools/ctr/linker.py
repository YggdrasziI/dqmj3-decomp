"""
Fixed-address linking of armcc objects.

The original game was linked with armlink, which is not available. Rather than lay
the program out from scratch, this linker puts every section of a compiled object at
the address symbols.txt gives the symbols it defines, and resolves references to
everything else through symbols.txt as well. Two things armlink did to the code have
to be reproduced for the result to match:

  - `bl` to a Thumb function becomes `blx`
  - `bl` to a function that is empty or a single instruction is replaced by
    `mov r0, r0` or by that instruction (armlink --inline)
  - a branch to the instruction that follows it is replaced by `mov r0, r0`
    (armlink --branchnop). This happens to tail calls, because armlink places the
    function being tail called right behind its caller when it can
    (armlink --tailreorder).

The `nop` instructions (0xE320F000) found all over the game are not the linker's
doing: armcc emits one wherever it inlines an empty function itself.

armlink also removed what nothing refers to (armlink --remove), including virtual
functions that are never called (--vfe). A section whose symbols are not in
symbols.txt is taken to be one of those and is left out, and an entry of a vtable
that points to it becomes 0, as it is in the original.

Not everything the compiler emits has a symbol. String literals are the common case,
and they come in two kinds:

  - Referenced from data, they are in `.conststring`. armlink merged those across
    the program, so their address is looked up in the pool (see strpool.py).
  - Referenced from code and 64 characters or longer, they are in a `.constdata`
    section that has no symbol. Such a section takes the space in the unit's ranges
    that the sections placed by symbol leave free.
"""

import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import arm, elf
from .image import Image, VersionConfig
from .strpool import StringPool
from .symbols import Symbol, SymbolTable, Unit


class LinkError(Exception):
    pass


# Sections that describe the object rather than contribute to the image
IGNORED_SECTION_PREFIXES = (".ARM.exidx", ".ARM.extab")

# Sections holding a vtable
VTABLE_SECTION_PREFIX = ".constdata__ZTV"

# Symbols armcc defines for its own bookkeeping
INTERNAL_SYMBOL_PREFIXES = ("__ARM_grp", "BuildAttributes$$", "__switch$$", "$")


def uses_pc(insn: int) -> bool:
    """Conservatively tells whether an ARM instruction reads or writes pc."""
    cls = (insn >> 25) & 7
    rn = (insn >> 16) & 0xF
    rd = (insn >> 12) & 0xF
    rs = (insn >> 8) & 0xF
    rm = insn & 0xF
    if cls == 0:
        return 15 in (rn, rd, rm) or (bool(insn & 0x10) and rs == 15)
    if cls == 1:
        return 15 in (rn, rd)
    if cls == 2:
        return 15 in (rn, rd)
    if cls == 3:
        return 15 in (rn, rd, rm)
    if cls == 4:
        return rn == 15 or bool(insn & 0x8000)
    if cls == 5:
        return True
    if cls == 6:
        return rn == 15
    return False


def inline_call(image: Image, insn: int, target: int, target_thumb: bool) -> Optional[int]:
    """
    Emulates `armlink --inline` for a `bl` in ARM state. Returns the instruction that
    replaces the call, or None if the call is kept.
    """
    if target_thumb or not arm.arm_is_bl(insn):
        return None
    text = image.config.section(".text")
    if not text.contains(target):
        return None
    body = image.u32(target)
    if body == arm.ARM_BX_LR:
        return (arm.arm_cond(insn) << 28) | (arm.ARM_MOV_R0_R0 & 0x0FFFFFFF)
    if target + 8 > text.end or image.u32(target + 4) != arm.ARM_BX_LR:
        return None
    return inline_body(insn, body)


def inline_body(insn: int, body: int) -> Optional[int]:
    """
    The instruction that replaces a call (`insn`) to a function whose body is `body`
    followed by `bx lr`, or None if armlink keeps the call.
    """
    cond = arm.arm_cond(insn)
    body_cond = arm.arm_cond(body)
    # `mov r0, r0` was a tail call when armlink made this decision: a branch, which like
    # anything else that involves pc can not be moved to the call site.
    if body_cond == 0xF or body == arm.ARM_MOV_R0_R0 or uses_pc(body):
        return None
    if cond == arm.COND_AL or cond == body_cond:
        return body
    if body_cond == arm.COND_AL:
        return (body & 0x0FFFFFFF) | (cond << 28)
    return None


def is_string_section(section: elf.Section) -> bool:
    """A section of string literals that the linker merges with all others of its name."""
    flags = elf.SHF_MERGE | elf.SHF_STRINGS
    return section.is_alloc and (section.flags & flags) == flags


def output_kind(section: elf.Section) -> str:
    """Kind of the output section (as in config.toml) that an object's section belongs in."""
    if section.is_code:
        return "code"
    if section.type == elf.SHT_NOBITS:
        return "bss"
    if section.flags & elf.SHF_WRITE:
        return "data"
    return "rodata"


class LinkContext:
    def __init__(self, config: VersionConfig, image: Image, symbols: SymbolTable) -> None:
        self.config = config
        self.image = image
        self.symbols = symbols
        try:
            self.string_pools: Dict[str, StringPool] = {
                pool.section: StringPool(image, pool) for pool in config.string_pools
            }
        except ValueError as e:
            raise LinkError(f"{config.path}: {e}") from None
        for name in config.inlined_functions:
            if symbols.find(name):
                raise LinkError(
                    f"{config.path}: {name} is listed in inlined_functions, but "
                    f"{config.symbols_path} gives it an address"
                )

    def lookup(self, name: str, unit: Optional[Unit] = None) -> Symbol:
        candidates = self.symbols.find(name)
        if not candidates:
            raise LinkError(f"undefined symbol {name} (not in {self.config.symbols_path})")
        if len(candidates) == 1:
            return candidates[0]
        if unit is not None:
            inside = [s for s in candidates if unit.contains(s.address)]
            if len(inside) == 1:
                return inside[0]
        exported = [s for s in candidates if s.scope != "local"]
        if len(exported) == 1:
            return exported[0]
        where = ", ".join(f"0x{s.address:08X}" for s in candidates)
        raise LinkError(f"symbol {name} is ambiguous ({where})")


@dataclass
class Placement:
    section: elf.Section
    address: int
    owned: bool  # inside the unit's ranges: its bytes are part of the output


class PlacedObject:
    """An object file whose sections have been assigned addresses."""

    def __init__(
        self, ctx: LinkContext, path: Path, unit: Optional[Unit], strict: bool = True
    ) -> None:
        """
        With `strict` off, sections that cannot be placed are left out instead of
        being an error. That is what work-in-progress objects need: they are only
        compared in objdiff, never linked.
        """
        self.ctx = ctx
        self.path = path
        self.unit = unit
        self.strict = strict
        self.elf = elf.ElfFile.load(path)
        self.placements: Dict[int, Placement] = {}
        # Sections left out because the original image does not have them
        self.removed: List[elf.Section] = []
        self._check_inlined_functions()
        self._place()

    def _check_inlined_functions(self) -> None:
        """The compiled body of an inlined function must be the one config.toml gives."""
        for sym in self.elf.symbols:
            instruction = self.ctx.config.inlined_functions.get(sym.name)
            if instruction is None or not sym.is_defined or sym.bind == elf.STB_LOCAL:
                continue
            body = struct.pack("<II", instruction, arm.ARM_BX_LR)
            section = (
                self.elf.sections[sym.shndx] if sym.shndx < len(self.elf.sections) else None
            )
            if (
                section is None
                or not section.is_code
                or sym.type != elf.STT_FUNC
                or sym.value & 1
                or sym.size != len(body)
                or section.data[sym.value : sym.value + len(body)] != body
                or any(sym.value <= r.offset < sym.value + len(body) for r in section.relocs)
            ):
                raise LinkError(
                    f"{self.path}: {sym.name} does not compile to the body that "
                    f"inlined_functions in {self.ctx.config.path} gives it"
                )

    def _is_candidate(self, section: elf.Section) -> bool:
        if not section.is_alloc or section.type not in (
            elf.SHT_PROGBITS,
            elf.SHT_NOBITS,
            elf.SHT_INIT_ARRAY,
        ):
            return False
        if section.size == 0 or is_string_section(section):
            return False
        return not section.name.startswith(IGNORED_SECTION_PREFIXES)

    def _place(self) -> None:
        by_section: Dict[int, List[elf.Symbol]] = {}
        for sym in self.elf.symbols:
            if sym.shndx in (elf.SHN_UNDEF, elf.SHN_ABS, elf.SHN_COMMON):
                continue
            if sym.type in (elf.STT_SECTION, elf.STT_FILE) or not sym.name:
                continue
            if sym.name.startswith(INTERNAL_SYMBOL_PREFIXES):
                continue
            by_section.setdefault(sym.shndx, []).append(sym)

        floating: List[elf.Section] = []
        for section in self.elf.sections:
            if not self._is_candidate(section):
                continue
            syms = by_section.get(section.index, [])
            shared = bool(section.flags & elf.SHF_GROUP) or (
                bool(syms) and all(s.bind == elf.STB_WEAK for s in syms)
            )
            base: Optional[int] = None
            anchor = ""
            nonmatching = False
            for sym in syms:
                try:
                    known = self.ctx.lookup(sym.name, self.unit)
                except LinkError:
                    continue
                value = sym.value & ~1 if sym.type == elf.STT_FUNC else sym.value
                candidate = known.address - value
                if base is None:
                    base, anchor = candidate, sym.name
                    nonmatching = "nonmatching" in known.extra
                elif candidate != base and self.strict:
                    raise LinkError(
                        f"{self.path}: section {section.name} cannot be placed: {anchor} puts it at "
                        f"0x{base:08X} but {sym.name} puts it at 0x{candidate:08X}"
                    )
            if base is None:
                # Data whose only symbols are locals the original has no name for
                # (__FUNCTION__ strings: one per function, all with that name) is
                # placed like data without a symbol.
                anonymous = not syms or (
                    not section.is_code and all(s.bind == elf.STB_LOCAL for s in syms)
                )
                if anonymous and not shared:
                    floating.append(section)
                    continue
                # None of its symbols exist in the original: the linker removed it.
                # That is only an error if something that was kept refers to it.
                self.removed.append(section)
                continue
            owned = True
            if self.unit is not None:
                end = base + section.size
                owned = any(r.start <= base and end <= r.end for r in self.unit.ranges)
                if not owned and nonmatching:
                    # Code that cannot be left out of the build with NON_MATCHING, such as
                    # a static initializer, but does not match yet: the original stays.
                    self.removed.append(section)
                    continue
                if not owned and not shared and self.strict:
                    raise LinkError(
                        f"{self.path}: {anchor} is at [0x{base:08X}, 0x{end:08X}) which is outside "
                        f"the ranges of {self.unit.name} in {self.ctx.config.splits_path}"
                    )
            self.placements[section.index] = Placement(section, base, owned)

        if self.unit is not None:
            self._place_floating(floating)

    def _place_floating(self, sections: List[elf.Section]) -> None:
        """
        Places sections that have no symbol, in the order they appear in the object.
        Each one goes to the lowest suitably aligned address in the unit's ranges that
        nothing occupies yet, which is where a linker working through the object
        would put it.
        """
        assert self.unit is not None
        config = self.ctx.config
        for section in sections:
            kind = output_kind(section)
            occupied = sorted(
                (p.address, p.address + p.section.size)
                for p in self.placements.values()
                if p.owned
            )
            align = max(section.align, 1)
            for rng in sorted(self.unit.ranges, key=lambda r: r.start):
                if config.section(rng.section).kind != kind:
                    continue
                address = (rng.start + align - 1) & ~(align - 1)
                for start, end in occupied:
                    if end <= address:
                        continue
                    if start >= address + section.size:
                        break
                    address = (end + align - 1) & ~(align - 1)
                if address + section.size <= rng.end:
                    self.placements[section.index] = Placement(section, address, True)
                    break

    def _string_section(self, sym: elf.Symbol) -> Optional[elf.Section]:
        if sym.shndx in (elf.SHN_UNDEF, elf.SHN_ABS, elf.SHN_COMMON):
            return None
        section = self.elf.sections[sym.shndx]
        return section if is_string_section(section) else None

    def locate_string(self, section: elf.Section, offset: int, where: str) -> int:
        """Address in the image of the string literal at `offset` of a string section."""
        pool = self.ctx.string_pools.get(section.name)
        if pool is None:
            raise LinkError(
                f"{where}: reference to a string literal in {section.name}, but "
                f"{self.ctx.config.path} does not define a string pool for that section"
            )
        data = section.data
        if not 0 <= offset < len(data):
            raise LinkError(f"{where}: reference past the end of {section.name}")
        start, end = StringPool.literal_containing(data, offset, pool.char_size)
        contents = data[start:end]
        address = pool.locate(contents)
        if address is None:
            raise LinkError(
                f"{where}: string literal {pool.describe(contents)} is not in the "
                f"{section.name} pool of the original image "
                f"[0x{pool.address:08X}, 0x{pool.end:08X})"
            )
        return address + (offset - start)

    def resolve(self, sym: elf.Symbol) -> Tuple[int, bool]:
        """Address of a symbol and whether it is a Thumb function."""
        if sym.shndx == elf.SHN_ABS:
            return sym.value, False
        if sym.shndx not in (elf.SHN_UNDEF, elf.SHN_COMMON):
            placement = self.placements.get(sym.shndx)
            if placement is not None:
                if sym.type == elf.STT_FUNC:
                    return placement.address + (sym.value & ~1), bool(sym.value & 1)
                return placement.address + sym.value, False
            if sym.type == elf.STT_SECTION or not sym.name:
                section = self.elf.sections[sym.shndx]
                unit = self.unit.name if self.unit is not None else "the unit"
                raise LinkError(
                    f"{self.path}: section {section.name} (0x{section.size:X} bytes) has no symbol "
                    f"to place it by, and {unit} has no free space for it. Add the address range "
                    f"of this data to the unit in {self.ctx.config.splits_path}"
                )
        known = self.ctx.lookup(sym.name, self.unit)
        return known.address, known.thumb

    def unplaced_empty_call(self, section: elf.Section, reloc: elf.Reloc) -> Optional[int]:
        """Inline a narrowly known helper removed by armlink's section elimination.

        A function listed in inlined_functions of config.toml is the other case: it
        is usually defined in another object, so its body comes from the config (and
        is checked against the object that defines it, see _check_inlined_functions).

        Otherwise the complete body must be available in this object.
        No image address is needed for the substitutions below. Address-taking
        and other nonempty bodies must still resolve normally. A second exact case models
        the local result-description accessor: one ``ldr r0, [r0, #4]`` followed by
        ``bx lr``. It is accepted only when the complete helper section is that
        function and every allocated reference outside ignored unwind sections is
        a direct unconditional BL.
        """
        if reloc.type not in (elf.R_ARM_CALL, elf.R_ARM_JUMP24, elf.R_ARM_PC24):
            return None
        if reloc.offset < 0 or reloc.offset + 4 > len(section.data):
            return None
        insn = struct.unpack_from("<I", section.data, reloc.offset)[0]
        if not arm.arm_is_bl(insn):
            return None
        sym = self.elf.symbols[reloc.symbol]
        # Only a call to the entry itself is eligible, never a symbol-plus-offset.
        target_offset = arm.sext(insn & 0x00FFFFFF, 24) * 4 + 8
        instruction = self.ctx.config.inlined_functions.get(sym.name)
        if instruction is not None and sym.bind != elf.STB_LOCAL:
            # Declared in config.toml; its body is checked wherever it is defined
            if target_offset != 0:
                return None
            return inline_body(insn, instruction)
        if (sym.type != elf.STT_FUNC or not sym.is_defined or sym.value & 1
                or sym.shndx >= len(self.elf.sections) or sym.shndx in self.placements
                or self.ctx.symbols.find(sym.name)):
            return None
        body = self.elf.sections[sym.shndx]
        if sym.size == 4 and body.is_code and not body.relocs and target_offset == 0:
            if body.data[sym.value:sym.value + 4] == struct.pack("<I", arm.ARM_BX_LR):
                return (arm.arm_cond(insn) << 28) | (arm.ARM_MOV_R0_R0 & 0x0FFFFFFF)

        replacement = self._unplaced_result_desc_call(section, reloc, sym, insn, body, target_offset)
        if replacement is not None:
            return replacement
        return None

    def _unplaced_result_desc_call(
        self,
        section: elf.Section,
        reloc: elf.Reloc,
        sym: elf.Symbol,
        insn: int,
        body: elf.Section,
        target_offset: int,
    ) -> Optional[int]:
        """Return the exact accessor instruction for one local, erased helper.

        Keep this rule intentionally specific to the observed two-word result
        accessor. In particular, do not infer an address for it or generalize
        one-instruction calls to other local functions.
        """
        if (reloc.type != elf.R_ARM_CALL or arm.arm_cond(insn) != arm.COND_AL
                or not section.is_alloc or not section.is_code):
            return None
        if (sym.bind != elf.STB_LOCAL or sym.type != elf.STT_FUNC or not sym.is_defined
                or sym.value != 0 or sym.size != 8 or sym.shndx >= len(self.elf.sections)
                or sym.shndx in self.placements or self.ctx.symbols.find(sym.name)):
            return None
        if (not body.is_alloc or not body.is_code or body.size != 8 or len(body.data) != 8
                or body.relocs or target_offset != sym.value
                or body.data != struct.pack("<II", 0xE5900004, arm.ARM_BX_LR)):
            return None

        # There may be one normal ELF section symbol and compiler mapping/tag
        # markers, but no other function, object, alias, or cohabiting symbol.
        section_symbols = [
            other for other in self.elf.symbols
            if other.shndx == sym.shndx and other.type == elf.STT_SECTION
        ]
        if (len(section_symbols) != 1 or section_symbols[0].value != 0
                or section_symbols[0].size != 0 or section_symbols[0].name != body.name):
            return None
        for other in self.elf.symbols:
            if (other.shndx != sym.shndx or other is sym
                    or other is section_symbols[0]):
                continue
            if other.is_mapping and other.size == 0:
                continue
            if (other.type == elf.STT_NOTYPE and other.size == 0
                    and other.name.startswith("__tagsym$$")):
                continue
            return None

        # Prove all allocated uses are eligible calls through this exact symbol.
        # In particular, an address-taking/section-symbol reference must not be
        # silently discarded with the helper body.
        saw_call = False
        for caller in self.elf.sections:
            if not caller.is_alloc or caller.name.startswith(IGNORED_SECTION_PREFIXES):
                continue
            for use in caller.relocs:
                target = self.elf.symbols[use.symbol]
                if target.index != sym.index and not (
                    target.type == elf.STT_SECTION and target.shndx == sym.shndx
                ):
                    continue
                if (target.index != sym.index or use.type != elf.R_ARM_CALL
                        or not caller.is_code or use.offset < 0
                        or use.offset + 4 > len(caller.data)):
                    return None
                call_insn = struct.unpack_from("<I", caller.data, use.offset)[0]
                if (not arm.arm_is_bl(call_insn) or arm.arm_cond(call_insn) != arm.COND_AL
                        or arm.sext(call_insn & 0x00FFFFFF, 24) * 4 + 8 != sym.value):
                    return None
                saw_call = True

        if not saw_call:
            return None
        return 0xE5900004

    def relocate(self, placement: Placement, inline: bool = True) -> bytearray:
        """Contents of a section with every relocation applied."""
        section = placement.section
        data = bytearray(section.data)
        image = self.ctx.image
        for reloc in section.relocs:
            if reloc.type in (elf.R_ARM_NONE, elf.R_ARM_V4BX):
                continue
            sym = self.elf.symbols[reloc.symbol]
            off = reloc.offset
            p = placement.address + off
            where = f"{self.path}: {section.name}+0x{off:X}"

            replacement = self.unplaced_empty_call(section, reloc) if inline else None
            if replacement is not None:
                struct.pack_into("<I", data, off, replacement)
                continue

            strings = self._string_section(sym)
            if strings is not None:
                if reloc.type not in (elf.R_ARM_ABS32, elf.R_ARM_TARGET1):
                    name = elf.RELOC_NAMES.get(reloc.type, str(reloc.type))
                    raise LinkError(f"{where}: unsupported relocation {name} against a string")
                addend = struct.unpack_from("<I", data, off)[0]
                address = self.locate_string(strings, sym.value + addend, where)
                struct.pack_into("<I", data, off, address)
                continue

            try:
                s, thumb = self.resolve(sym)
            except LinkError as e:
                if self.is_removed_virtual(section, reloc):
                    struct.pack_into("<I", data, off, 0)
                    continue
                raise LinkError(f"{e}\n  referenced from {section.name}+0x{reloc.offset:X}") from None

            if reloc.type == elf.R_ARM_TARGET1 and section.name == ".init_array":
                # The game's static initializer table holds offsets, not addresses
                addend = struct.unpack_from("<I", data, off)[0]
                struct.pack_into("<I", data, off, (s + addend - p) & 0xFFFFFFFF)

            elif reloc.type in (elf.R_ARM_ABS32, elf.R_ARM_TARGET1):
                addend = struct.unpack_from("<I", data, off)[0]
                struct.pack_into("<I", data, off, ((s + addend) & 0xFFFFFFFF) | int(thumb))

            elif reloc.type == elf.R_ARM_REL32:
                addend = struct.unpack_from("<I", data, off)[0]
                struct.pack_into("<I", data, off, (((s + addend) | int(thumb)) - p) & 0xFFFFFFFF)

            elif reloc.type in (elf.R_ARM_CALL, elf.R_ARM_JUMP24, elf.R_ARM_PC24):
                insn = struct.unpack_from("<I", data, off)[0]
                target = (s + (arm.sext(insn & 0x00FFFFFF, 24) << 2) + 8) & 0xFFFFFFFF
                is_call = arm.arm_is_bl(insn) or arm.arm_is_blx_imm(insn)
                if inline and is_call:
                    replacement = inline_call(image, insn, target, thumb)
                    if replacement is not None:
                        struct.pack_into("<I", data, off, replacement)
                        continue
                offset = target - (p + 8)
                if offset == -4 and not thumb and arm.arm_cond(insn) == arm.COND_AL:
                    # A branch to the next instruction
                    struct.pack_into("<I", data, off, arm.ARM_MOV_R0_R0)
                    continue
                if not -0x2000000 <= offset < 0x2000000:
                    raise LinkError(f"{where}: branch to {sym.name} is out of range")
                if thumb:
                    if not is_call or arm.arm_cond(insn) not in (arm.COND_AL, 0xF):
                        raise LinkError(
                            f"{where}: branch to Thumb function {sym.name} needs a veneer"
                        )
                    insn = 0xFA000000 | (((offset >> 1) & 1) << 24) | ((offset >> 2) & 0x00FFFFFF)
                else:
                    if arm.arm_is_blx_imm(insn):
                        insn = 0xEB000000
                    insn = (insn & 0xFF000000) | ((offset >> 2) & 0x00FFFFFF)
                struct.pack_into("<I", data, off, insn)

            elif reloc.type == elf.R_ARM_THM_CALL:
                hi, lo = struct.unpack_from("<HH", data, off)
                addend = (arm.sext(hi & 0x7FF, 11) << 12) | ((lo & 0x7FF) << 1)
                target = (s + addend + 4) & 0xFFFFFFFF
                if thumb:
                    offset = target - (p + 4)
                    lo = 0xF800 | ((offset >> 1) & 0x7FF)
                else:
                    offset = target - ((p + 4) & ~3)
                    lo = 0xE800 | ((offset >> 1) & 0x7FE)
                if not -0x400000 <= offset < 0x400000:
                    raise LinkError(f"{where}: call to {sym.name} is out of range")
                hi = 0xF000 | ((offset >> 12) & 0x7FF)
                struct.pack_into("<HH", data, off, hi, lo)

            elif reloc.type == elf.R_ARM_PREL31:
                word = struct.unpack_from("<I", data, off)[0]
                addend = arm.sext(word & 0x7FFFFFFF, 31)
                value = ((s + addend) | int(thumb)) - p
                struct.pack_into("<I", data, off, (word & 0x80000000) | (value & 0x7FFFFFFF))

            else:
                name = elf.RELOC_NAMES.get(reloc.type, str(reloc.type))
                raise LinkError(f"{where}: unsupported relocation {name} against {sym.name}")
        return data

    def is_removed_virtual(self, section: elf.Section, reloc: elf.Reloc) -> bool:
        """
        A vtable entry for a function the original image does not have: armlink removed
        virtual functions that are never called and left 0 in their place.
        """
        if not section.name.startswith(VTABLE_SECTION_PREFIX):
            return False
        if reloc.type not in (elf.R_ARM_ABS32, elf.R_ARM_TARGET1):
            return False
        sym = self.elf.symbols[reloc.symbol]
        return sym.type in (elf.STT_FUNC, elf.STT_NOTYPE) and not self.ctx.symbols.find(sym.name)

    def removed_virtuals(self, section: elf.Section) -> List[elf.Reloc]:
        """Relocations of a vtable section whose target was removed by the linker."""
        result = []
        for reloc in section.relocs:
            if not self.is_removed_virtual(section, reloc):
                continue
            try:
                self.resolve(self.elf.symbols[reloc.symbol])
            except LinkError:
                result.append(reloc)
        return result

    def inlined_calls(self, placement: Placement) -> List[Tuple[elf.Reloc, int]]:
        """Calls in a section that armlink would have replaced, with their replacement."""
        section = placement.section
        result = []
        for reloc in section.relocs:
            replacement = self.unplaced_empty_call(section, reloc)
            if replacement is not None:
                result.append((reloc, replacement))
                continue
            if reloc.type not in (elf.R_ARM_CALL, elf.R_ARM_JUMP24, elf.R_ARM_PC24):
                continue
            insn = struct.unpack_from("<I", section.data, reloc.offset)[0]
            if not arm.arm_is_bl(insn):
                continue
            try:
                s, thumb = self.resolve(self.elf.symbols[reloc.symbol])
            except LinkError:
                continue
            target = (s + (arm.sext(insn & 0x00FFFFFF, 24) << 2) + 8) & 0xFFFFFFFF
            replacement = inline_call(self.ctx.image, insn, target, thumb)
            if replacement is not None:
                result.append((reloc, replacement))
        return result
