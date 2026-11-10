"""
Minimal ARMv6K (ARM + Thumb-1) decoding and per-function control-flow analysis.

This is not a disassembler. It decodes just enough to answer the questions the
split/link tooling cares about:

  - where control flow goes (branches, calls, returns, switch tables)
  - which words inside a function are data (literal pools, jump tables, inline
    strings) rather than instructions
  - which words need relocations once the function is lifted out of the image

Everything here is specific to the code RVCT `armcc` generates for the 3DS.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set, Tuple

COND_AL = 0xE

ARM_NOP = 0xE320F000  # `nop`: what armcc leaves behind when it inlines an empty function
ARM_MOV_R0_R0 = 0xE1A00000  # the no-op armlink overwrites branches it optimizes away with
ARM_BX_LR = 0xE12FFF1E
THUMB_BX_LR = 0x4770


def sext(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return (value & (sign - 1)) - (value & sign)


def ror32(value: int, amount: int) -> int:
    amount &= 31
    return ((value >> amount) | (value << (32 - amount))) & 0xFFFFFFFF


def arm_expand_imm(insn: int) -> int:
    return ror32(insn & 0xFF, ((insn >> 8) & 0xF) * 2)


###
# ARM instruction predicates
###


def arm_cond(insn: int) -> int:
    return insn >> 28

def arm_is_bl(insn: int) -> bool:
    return (insn & 0x0F000000) == 0x0B000000 and arm_cond(insn) != 0xF


def arm_is_b(insn: int) -> bool:
    return (insn & 0x0F000000) == 0x0A000000 and arm_cond(insn) != 0xF


def arm_is_blx_imm(insn: int) -> bool:
    return (insn & 0xFE000000) == 0xFA000000


def arm_branch_target(addr: int, insn: int) -> int:
    """Target of B/BL/BLX <imm>. For BLX the result does not carry the Thumb bit."""
    target = addr + 8 + (sext(insn & 0x00FFFFFF, 24) << 2)
    if arm_is_blx_imm(insn):
        target += ((insn >> 24) & 1) << 1
    return target & 0xFFFFFFFF


def arm_is_bx(insn: int) -> bool:
    return (insn & 0x0FFFFFF0) == 0x012FFF10 and arm_cond(insn) != 0xF

def arm_is_data_processing(insn: int) -> bool:
    if arm_cond(insn) == 0xF or (insn & 0x0C000000) != 0:
        return False
    if (insn & 0x02000000) == 0 and (insn & 0x90) == 0x90:
        return False  # multiplies, extra load/store
    if (insn & 0x01900000) == 0x01000000:
        return False  # miscellaneous (bx, clz, msr, ...)
    return True


def arm_dp_writes_pc(insn: int) -> bool:
    if not arm_is_data_processing(insn):
        return False
    opcode = (insn >> 21) & 0xF
    if 8 <= opcode <= 11:
        return False  # tst/teq/cmp/cmn
    return ((insn >> 12) & 0xF) == 15


def arm_is_adr(insn: int) -> bool:
    """add/sub rX, pc, #imm"""
    return arm_cond(insn) != 0xF and (insn & 0x0FFF0000) in (0x028F0000, 0x024F0000)


def arm_adr_target(addr: int, insn: int) -> int:
    imm = arm_expand_imm(insn)
    if (insn & 0x0FFF0000) == 0x024F0000:
        imm = -imm
    return (addr + 8 + imm) & 0xFFFFFFFF


def arm_is_ldr_literal(insn: int) -> bool:
    """ldr/ldrb rX, [pc, #imm]"""
    return arm_cond(insn) != 0xF and (insn & 0x0F3F0000) == 0x051F0000


def arm_ldr_literal_target(addr: int, insn: int) -> int:
    imm = insn & 0xFFF
    if not insn & 0x00800000:
        imm = -imm
    return (addr + 8 + imm) & 0xFFFFFFFF


def arm_is_vldr_literal(insn: int) -> bool:
    """vldr sX/dX, [pc, #imm]"""
    return arm_cond(insn) != 0xF and (insn & 0x0F3F0E00) == 0x0D1F0A00


def arm_vldr_literal_target(addr: int, insn: int) -> Tuple[int, int]:
    imm = (insn & 0xFF) << 2
    if not insn & 0x00800000:
        imm = -imm
    size = 8 if insn & 0x100 else 4
    return (addr + 8 + imm) & 0xFFFFFFFF, size


def arm_is_load_to_pc(insn: int) -> bool:
    """ldr pc, [...]"""
    if arm_cond(insn) == 0xF or (insn & 0x0C000000) != 0x04000000:
        return False
    if (insn & 0x02000010) == 0x02000010:
        return False  # media instructions
    return (insn & 0x00500000) == 0x00100000 and ((insn >> 12) & 0xF) == 15


def arm_is_switch_ldr(insn: int) -> bool:
    """ldr<cc> pc, [pc, rX, lsl #2]: armcc's ARM-state switch with an address table."""
    return arm_cond(insn) != 0xF and (insn & 0x0FFFFFF0) == 0x079FF100


def arm_is_switch_add(insn: int) -> bool:
    """add<cc> pc, pc, rX, lsl #2: switch with a table of branches."""
    return arm_cond(insn) != 0xF and (insn & 0x0FFFFFF0) == 0x008FF100


def arm_is_ldm_pc(insn: int) -> bool:
    """ldm/pop with pc in the register list"""
    return arm_cond(insn) != 0xF and (insn & 0x0E108000) == 0x08108000


def arm_saves_lr(insn: int) -> bool:
    """push {..., lr}"""
    return (insn & 0x0FFF4000) == 0x092D4000 or (insn & 0x0FFFFFFF) == 0x052DE004


def arm_restores_lr(insn: int) -> bool:
    """pop {..., lr}: the epilogue of a function that is about to tail call"""
    if (insn & 0x0FFFFFFF) == 0x049DE004:
        return True
    return (insn & 0x0FFFC000) == 0x08BD4000


def arm_is_cmp_imm(insn: int) -> bool:
    return arm_cond(insn) != 0xF and (insn & 0x0FF00000) == 0x03500000


def arm_is_undefined(insn: int) -> bool:
    """Cheap filter for words that cannot be code armcc generated (used to validate guesses)."""
    cond = arm_cond(insn)
    if cond == 0xF:
        # blx imm, pld, cps, etc. Everything else in the unconditional space is not expected.
        if arm_is_blx_imm(insn):
            return False
        if (insn & 0x0D70F000) == 0x0550F000:
            return False  # pld
        if insn == 0xF57FF01F:
            return False  # clrex
        return True
    cls = (insn >> 25) & 7
    if cls == 3 and insn & 0x10:
        # media instructions (sxt*/uxt*, rev, pkh, sat, ...); only UDF is rejected
        return (insn & 0x0FF000F0) == 0x07F000F0
    if cls in (6, 7) and (insn & 0x0F000000) != 0x0F000000:
        # coprocessor: only VFP (cp10/cp11) and cp15 are plausible
        cp = (insn >> 8) & 0xF
        return cp not in (10, 11, 15)
    return False


###
# Thumb instruction predicates
###


def thumb_is_bl_prefix(insn: int) -> bool:
    return (insn & 0xF800) == 0xF000


def thumb_is_bl_suffix(insn: int) -> bool:
    return (insn & 0xF800) == 0xF800


def thumb_is_blx_suffix(insn: int) -> bool:
    return (insn & 0xF801) == 0xE800


def thumb_bl_target(addr: int, hi: int, lo: int) -> int:
    """Target of a Thumb BL/BLX pair located at `addr`."""
    offset = (sext(hi & 0x7FF, 11) << 12) | ((lo & 0x7FF) << 1)
    target = (addr + 4 + offset) & 0xFFFFFFFF
    if thumb_is_blx_suffix(lo):
        target &= ~3
    return target


def thumb_is_b(insn: int) -> bool:
    return (insn & 0xF800) == 0xE000


def thumb_is_bcond(insn: int) -> bool:
    return (insn & 0xF000) == 0xD000 and ((insn >> 8) & 0xF) < 0xE


def thumb_branch_target(addr: int, insn: int) -> int:
    if thumb_is_b(insn):
        return (addr + 4 + (sext(insn & 0x7FF, 11) << 1)) & 0xFFFFFFFF
    return (addr + 4 + (sext(insn & 0xFF, 8) << 1)) & 0xFFFFFFFF


def thumb_is_ldr_literal(insn: int) -> bool:
    return (insn & 0xF800) == 0x4800


def thumb_ldr_literal_target(addr: int, insn: int) -> int:
    return ((addr + 4) & ~3) + ((insn & 0xFF) << 2)


def thumb_is_adr(insn: int) -> bool:
    return (insn & 0xF800) == 0xA000


def thumb_is_pop_pc(insn: int) -> bool:
    return (insn & 0xFF00) == 0xBD00


def thumb_is_bx(insn: int) -> bool:
    return (insn & 0xFF87) == 0x4700


def thumb_is_undefined(insn: int) -> bool:
    """Encodings that do not exist in ARMv6K Thumb (a BL suffix is checked by the caller)."""
    if (insn & 0xFF00) == 0xDE00:
        return True  # udf
    if (insn & 0xF000) == 0xB000:
        # Miscellaneous: only sp adjust, sign/zero extend, push/pop, cps, rev and bkpt exist
        return ((insn >> 8) & 0xF) in (0x1, 0x3, 0x7, 0x8, 0x9, 0xB, 0xF)
    return False


def thumb_is_mov_pc(insn: int) -> bool:
    """mov pc, rX / add pc, rX"""
    return (insn & 0xFF87) in (0x4687, 0x4487)


###
# Function analysis
###

KIND_CALL = "call"  # bl / blx
KIND_JUMP = "jump"  # b / b<cond> leaving the function (tail call)


@dataclass
class BranchRef:
    addr: int  # address of the branch instruction
    target: int  # destination address (no Thumb bit)
    target_thumb: bool
    kind: str
    thumb: bool  # the branch instruction itself is Thumb


@dataclass
class SwitchTable:
    label: int  # address of the `__switch$$` label (the instruction after the ldr pc)
    table: int  # address of the first table entry
    count: int  # number of entries


@dataclass
class FunctionInfo:
    start: int
    limit: int
    thumb: bool
    # Addresses of decoded instructions
    code: Set[int] = field(default_factory=set)
    # Literal pool entries (addr -> size in bytes)
    pool: Dict[int, int] = field(default_factory=dict)
    # Calls and tail calls leaving the function
    branches: List[BranchRef] = field(default_factory=list)
    switches: List[SwitchTable] = field(default_factory=list)
    # Data addressed with `adr` (inline strings and tables)
    adr_targets: Set[int] = field(default_factory=set)
    # Word-aligned addresses of everything known to be data
    data_words: Set[int] = field(default_factory=set)
    # Pool entries loaded with `ldr` (as opposed to floating-point constants)
    ldr_pool: Set[int] = field(default_factory=set)
    # Decoding ran into something that is not plausible code
    suspicious: bool = False
    # Words an earlier walk decoded as code before finding they are loaded as data
    data_stops: Set[int] = field(default_factory=set)

    def is_data(self, addr: int) -> bool:
        return (addr & ~3) in self.data_words or (addr & ~3) in self.data_stops

    def add_pool(self, addr: int, size: int) -> None:
        if size > self.pool.get(addr, 0):
            self.pool[addr] = size
            for off in range(0, size, 4):
                self.data_words.add(addr + off)


ReadWord = Callable[[int], int]


class Analyzer:
    """
    Walks the control flow of a single function.

    `read32`/`read16` read from the image. `is_function` tells the analyzer whether an
    address is a known function entry point, which is how an in-function branch is told
    apart from a tail call.
    """

    def __init__(
        self,
        read32: ReadWord,
        read16: ReadWord,
        text_start: int,
        text_end: int,
        is_function: Callable[[int], bool],
    ) -> None:
        self.read32 = read32
        self.read16 = read16
        self.text_start = text_start
        self.text_end = text_end
        self.is_function = is_function

    def analyze(self, start: int, limit: int, thumb: bool) -> FunctionInfo:
        """
        A walk can decode a literal pool as code before it reaches the load that
        makes it data: code after a call that does not return (`bl longjmp`) runs
        straight into the pool. The walk is then repeated with those words known to
        be data, until no word is both.
        """
        stops: Set[int] = set()
        while True:
            info = FunctionInfo(start, limit, thumb)
            info.data_stops = stops
            if thumb:
                self._walk_thumb(info)
            else:
                self._walk_arm(info)
            conflicts = {addr & ~3 for addr in info.code if (addr & ~3) in info.data_words}
            if not conflicts or conflicts <= stops:
                return info
            stops = stops | conflicts

    # ARM

    def _switch_count(self, info: FunctionInfo, addr: int, insn: int) -> Optional[int]:
        """Find the `cmp rX, #N` guarding a switch dispatch and derive the entry count."""
        rm = insn & 0xF
        cond = arm_cond(insn)
        for back in range(1, 6):
            prev_addr = addr - back * 4
            if prev_addr < info.start:
                break
            prev = self.read32(prev_addr)
            if arm_is_cmp_imm(prev) and ((prev >> 16) & 0xF) == rm:
                n = arm_expand_imm(prev)
                if cond == 0x3:  # cc/lo
                    return n
                if cond == 0x9:  # ls
                    return n + 1
                return None
        return None

    def _walk_arm(self, info: FunctionInfo) -> None:
        work = [info.start]
        start, limit = info.start, info.limit
        code = info.code
        read32 = self.read32
        while work:
            pc = work.pop()
            while start <= pc < limit and pc not in code:
                if info.is_data(pc):
                    break
                insn = read32(pc)
                cond = insn >> 28
                cls = (insn >> 25) & 7

                if cond == 0xF:
                    if arm_is_blx_imm(insn):
                        code.add(pc)
                        target = arm_branch_target(pc, insn)
                        info.branches.append(BranchRef(pc, target, True, KIND_CALL, False))
                        pc += 4
                        continue
                    if arm_is_undefined(insn):
                        info.suspicious = True
                        break
                    code.add(pc)
                    pc += 4
                    continue

                always = cond == COND_AL

                if cls == 5:
                    code.add(pc)
                    target = arm_branch_target(pc, insn)
                    if insn & 0x01000000:
                        info.branches.append(BranchRef(pc, target, False, KIND_CALL, False))
                        pc += 4
                        continue
                    internal = start <= target < limit and (
                        target == start or not self.is_function(target)
                    )
                    if internal:
                        work.append(target)
                    else:
                        info.branches.append(BranchRef(pc, target, False, KIND_JUMP, False))
                    if always:
                        break
                    pc += 4
                    continue

                if cls == 7:
                    code.add(pc)
                    pc += 4
                    continue

                if cls == 6:
                    if arm_is_undefined(insn):
                        info.suspicious = True
                        break
                    code.add(pc)
                    if arm_is_vldr_literal(insn):
                        target, size = arm_vldr_literal_target(pc, insn)
                        if start <= target < limit:
                            info.add_pool(target, size)
                        else:
                            info.suspicious = True
                    pc += 4
                    continue

                if cls == 4:
                    code.add(pc)
                    if arm_is_ldm_pc(insn) and always:
                        break
                    pc += 4
                    continue

                if cls >= 2:
                    # Load/store word or byte
                    if arm_is_undefined(insn):
                        info.suspicious = True
                        break
                    code.add(pc)
                    if arm_is_switch_ldr(insn):
                        self._switch_ldr(info, pc, insn, work)
                        # The instruction after the dispatch handles the out-of-range case
                        pc += 4
                        continue
                    if arm_is_ldr_literal(insn):
                        target = arm_ldr_literal_target(pc, insn)
                        if start <= target < limit:
                            # Byte loads still occupy a whole pool word
                            info.add_pool(target & ~3, 4)
                            info.ldr_pool.add(target & ~3)
                        else:
                            info.suspicious = True
                    if arm_is_load_to_pc(insn) and always:
                        break
                    pc += 4
                    continue

                # Data processing and miscellaneous
                code.add(pc)
                if arm_is_bx(insn):
                    if always:
                        break
                elif arm_is_switch_add(insn):
                    count = self._switch_count(info, pc, insn)
                    table = pc + 8
                    if count is None:
                        count = 0
                        while table + count * 4 < limit and arm_is_b(
                            read32(table + count * 4)
                        ):
                            count += 1
                    for i in range(count):
                        work.append(table + i * 4)
                elif arm_dp_writes_pc(insn):
                    if always:
                        break
                elif arm_is_adr(insn):
                    target = arm_adr_target(pc, insn)
                    if start <= target < limit:
                        info.adr_targets.add(target)
                pc += 4

    def _switch_ldr(self, info: FunctionInfo, pc: int, insn: int, work: List[int]) -> None:
        start, limit = info.start, info.limit
        table = pc + 8
        count = self._switch_count(info, pc, insn)
        if count is None:
            count = (limit - table) // 4
            exact = False
        else:
            exact = True
        # Guard against a bad count running off into code
        valid = 0
        for i in range(count):
            if table + i * 4 >= limit:
                break
            entry = self.read32(table + i * 4)
            if not (start <= entry < limit) or entry & 3:
                break
            valid += 1
        if exact and valid != count:
            info.suspicious = True
        info.switches.append(SwitchTable(pc + 4, table, valid))
        for i in range(valid):
            info.data_words.add(table + i * 4)
            work.append(self.read32(table + i * 4))

    # Thumb

    def _walk_thumb(self, info: FunctionInfo) -> None:
        work = [info.start]
        start, limit = info.start, info.limit
        while work:
            pc = work.pop()
            while start <= pc < limit and pc not in info.code:
                if info.is_data(pc):
                    break
                insn = self.read16(pc)

                if thumb_is_bl_prefix(insn):
                    lo = self.read16(pc + 2) if pc + 2 < limit else 0
                    if thumb_is_bl_suffix(lo) or thumb_is_blx_suffix(lo):
                        target = thumb_bl_target(pc, insn, lo)
                        info.code.add(pc)
                        info.code.add(pc + 2)
                        info.branches.append(
                            BranchRef(
                                pc, target, thumb_is_bl_suffix(lo), KIND_CALL, True
                            )
                        )
                        pc += 4
                        continue
                    info.suspicious = True
                    break

                if (insn & 0xE800) == 0xE800 or thumb_is_undefined(insn):
                    # A BL suffix on its own, or an encoding ARMv6K does not have
                    info.suspicious = True
                    break
                info.code.add(pc)

                if thumb_is_b(insn) or thumb_is_bcond(insn):
                    target = thumb_branch_target(pc, insn)
                    internal = start <= target < limit and (
                        target == start or not self.is_function(target)
                    )
                    if internal:
                        work.append(target)
                    else:
                        info.branches.append(
                            BranchRef(pc, target, True, KIND_JUMP, True)
                        )
                    if thumb_is_b(insn):
                        break
                    pc += 2
                    continue

                if thumb_is_ldr_literal(insn):
                    target = thumb_ldr_literal_target(pc, insn)
                    if start <= target < limit:
                        info.add_pool(target, 4)
                        info.ldr_pool.add(target)
                    else:
                        info.suspicious = True
                    pc += 2
                    continue

                if thumb_is_adr(insn):
                    target = ((pc + 4) & ~3) + ((insn & 0xFF) << 2)
                    if start <= target < limit:
                        info.adr_targets.add(target)
                    pc += 2
                    continue

                if thumb_is_pop_pc(insn) or thumb_is_bx(insn) or thumb_is_mov_pc(insn):
                    break

                pc += 2
