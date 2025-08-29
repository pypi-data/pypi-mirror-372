from __future__ import annotations

import fcntl
import io
import logging
import struct
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Generator

from contextlib import suppress

from labels.parsers.cataloger.redhat.rpmdb.rpmdb_interface import RpmDBInterface
from labels.utils.exceptions import InvalidDBFormatError

# Constants
NDB_SLOT_ENTRIES_PER_PAGE = 4096 // 16  # 16 bytes per ndbSlotEntry
NDB_HEADER_MAGIC = ord("R") | (ord("p") << 8) | (ord("m") << 16) | (ord("P") << 24)
NDB_DB_VERSION = 0
LOGGER = logging.getLogger(__name__)


def syscall_flock(fd: int, how: int) -> None:
    fcntl.flock(fd, how)


# Struct formats
NDB_HEADER_STRUCT = struct.Struct("<8I")  # 8 unsigned 32-bit integers
NDB_SLOT_ENTRY_STRUCT = struct.Struct("<4I")  # 4 unsigned 32-bit integers
NDB_BLOB_HEADER_STRUCT = struct.Struct("<4I")  # 4 unsigned 32-bit integers


class RpmNDB(RpmDBInterface):
    def __init__(self, file: io.BufferedReader, slots: list[dict[str, int]]) -> None:
        self.file = file
        self.slots = slots

    @classmethod
    def open(cls, path: str) -> RpmNDB:
        file = Path(path).open("rb")  # noqa: SIM115
        try:
            syscall_flock(file.fileno(), fcntl.LOCK_SH)
        except Exception as exc:
            file.close()
            raise exc  # noqa: TRY201

        # Read NDB header
        hdr_data = file.read(NDB_HEADER_STRUCT.size)
        if len(hdr_data) != NDB_HEADER_STRUCT.size:
            file.close()
            error_msg = "Failed to read metadata"
            raise InvalidDBFormatError(error_msg)

        hdr_fields = NDB_HEADER_STRUCT.unpack(hdr_data)
        hdr = {
            "HeaderMagic": hdr_fields[0],
            "NDBVersion": hdr_fields[1],
            "NDBGeneration": hdr_fields[2],
            "SlotNPages": hdr_fields[3],
            # Remaining fields are ignored
        }

        if (
            hdr["HeaderMagic"] != NDB_HEADER_MAGIC
            or hdr["SlotNPages"] == 0
            or hdr["NDBVersion"] != NDB_DB_VERSION
        ):
            file.close()
            error_msg = "Invalid or unsupported NDB format"
            raise InvalidDBFormatError(error_msg)

        if hdr["SlotNPages"] > 2048:
            file.close()
            error_msg = f"Slot page limit exceeded: {hdr['SlotNPages']:x}"
            raise InvalidDBFormatError(error_msg)

        # Read slot entries
        num_slots = hdr["SlotNPages"] * NDB_SLOT_ENTRIES_PER_PAGE - 2  # First two slots are headers
        slots_data = file.read(num_slots * NDB_SLOT_ENTRY_STRUCT.size)
        if len(slots_data) != num_slots * NDB_SLOT_ENTRY_STRUCT.size:
            file.close()
            error_msg = "Failed to read NDB slot pages"
            raise InvalidDBFormatError(error_msg)

        slots = []
        for i in range(num_slots):
            slot_data = slots_data[
                i * NDB_SLOT_ENTRY_STRUCT.size : (i + 1) * NDB_SLOT_ENTRY_STRUCT.size
            ]
            slot_fields = NDB_SLOT_ENTRY_STRUCT.unpack(slot_data)
            slot = {
                "SlotMagic": slot_fields[0],
                "PkgIndex": slot_fields[1],
                "BlkOffset": slot_fields[2],
                "BlkCount": slot_fields[3],
            }
            slots.append(slot)

        return cls(file, slots)

    def close(self) -> None:
        with suppress(Exception):
            syscall_flock(self.file.fileno(), fcntl.LOCK_UN)
        self.file.close()

    def read(self) -> Generator[bytes, None, None]:
        ndb_slot_magic = ord("S") | (ord("l") << 8) | (ord("o") << 16) | (ord("t") << 24)
        ndb_blob_magic = ord("B") | (ord("l") << 8) | (ord("b") << 16) | (ord("S") << 24)

        for slot in self.slots:
            if slot["SlotMagic"] != ndb_slot_magic:
                LOGGER.error("Bad slot magic %s", slot["SlotMagic"])
                return
            # Empty slot?
            if slot["PkgIndex"] == 0:
                continue
            # Seek to Blob
            offset = slot["BlkOffset"] * NDB_BLOB_HEADER_STRUCT.size
            try:
                self.file.seek(offset, io.SEEK_SET)
            except OSError:
                LOGGER.exception("Failed to seek to blob")
                return

            # Read Blob Header
            blob_header_data = self.file.read(NDB_BLOB_HEADER_STRUCT.size)
            if len(blob_header_data) != NDB_BLOB_HEADER_STRUCT.size:
                LOGGER.error("Failed to read blob header")
                return
            blob_header_fields = NDB_BLOB_HEADER_STRUCT.unpack(blob_header_data)
            blob_header = {
                "BlobMagic": blob_header_fields[0],
                "PkgIndex": blob_header_fields[1],
                "BlobCkSum": blob_header_fields[2],
                "BlobLen": blob_header_fields[3],
            }
            if blob_header["BlobMagic"] != ndb_blob_magic:
                LOGGER.error(
                    "Unexpected NDB blob Magic for pkg %s: %s",
                    slot["PkgIndex"],
                    blob_header["BlobMagic"],
                )
                return
            if blob_header["PkgIndex"] != slot["PkgIndex"]:
                LOGGER.error("Failed to find NDB blob for pkg %s", slot["PkgIndex"])
                return

            # Read Blob Content
            blob_len = blob_header["BlobLen"]
            blob_entry = self.file.read(blob_len)
            if len(blob_entry) != blob_len:
                LOGGER.error("Failed to read blob content")
                return
            yield blob_entry
