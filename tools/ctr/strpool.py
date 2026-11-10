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
        offset = 0
        while offset < self.size:
            end = self.find_terminator(self.data, offset, self.char_size)
            if end is None:
                raise ValueError(
                    f"string pool {self.name} does not end with a terminator: check its size in the config"
                )
            self.entries.append((self.address + offset, self.data[offset:end]))
            offset = end + self.char_size
        self._whole: Dict[bytes, int] = {}
        for address, contents in self.entries:
            self._whole.setdefault(contents, address)
        self._located: Dict[bytes, Optional[int]] = {}

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

    def string_at(self, address: int) -> bytes:
        """Contents of the string that starts at `address`, without its terminator."""
        offset = address - self.address
        end = self.find_terminator(self.data, offset, self.char_size)
        assert end is not None
        return self.data[offset:end]

    def describe(self, contents: bytes) -> str:
        if self.char_size == 2:
            return repr(contents.decode("utf-16-le", "replace"))
        return repr(contents.decode("shift_jis", "replace"))
