"""IFO parsing utilities."""

import os
import struct
import typing

import attrs


@attrs.define
class BinaryStream:
    """Utility for parsing bytes from a binary stream."""

    inbytes: typing.BinaryIO
    endian_marker: str = ">"

    def unpack(self, spec: str) -> tuple:
        """Unpack values from the stream with a struct format spec."""
        # B = 1
        # H = 2
        # I = 4
        # Q = 8
        spec = f"{self.endian_marker}{spec}"
        return struct.unpack(spec, self.get_bytes(struct.calcsize(spec)))

    def get_bytes(self, size: int) -> bytes:
        """Get raw bytes from the stream."""
        return self.inbytes.read(size)

    def skip_bytes(self, size: int):
        """Skip forward without reading bytes."""
        self.inbytes.seek(size, os.SEEK_CUR)

    def seek(self, pos: int):
        """Seek to a specific position."""
        self.inbytes.seek(pos, os.SEEK_SET)

    def tell(self) -> int:
        """Get current cursor position."""
        return self.inbytes.tell()
