"""
Minimal ELF32 little-endian relocatable object reader and writer.

Covers what armcc emits and what objdiff needs to read: sections, a symbol table and
REL relocations (the addend is stored in the place being relocated).
"""

import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

ET_REL = 1
EM_ARM = 40
EF_ARM_EABI_VER5 = 0x05000000

SHT_NULL = 0
SHT_PROGBITS = 1
SHT_SYMTAB = 2
SHT_STRTAB = 3
SHT_RELA = 4
SHT_NOBITS = 8
SHT_REL = 9
SHT_INIT_ARRAY = 14
SHT_GROUP = 17
SHT_ARM_ATTRIBUTES = 0x70000003

SHF_WRITE = 0x1
SHF_ALLOC = 0x2
SHF_EXECINSTR = 0x4
SHF_MERGE = 0x10
SHF_STRINGS = 0x20
SHF_GROUP = 0x200

SHN_UNDEF = 0
SHN_ABS = 0xFFF1
SHN_COMMON = 0xFFF2

STB_LOCAL = 0
STB_GLOBAL = 1
STB_WEAK = 2

STT_NOTYPE = 0
STT_OBJECT = 1
STT_FUNC = 2
STT_SECTION = 3
STT_FILE = 4

STV_DEFAULT = 0
STV_HIDDEN = 2

R_ARM_NONE = 0
R_ARM_PC24 = 1
R_ARM_ABS32 = 2
R_ARM_REL32 = 3
R_ARM_THM_CALL = 10
R_ARM_CALL = 28
R_ARM_JUMP24 = 29
R_ARM_THM_JUMP24 = 30
R_ARM_TARGET1 = 38
R_ARM_V4BX = 40
R_ARM_PREL31 = 42
R_ARM_THM_JUMP11 = 102
R_ARM_THM_JUMP8 = 103

RELOC_NAMES = {
    R_ARM_NONE: "R_ARM_NONE",
    R_ARM_PC24: "R_ARM_PC24",
    R_ARM_ABS32: "R_ARM_ABS32",
    R_ARM_REL32: "R_ARM_REL32",
    R_ARM_THM_CALL: "R_ARM_THM_CALL",
    R_ARM_CALL: "R_ARM_CALL",
    R_ARM_JUMP24: "R_ARM_JUMP24",
    R_ARM_THM_JUMP24: "R_ARM_THM_JUMP24",
    R_ARM_TARGET1: "R_ARM_TARGET1",
    R_ARM_V4BX: "R_ARM_V4BX",
    R_ARM_PREL31: "R_ARM_PREL31",
    R_ARM_THM_JUMP11: "R_ARM_THM_JUMP11",
    R_ARM_THM_JUMP8: "R_ARM_THM_JUMP8",
}


@dataclass
class Reloc:
    offset: int
    type: int
    symbol: Union[int, "Symbol"]  # symbol table index (a Symbol when writing)
    addend: Optional[int] = None  # only set for RELA
    # Where the entry came from when read from a file: (index of the REL section, entry number)
    origin: Optional[Tuple[int, int]] = None


@dataclass
class Section:
    name: str
    type: int = SHT_PROGBITS
    flags: int = 0
    addr: int = 0
    data: bytes = b""
    size: int = 0  # for SHT_NOBITS, otherwise len(data)
    link: int = 0
    info: int = 0
    align: int = 1
    entsize: int = 0
    relocs: List[Reloc] = field(default_factory=list)
    index: int = 0
    offset: int = 0  # position of the contents in the file it was read from

    @property
    def is_alloc(self) -> bool:
        return bool(self.flags & SHF_ALLOC)

    @property
    def is_code(self) -> bool:
        return bool(self.flags & SHF_EXECINSTR)


@dataclass
class Symbol:
    name: str
    value: int = 0
    size: int = 0
    bind: int = STB_LOCAL
    type: int = STT_NOTYPE
    other: int = STV_DEFAULT
    shndx: int = SHN_UNDEF
    index: int = 0

    @property
    def is_defined(self) -> bool:
        return self.shndx != SHN_UNDEF

    @property
    def is_mapping(self) -> bool:
        """$a/$t/$d (optionally with a .suffix) mark ARM code, Thumb code and data."""
        return (
            len(self.name) >= 2
            and self.name[0] == "$"
            and self.name[1] in "atd"
            and (len(self.name) == 2 or self.name[2] == ".")
        )


###
# Reader
###


class ElfFile:
    def __init__(self) -> None:
        self.sections: List[Section] = []
        self.symbols: List[Symbol] = []
        self.flags = EF_ARM_EABI_VER5
        self.shoff = 0
        self.shentsize = 40

    @staticmethod
    def load(path: Path) -> "ElfFile":
        return ElfFile.parse(Path(path).read_bytes(), str(path))

    @staticmethod
    def parse(data: bytes, where: str = "<elf>") -> "ElfFile":
        if data[:4] != b"\x7fELF":
            raise ValueError(f"{where}: not an ELF file")
        if data[4] != 1 or data[5] != 1:
            raise ValueError(f"{where}: expected a 32-bit little-endian ELF")
        (e_type, e_machine, _, _, _, e_shoff, e_flags, _, _, _, e_shentsize, e_shnum, e_shstrndx) = (
            struct.unpack_from("<HHIIIIIHHHHHH", data, 16)
        )
        if e_machine != EM_ARM:
            raise ValueError(f"{where}: not an ARM object")

        elf = ElfFile()
        elf.flags = e_flags
        elf.shoff = e_shoff
        elf.shentsize = e_shentsize
        raw = []
        for i in range(e_shnum):
            raw.append(struct.unpack_from("<IIIIIIIIII", data, e_shoff + i * e_shentsize))

        def cstr(table: bytes, off: int) -> str:
            end = table.index(b"\0", off)
            return table[off:end].decode("utf-8", "replace")

        shstr_off, shstr_size = raw[e_shstrndx][4], raw[e_shstrndx][5]
        shstrtab = data[shstr_off : shstr_off + shstr_size]

        for i, (name, typ, flags, addr, off, size, link, info, align, entsize) in enumerate(raw):
            body = b"" if typ in (SHT_NOBITS, SHT_NULL) else data[off : off + size]
            elf.sections.append(
                Section(
                    cstr(shstrtab, name), typ, flags, addr, body, size, link, info, align, entsize,
                    index=i, offset=off,
                )
            )

        symtab = next((s for s in elf.sections if s.type == SHT_SYMTAB), None)
        if symtab is not None:
            strtab = elf.sections[symtab.link].data
            for i in range(len(symtab.data) // 16):
                name, value, size, info, other, shndx = struct.unpack_from(
                    "<IIIBBH", symtab.data, i * 16
                )
                elf.symbols.append(
                    Symbol(cstr(strtab, name), value, size, info >> 4, info & 0xF, other, shndx, index=i)
                )

        for section in elf.sections:
            if section.type == SHT_REL:
                target = elf.sections[section.info]
                for i in range(len(section.data) // 8):
                    offset, info = struct.unpack_from("<II", section.data, i * 8)
                    target.relocs.append(
                        Reloc(offset, info & 0xFF, info >> 8, origin=(section.index, i))
                    )
            elif section.type == SHT_RELA:
                target = elf.sections[section.info]
                for i in range(len(section.data) // 12):
                    offset, info, addend = struct.unpack_from("<IIi", section.data, i * 12)
                    target.relocs.append(Reloc(offset, info & 0xFF, info >> 8, addend))
        return elf

    def section(self, name: str) -> Optional[Section]:
        for section in self.sections:
            if section.name == name:
                return section
        return None


###
# Writer
###


class StringTable:
    def __init__(self) -> None:
        self.data = bytearray(b"\0")
        self.offsets: Dict[str, int] = {"": 0}

    def add(self, name: str) -> int:
        off = self.offsets.get(name)
        if off is None:
            off = len(self.data)
            self.offsets[name] = off
            self.data += name.encode("utf-8") + b"\0"
        return off


def build_attributes() -> bytes:
    """
    .ARM.attributes matching what armcc emits for `--cpu=MPCore`. objdiff reads this
    to pick the instruction set (ARMv6K with VFPv2) when disassembling.
    """

    def uleb(value: int) -> bytes:
        out = bytearray()
        while True:
            byte = value & 0x7F
            value >>= 7
            out.append(byte | (0x80 if value else 0))
            if not value:
                return bytes(out)

    attrs = bytearray()
    attrs += uleb(5) + b"MPCore\0"  # Tag_CPU_name
    attrs += uleb(6) + uleb(9)  # Tag_CPU_arch: v6K
    attrs += uleb(8) + uleb(1)  # Tag_ARM_ISA_use
    attrs += uleb(9) + uleb(1)  # Tag_THUMB_ISA_use: Thumb-1
    attrs += uleb(10) + uleb(2)  # Tag_FP_arch: VFPv2
    attrs += uleb(24) + uleb(1)  # Tag_ABI_align_needed
    attrs += uleb(25) + uleb(1)  # Tag_ABI_align_preserved
    attrs += uleb(28) + uleb(1)  # Tag_ABI_VFP_args
    file_attrs = b"\x01" + struct.pack("<I", 5 + len(attrs)) + bytes(attrs)
    vendor = b"aeabi\0" + file_attrs
    return b"A" + struct.pack("<I", 4 + len(vendor)) + vendor


class ElfWriter:
    """Builds a relocatable object. Symbols may be added in any order."""

    def __init__(self) -> None:
        self.sections: List[Section] = [Section("", SHT_NULL)]
        self.symbols: List[Symbol] = []
        self._undefined: Dict[str, Symbol] = {}

    def add_section(self, section: Section) -> Section:
        section.index = len(self.sections)
        self.sections.append(section)
        return section

    def add_symbol(self, symbol: Symbol) -> Symbol:
        self.symbols.append(symbol)
        return symbol

    def undefined(self, name: str, typ: int = STT_NOTYPE) -> Symbol:
        """An external symbol, created on first use."""
        sym = self._undefined.get(name)
        if sym is None:
            sym = Symbol(name, bind=STB_GLOBAL, type=typ, shndx=SHN_UNDEF)
            self._undefined[name] = sym
            self.symbols.append(sym)
        return sym

    def write(self, path: Path) -> bool:
        """Writes the object. Returns False if the file already had the same content."""
        data = self.serialize()
        path = Path(path)
        if path.is_file() and path.read_bytes() == data:
            return False
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return True

    def serialize(self) -> bytes:
        sections = list(self.sections)
        sections.append(
            Section(".ARM.attributes", SHT_ARM_ATTRIBUTES, data=build_attributes(), align=1)
        )

        # Local symbols must come first
        ordered = [Symbol("")]
        ordered += [s for s in self.symbols if s.bind == STB_LOCAL]
        first_global = len(ordered)
        ordered += [s for s in self.symbols if s.bind != STB_LOCAL]
        for i, sym in enumerate(ordered):
            sym.index = i

        strtab = StringTable()
        symtab = bytearray()
        for sym in ordered:
            symtab += struct.pack(
                "<IIIBBH",
                strtab.add(sym.name),
                sym.value,
                sym.size,
                (sym.bind << 4) | sym.type,
                sym.other,
                sym.shndx,
            )

        symtab_index = len(sections)
        strtab_index = symtab_index + 1
        sections.append(
            Section(".symtab", SHT_SYMTAB, data=bytes(symtab), link=strtab_index, info=first_global, align=4, entsize=16)
        )
        sections.append(Section(".strtab", SHT_STRTAB, data=bytes(strtab.data)))

        for section in list(self.sections):
            if not section.relocs:
                continue
            body = bytearray()
            for reloc in sorted(section.relocs, key=lambda r: r.offset):
                sym_index = reloc.symbol.index if isinstance(reloc.symbol, Symbol) else reloc.symbol
                body += struct.pack("<II", reloc.offset, (sym_index << 8) | reloc.type)
            sections.append(
                Section(
                    ".rel" + section.name, SHT_REL, data=bytes(body), link=symtab_index, info=section.index, align=4, entsize=8
                )
            )

        shstrtab = StringTable()
        shstrtab_index = len(sections)
        sections.append(Section(".shstrtab", SHT_STRTAB))
        name_offsets = [shstrtab.add(s.name) for s in sections]
        sections[-1].data = bytes(shstrtab.data)

        out = bytearray(b"\0" * 52)
        headers = []
        for section, name_off in zip(sections, name_offsets):
            align = max(section.align, 1)
            if section.type == SHT_NULL:
                headers.append((0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
                continue
            while len(out) % align:
                out.append(0)
            offset = len(out)
            if section.type == SHT_NOBITS:
                size = section.size
            else:
                size = len(section.data)
                out += section.data
            headers.append(
                (name_off, section.type, section.flags, section.addr, offset, size, section.link, section.info, align, section.entsize)
            )
        while len(out) % 4:
            out.append(0)
        shoff = len(out)
        for header in headers:
            out += struct.pack("<IIIIIIIIII", *header)

        ident = b"\x7fELF" + bytes([1, 1, 1, 0]) + b"\0" * 8
        struct.pack_into(
            "<16sHHIIIIIHHHHHH",
            out,
            0,
            ident,
            ET_REL,
            EM_ARM,
            1,
            0,
            0,
            shoff,
            EF_ARM_EABI_VER5,
            52,
            0,
            0,
            40,
            len(sections),
            shstrtab_index,
        )
        return bytes(out)
