"""
Merged string pools.

The compiler puts string literals that are referenced from data in `.conststring`
(and wide ones in `.constwstring`). Those sections are flagged as mergeable, and
armlink merged all of them across the whole program into one pool per section name:

  - a string is stored once, no matter how many source files use it
  - a string that is the tail of another string is not stored at all. It points
    into the longer one ("wait" lives inside "bg_wait")

So the strings of a source file are not a block of the image that could be placed
somewhere. Instead the address of a string is found by looking its contents up in
the pool of the original image, following the choices armlink made.

The pool is not always packed: the strings of a section with 4-byte alignment stay
4-byte aligned (zero padding after the terminator), and armlink fills the gaps
between input sections with 0xFF. Padding is skipped and is not a string.
"""

from typing import Dict, List, Optional, Tuple

from .image import Image, StringPoolDef


class StringPool:
    def __init__(self, image: Image, definition: StringPoolDef) -> None:
        self.name = definition.section
        self.address = definition.address
        self.size = definition.size
        self.char_size = definition.char_size
        self.end = self.address + self.size
        self.data = image.read(self.address, self.size)
        if len(self.data) != self.size or self.size % self.char_size:
            raise ValueError(f"string pool {self.name} does not lie within the image")

        # (address, contents without terminator)
        self.entries: List[Tuple[int, bytes]] = []
        # Offsets of the code units that belong to a string (its characters and terminator)
        self._in_string = bytearray(self.size // self.char_size)
        offset = 0
        while offset < self.size:
            if self._is_padding(offset):
                offset += self.char_size
                continue
            end = self.find_terminator(self.data, offset, self.char_size)
            if end is None:
                raise ValueError(
                    f"string pool {self.name} does not end with a terminator: check its size in the config"
                )
            self.entries.append((self.address + offset, self.data[offset:end]))
            for unit in range(offset // self.char_size, end // self.char_size + 1):
                self._in_string[unit] = 1
            offset = end + self.char_size
        self._whole: Dict[bytes, int] = {}
        for address, contents in self.entries:
            self._whole.setdefault(contents, address)
        self._located: Dict[bytes, Optional[int]] = {}

    def _is_padding(self, offset: int) -> bool:
        """A code unit between strings: a zero (alignment) or 0xFF (armlink's fill)."""
        unit = self.data[offset : offset + self.char_size]
        return unit == bytes(self.char_size) or unit == b"\xff" * self.char_size

    @staticmethod
    def find_terminator(data: bytes, offset: int, char_size: int) -> Optional[int]:
        """Offset of the terminator of the string that starts at `offset`."""
        if char_size == 1:
            end = data.find(b"\0", offset)
            return end if end >= 0 else None
        terminator = bytes(char_size)
        while offset + char_size <= len(data):
            if data[offset : offset + char_size] == terminator:
                return offset
            offset += char_size
        return None

    @staticmethod
    def literal_containing(data: bytes, offset: int, char_size: int) -> Tuple[int, int]:
        """
        Start and end (offset of the terminator) of the literal of a compiled string
        section that `offset` falls into; a section that ends without a terminator
        ends its last literal.
        """
        start = 0
        while True:
            end = StringPool.find_terminator(data, start, char_size)
            if end is None:
                return start, len(data)
            if offset <= end:
                return start, end
            start = end + char_size

    def contains(self, address: int) -> bool:
        return self.address <= address < self.end

    def _reversed(self, contents: bytes) -> Tuple[int, ...]:
        """Characters of a string from last to first."""
        size = self.char_size
        return tuple(
            int.from_bytes(contents[i : i + size], "little")
            for i in range(len(contents) - size, -1, -size)
        )

    def locate(self, contents: bytes) -> Optional[int]:
        """
        Address of a string (given without its terminator) in the pool.

        A string that only exists as the tail of other strings is inside the one that
        comes last when the candidates are ordered by their characters read backwards.
        That is what merging tails by sorting reversed strings produces, and it holds
        for every such string in the original image.
        """
        if contents in self._located:
            return self._located[contents]
        address = self._whole.get(contents)
        if address is None:
            hosts = [
                (self._reversed(host), host_address + len(host) - len(contents))
                for host_address, host in self.entries
                if len(host) > len(contents) and host.endswith(contents)
            ]
            if hosts:
                address = max(hosts)[1]
        self._located[contents] = address
        return address

    def string_at(self, address: int) -> Optional[bytes]:
        """
        Contents of the string that starts at `address`, without its terminator, or
        None if `address` is padding. An address on a terminator is the empty string
        that ends the string before it.
        """
        offset = address - self.address
        if not (0 <= offset < self.size) or offset % self.char_size:
            return None
        if not self._in_string[offset // self.char_size]:
            return None
        end = self.find_terminator(self.data, offset, self.char_size)
        assert end is not None
        return self.data[offset:end]

    def describe(self, contents: bytes) -> str:
        if self.char_size == 2:
            return repr(contents.decode("utf-16-le", "replace"))
        return repr(contents.decode("shift_jis", "replace"))
