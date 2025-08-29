import io
import struct

from pydantic import (
    BaseModel,
)

from labels.parsers.cataloger.redhat.rpmdb.berkeley.constants import (
    HASH_INDEX_ENTRY_SIZE,
    HASH_OF_INDEX_PAGE_TYPE,
    HASH_OFF_PAGE_SIZE,
    OVERFLOW_PAGE_TYPE,
    PAGE_HEADER_SIZE,
)
from labels.parsers.cataloger.redhat.rpmdb.berkeley.hash_page_entry import (
    parse_hash_off_page_entry,
)


class HashPage(BaseModel):
    """Represents a Hash Page in the RPM database."""

    lsn: bytes  # 8 bytes
    page_no: int  # uint32
    previous_page_no: int  # uint32
    next_page_no: int  # uint32
    num_entries: int  # uint16
    free_area_offset: int  # uint16
    tree_level: int  # uint8
    page_type: int  # uint8

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        *,
        swapped: bool,
    ) -> "HashPage":
        expected_size = 26  # Total size in bytes for HashPage header
        if len(data) < expected_size:
            error_msg = (
                f"Data too short, expected at least {expected_size} bytes, got {len(data)} bytes"
            )
            raise ValueError(error_msg)

        byte_order_char = ">" if swapped else "<"

        fmt = f"{byte_order_char}8sIIIHHBB"
        try:
            unpacked_data = struct.unpack(fmt, data[:expected_size])
        except struct.error as exc:
            error_msg = "Failed to unpack HashPage"
            raise ValueError(error_msg) from exc

        (
            lsn,
            page_no,
            previous_page_no,
            next_page_no,
            num_entries,
            free_area_offset,
            tree_level,
            page_type,
        ) = unpacked_data

        return cls(
            lsn=lsn,
            page_no=page_no,
            previous_page_no=previous_page_no,
            next_page_no=next_page_no,
            num_entries=num_entries,
            free_area_offset=free_area_offset,
            tree_level=tree_level,
            page_type=page_type,
        )

    def __repr__(self) -> str:
        return (
            f"HashPage(LSN={self.lsn.hex()}, PageNo={self.page_no},"
            f" PreviousPageNo={self.previous_page_no},"
            f" NextPageNo={self.next_page_no}, NumEntries={self.num_entries},"
            f" FreeAreaOffset={self.free_area_offset},"
            f" TreeLevel={self.tree_level}, PageType={self.page_type})"
        )


def parse_hash_page(data: bytes, *, swapped: bool) -> HashPage:
    return HashPage.from_bytes(data, swapped=swapped)


def hash_page_value_content(
    db_file: io.BufferedReader,
    page_data: bytes,
    hash_page_index: int,
    page_size: int,
    *,
    swapped: bool,
) -> bytes:
    # The first byte is the page type
    value_page_type = page_data[hash_page_index]

    # Only HOFFPAGE page types have data of interest
    if value_page_type != HASH_OF_INDEX_PAGE_TYPE:
        error_msg = f"Only HOFFPAGE types supported (got {value_page_type})"
        raise ValueError(error_msg)

    hash_off_page_entry_buff = page_data[hash_page_index : hash_page_index + HASH_OFF_PAGE_SIZE]

    entry = parse_hash_off_page_entry(hash_off_page_entry_buff, swapped=swapped)

    hash_value = bytearray()

    current_page_no = entry.page_no
    while current_page_no != 0:
        page_start = page_size * current_page_no

        db_file.seek(page_start)
        current_page_buff = db_file.read(page_size)
        if len(current_page_buff) != page_size:
            error_msg = f"Failed to read page {current_page_no}: insufficient data"
            raise ValueError(error_msg)

        current_page = parse_hash_page(current_page_buff, swapped=swapped)
        if current_page.page_type != OVERFLOW_PAGE_TYPE:
            current_page_no = current_page.next_page_no
            continue

        if current_page.next_page_no == 0:
            # This is the last page, the content length is FreeAreaOffset
            data_length = current_page.free_area_offset
            hash_value_bytes = current_page_buff[PAGE_HEADER_SIZE : PAGE_HEADER_SIZE + data_length]
        else:
            # For intermediate pages, use all data after header
            hash_value_bytes = current_page_buff[PAGE_HEADER_SIZE:]

        hash_value.extend(hash_value_bytes)

        current_page_no = current_page.next_page_no

    return bytes(hash_value)


def hash_page_value_indexes(data: bytes, entries: int, *, swapped: bool) -> list:
    if entries % 2 != 0:
        error_msg = f"Invalid hash index: entries should only come in pairs (got {entries})"
        raise ValueError(error_msg)

    order_char = ">" if swapped else "<"

    hash_index_values = []

    # Every entry is a 2-byte offset that points somewhere in the current
    # database page.
    hash_index_size = entries * HASH_INDEX_ENTRY_SIZE
    hash_index_data = data[PAGE_HEADER_SIZE : PAGE_HEADER_SIZE + hash_index_size]

    # Data is stored in key-value pairs, skip over keys and only keep values
    key_value_pair_size = 2 * HASH_INDEX_ENTRY_SIZE

    for idx in range(0, len(hash_index_data), HASH_INDEX_ENTRY_SIZE):
        if (idx - HASH_INDEX_ENTRY_SIZE) % key_value_pair_size == 0:
            # This is a value index
            value_bytes = hash_index_data[idx : idx + HASH_INDEX_ENTRY_SIZE]
            if len(value_bytes) < HASH_INDEX_ENTRY_SIZE:
                error_msg = f"Insufficient data at index {idx}"
                raise ValueError(error_msg)
            value = struct.unpack(f"{order_char}H", value_bytes)[0]
            hash_index_values.append(value)

    return hash_index_values


def slice_reader(reader: io.BufferedReader, num: int) -> bytes:
    """Read n bytes from a reader.

    :param reader: A file-like object to read from.
    :param n: Number of bytes to read.
    :return: The bytes read.
    :raises ValueError: If the number of bytes read is less than n.
    """
    data = reader.read(num)
    if len(data) != num:
        error_msg = f"Failed to read {num} bytes, got {len(data)} bytes"
        raise ValueError(error_msg)
    return data
