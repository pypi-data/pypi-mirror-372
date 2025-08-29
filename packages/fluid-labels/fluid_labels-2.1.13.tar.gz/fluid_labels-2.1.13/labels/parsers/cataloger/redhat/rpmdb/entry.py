import struct

from pydantic import BaseModel

from labels.parsers.cataloger.redhat.rpmdb.inet import htonl, htonlu
from labels.parsers.cataloger.redhat.rpmdb.rpmtags import (
    HEADER_I18NTABLE,
    RPM_BIN_TYPE,
    RPM_I18NSTRING_TYPE,
    RPM_MAX_TYPE,
    RPM_MIN_TYPE,
    RPM_STRING_ARRAY_TYPE,
    RPM_STRING_TYPE,
    RPMTAG_HEADERI18NTABLE,
    RPMTAG_HEADERIMAGE,
    RPMTAG_HEADERIMMUTABLE,
    RPMTAG_HEADERSIGNATURES,
)

REGION_TAG_COUNT = 16
REGION_TAG_TYPE = RPM_BIN_TYPE

HEADER_MAX_BYTES = 256 * 1024 * 1024

TYPE_SIZES = [
    0,  # RPM_NULL_TYPE
    1,  # RPM_CHAR_TYPE
    1,  # RPM_INT8_TYPE
    2,  # RPM_INT16_TYPE
    4,  # RPM_INT32_TYPE
    8,  # RPM_INT64_TYPE
    -1,  # RPM_STRING_TYPE
    1,  # RPM_BIN_TYPE
    -1,  # RPM_STRING_ARRAY_TYPE
    -1,  # RPM_I18NSTRING_TYPE
    0,
    0,
    0,
    0,
    0,
    0,
]

TYPE_ALIGN = [
    1,  # RPM_NULL_TYPE
    1,  # RPM_CHAR_TYPE
    1,  # RPM_INT8_TYPE
    2,  # RPM_INT16_TYPE
    4,  # RPM_INT32_TYPE
    8,  # RPM_INT64_TYPE
    1,  # RPM_STRING_TYPE
    1,  # RPM_BIN_TYPE
    1,  # RPM_STRING_ARRAY_TYPE
    1,  # RPM_I18NSTRING_TYPE
    0,
    0,
    0,
    0,
    0,
    0,
]


class EntryInfo(BaseModel):
    tag: int  # int32 in Go
    type: int  # uint32 in Go
    offset: int  # int32 in Go
    count: int  # uint32 in Go


class IndexEntry(BaseModel):
    info: EntryInfo
    length: int
    rd_len: int
    data: bytes


class HdrBlob(BaseModel):
    pe_list: list[EntryInfo]  # List of `EntryInfo`
    i_length: int  # int32 in Go
    d_length: int  # int32 in Go
    pv_len: int  # int32 in Go
    data_start: int  # int32 in Go
    data_end: int  # int32 in Go
    region_tag: int  # int32 in Go
    ril: int  # int32 in Go
    rdl: int  # int32 in Go


def hdrchk_range(d_length: int, offset: int) -> bool:
    return offset < 0 or offset > d_length


def hdrchk_tag(tag: int) -> bool:
    return tag < HEADER_I18NTABLE


def hdrchk_type(type_: int) -> bool:
    return type_ < RPM_MIN_TYPE or type_ > RPM_MAX_TYPE


def hdrchk_align(type_: int, offset: int) -> bool:
    return offset & (TYPE_ALIGN[type_] - 1) != 0


def ei2h(package_entry: EntryInfo) -> EntryInfo:
    return EntryInfo(
        type=htonlu(package_entry.type),  # Convert unsigned 32-bit integer to network byte order
        count=htonlu(package_entry.count),  # Convert unsigned 32-bit integer to network byte order
        offset=htonl(package_entry.offset),  # Convert signed 32-bit integer to network byte order
        tag=htonl(package_entry.tag),  # Convert signed 32-bit integer to network byte order
    )


def data_length(data: bytes, type_: int, count: int, data_start: int, data_end: int) -> int:
    length = 0

    if type_ == RPM_STRING_TYPE:
        if count != 1:
            return -1
        length = strtaglen(data, 1, data_start, data_end)
    elif type_ in [RPM_STRING_ARRAY_TYPE, RPM_I18NSTRING_TYPE]:
        length = strtaglen(data, count, data_start, data_end)
    else:
        if TYPE_SIZES[type_] == -1:
            return -1
        length = TYPE_SIZES[type_ & 0xF] * count
        if length < 0 or data_end > 0 < data_start + length - data_end:
            return -1

    return length


def strtaglen(data: bytes, count: int, dat_start: int, data_end: int) -> int:
    length = 0
    if dat_start >= data_end or data_end > len(data):
        return -1

    for _ in range(count):
        offset = dat_start + length
        if offset > len(data):
            return -1
        try:
            index = data[offset:data_end].index(0x00)
        except ValueError:
            # Null terminator not found within the specified bounds
            return -1
        length += index + 1  # Include the null terminator

    return length


def align_diff(type_: int, align_size: int) -> int:
    type_size = TYPE_SIZES[type_]
    if type_size > 1:
        diff = type_size - (align_size % type_size)
        if diff != type_size:
            return diff
    return 0


def region_swab(
    data: bytes,
    pe_list: list[EntryInfo],
    d_length: int,
    data_start: int,
    data_end: int,
) -> tuple[list[IndexEntry], int]:
    index_entries = []

    for index, pkg_entry in enumerate(pe_list):
        index_entry = IndexEntry(info=ei2h(pkg_entry), length=0, rd_len=0, data=b"")

        # Calculate start offset
        start = data_start + index_entry.info.offset
        if start >= data_end:
            error_msg = "Invalid data offset"
            raise ValueError(error_msg)

        # Calculate length for the current index entry
        if index < len(pe_list) - 1 and TYPE_SIZES[index_entry.info.type] == -1:
            index_entry.length = htonl(pe_list[index + 1].offset) - index_entry.info.offset
        else:
            index_entry.length = data_length(
                data,
                index_entry.info.type,
                index_entry.info.count,
                start,
                data_end,
            )

        if index_entry.length < 0:
            error_msg = "Invalid data length"
            raise ValueError(error_msg)

        # Calculate the end index
        end = start + index_entry.length
        if start > len(data) or end > len(data):
            error_msg = "Invalid data length"
            raise ValueError(error_msg)

        # Extract the data from the byte array
        index_entry.data = data[start:end]
        index_entries.append(index_entry)

        # Update data length (dl) with alignment
        d_length += index_entry.length + align_diff(index_entry.info.type, d_length)

    return index_entries, d_length


def hdrblob_verify_info(
    blob: HdrBlob,
    data: bytes,
) -> None:
    end = 0
    pe_offset = 0
    if blob.region_tag != 0:
        pe_offset = 1

    for pkg_entry in blob.pe_list[pe_offset:]:
        info = ei2h(pkg_entry)

        if end > info.offset:
            error_msg = f"Invalid offset info: {info}"
            raise ValueError(error_msg)

        if hdrchk_tag(info.tag):
            error_msg = f"Invalid tag info: {info}"
            raise ValueError(error_msg)

        if hdrchk_type(info.type):
            error_msg = f"Invalid type info: {info}"
            raise ValueError(error_msg)

        if hdrchk_align(info.type, info.offset):
            error_msg = f"invalid align info: {info}"
            raise ValueError(error_msg)

        if hdrchk_range(blob.d_length, info.offset):
            error_msg = f"Invalid range info: {info}"
            raise ValueError(error_msg)

        length = data_length(
            data,
            info.type,
            info.count,
            blob.data_start + info.offset,
            blob.data_end,
        )
        end = info.offset + length
        if hdrchk_range(blob.d_length, end) or length <= 0:
            error_msg = f"Invalid data length info: {info}"
            raise ValueError(error_msg)


def hdrblob_import(blob: HdrBlob, data: bytes) -> list[IndexEntry]:
    index_entries: list[IndexEntry] = []
    dribble_index_entries: list[IndexEntry] = []

    # Parse the first entry
    entry = ei2h(blob.pe_list[0])

    # Handle v3 legacy headers
    if entry.tag >= RPMTAG_HEADERI18NTABLE:
        # v3 header, create a legacy region entry
        index_entries, rdlen = region_swab(data, blob.pe_list, 0, blob.data_start, blob.data_end)
    else:
        # v4 header or "upgraded" v3 header with legacy region
        ril = blob.ril
        if entry.offset == 0:
            ril = blob.i_length

        # Process region entries
        index_entries, rdlen = region_swab(
            data,
            blob.pe_list[1:ril],
            0,
            blob.data_start,
            blob.data_end,
        )
        if rdlen < 0:
            error_msg = "Invalid region length"
            raise ValueError(error_msg)

        # Process dribble entries if present
        if blob.ril < len(blob.pe_list) - 1:
            dribble_index_entries, rdlen = region_swab(
                data,
                blob.pe_list[ril:],
                rdlen,
                blob.data_start,
                blob.data_end,
            )
            if rdlen < 0:
                error_msg = "Invalid length of dribble entries"
                raise ValueError(error_msg)

            # Merge index entries and dribble entries into a unique tag map
            uniq_tag_map = {
                index_entry.info.tag: index_entry
                for index_entry in index_entries + dribble_index_entries
            }

            # Collect unique index entries
            index_entries = list(uniq_tag_map.values())

        # Add REGION_TAG_COUNT to rdlen
        rdlen += REGION_TAG_COUNT

    # Check if the calculated length matches the data length
    if rdlen != blob.d_length:
        error_msg = (
            f"The calculated length ({rdlen}) is different from the data length ({blob.d_length})"
        )
        raise ValueError(error_msg)

    return index_entries


def hdrblob_verify_region(blob: HdrBlob, data: bytes) -> None:
    einfo = ei2h(blob.pe_list[0])
    region_tag = _get_region_tag(einfo)

    if einfo.tag != region_tag:
        return

    _validate_region_tag(einfo)
    _check_region_offset(blob, einfo)
    _parse_and_validate_trailer(blob, data, einfo, region_tag)
    _process_trailer_and_update_blob(blob, data)


def _get_region_tag(einfo: EntryInfo) -> int:
    if einfo.tag in {
        RPMTAG_HEADERIMAGE,
        RPMTAG_HEADERSIGNATURES,
        RPMTAG_HEADERIMMUTABLE,
    }:
        return einfo.tag
    return 0


def _validate_region_tag(einfo: EntryInfo) -> None:
    if not (einfo.type == REGION_TAG_TYPE and einfo.count == REGION_TAG_COUNT):
        error_msg = "Invalid region tag"
        raise ValueError(error_msg)


def _check_region_offset(blob: HdrBlob, einfo: EntryInfo) -> None:
    if hdrchk_range(blob.d_length, einfo.offset + REGION_TAG_COUNT):
        error_msg = "Invalid region offset"
        raise ValueError(error_msg)


def _parse_and_validate_trailer(
    blob: HdrBlob,
    data: bytes,
    einfo: EntryInfo,
    region_tag: int,
) -> None:
    region_end = blob.data_start + einfo.offset
    if region_end > len(data) or region_end + REGION_TAG_COUNT > len(data):
        error_msg = "Invalid region offset"
        raise ValueError(error_msg)

    trailer_data = data[region_end : region_end + REGION_TAG_COUNT]
    try:
        result = struct.unpack("<iIiI", trailer_data)
        EntryInfo(tag=result[0], type=result[1], offset=result[2], count=result[3])
    except struct.error as exc:
        error_msg = "Failed to parse trailer"
        raise ValueError(error_msg) from exc

    blob.rdl = region_end + REGION_TAG_COUNT - blob.data_start

    if region_tag == RPMTAG_HEADERSIGNATURES and einfo.tag == RPMTAG_HEADERIMAGE:
        einfo.tag = RPMTAG_HEADERSIGNATURES

    if not (
        einfo.tag == region_tag
        and einfo.type == REGION_TAG_TYPE
        and einfo.count == REGION_TAG_COUNT
    ):
        error_msg = "Invalid region trailer"
        raise ValueError(error_msg)


def _process_trailer_and_update_blob(blob: HdrBlob, data: bytes) -> None:
    result = struct.unpack(
        "<iIiI",
        data[blob.data_start + blob.rdl - REGION_TAG_COUNT : blob.data_start + blob.rdl],
    )
    trailer = EntryInfo(tag=result[0], type=result[1], offset=result[2], count=result[3])
    einfo = ei2h(trailer)
    einfo.offset = -einfo.offset
    blob.ril = einfo.offset // struct.calcsize("<iIiI")

    if (
        einfo.offset % REGION_TAG_COUNT != 0
        or hdrchk_range(blob.i_length, blob.ril)
        or hdrchk_range(blob.d_length, blob.rdl)
    ):
        error_msg = f"Invalid region size, region {blob.region_tag}"
        raise ValueError(error_msg)

    blob.region_tag = blob.pe_list[0].tag


def hdrblob_init(data: bytes) -> HdrBlob | None:
    try:
        blob = _create_hdrblob(data)
        _calculate_blob_fields(blob)
        _read_pe_list(blob, data)
        _verify_blob(blob, data)
    except ValueError as exc:
        error_msg = "Failed to initialize header blob"
        raise ValueError(error_msg) from exc
    else:
        return blob


def _create_hdrblob(data: bytes) -> HdrBlob:
    reader = struct.Struct(">I")
    (ideal_length,) = reader.unpack_from(data, 0)
    (d_length,) = reader.unpack_from(data, 4)
    return HdrBlob(
        pe_list=[],
        i_length=ideal_length,
        d_length=d_length,
        pv_len=0,
        data_start=0,
        data_end=0,
        region_tag=0,
        ril=0,
        rdl=0,
    )


def _calculate_blob_fields(blob: HdrBlob) -> None:
    entry_info_size = struct.calcsize("<iIiI")
    blob.data_start = 4 + 4 + blob.i_length * entry_info_size
    blob.pv_len = blob.data_start + blob.d_length
    blob.data_end = blob.data_start + blob.d_length
    if blob.i_length < 1:
        error_msg = "Region no tags error"
        raise ValueError(error_msg)


def _read_pe_list(blob: HdrBlob, data: bytes) -> None:
    entry_info_size = struct.calcsize("<iIiI")
    offset = 8
    for _ in range(blob.i_length):
        entry_info_data = data[offset : offset + entry_info_size]
        if len(entry_info_data) < entry_info_size:
            error_msg = "Failed to read entry info: incomplete data"
            raise ValueError(error_msg)
        pkg_entry = struct.unpack("<iIiI", entry_info_data)
        blob.pe_list.append(
            EntryInfo(
                tag=pkg_entry[0],
                type=pkg_entry[1],
                offset=pkg_entry[2],
                count=pkg_entry[3],
            ),
        )
        offset += entry_info_size
    if blob.pv_len >= HEADER_MAX_BYTES:
        error_msg = (
            f"Blob size({blob.pv_len}) BAD, 8 + 16 * il({blob.i_length}) + dl({blob.d_length})"
        )
        raise ValueError(error_msg)


def _verify_blob(blob: HdrBlob, data: bytes) -> None:
    hdrblob_verify_region(blob, data)
    hdrblob_verify_info(blob, data)


def header_import(data: bytes) -> list[IndexEntry] | None:
    def _validate_blob(blob: HdrBlob | None) -> HdrBlob:
        if blob is None:
            error_msg = "Failed to initialize header blob"
            raise ValueError(error_msg)
        return blob

    try:
        # Initialize the hdrblob from the data
        blob = _validate_blob(hdrblob_init(data))
        return hdrblob_import(blob, data)

    except ValueError as exc:
        error_msg = "Header import failed"
        raise ValueError(error_msg) from exc
