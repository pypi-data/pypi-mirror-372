from __future__ import (
    annotations,
)

import struct


class HashOffPageEntry:
    def __init__(self, page_type: int, unused: int, page_no: int, length: int) -> None:
        self.page_type = page_type  # uint8
        self.unused = unused  # 3 bytes
        self.page_no = page_no  # uint32
        self.length = length  # uint32

    @classmethod
    def from_bytes(cls, data: bytes, *, swapped: bool) -> HashOffPageEntry:
        expected_size = 12  # Total size in bytes
        if len(data) < expected_size:
            error_msg = (
                f"Data too short, expected at least {expected_size} bytes, got {len(data)} bytes"
            )
            raise ValueError(error_msg)

        # Determine the byte order
        byte_order_str = ">" if swapped else "<"  # '>' for big-endian, '<' for little-endian

        # Struct format string
        fmt = f"{byte_order_str}B3sII"  # Format: PageType(uint8),
        # Unused(3 bytes), PageNo(uint32), Length(uint32)

        try:
            unpacked_data = struct.unpack(fmt, data[:expected_size])
        except struct.error as exc:
            error_msg = f"Failed to unpack HashOffPageEntry: {exc}"
            raise ValueError(error_msg) from exc

        page_type, unused, page_no, length = unpacked_data

        return cls(page_type, unused, page_no, length)

    def __repr__(self) -> str:
        return (
            f"HashOffPageEntry("
            f"PageType={self.page_type}, Unused={self.unused}, "
            f"PageNo={self.page_no}, Length={self.length})"
        )


def parse_hash_off_page_entry(data: bytes, *, swapped: bool) -> HashOffPageEntry:
    return HashOffPageEntry.from_bytes(data, swapped=swapped)
