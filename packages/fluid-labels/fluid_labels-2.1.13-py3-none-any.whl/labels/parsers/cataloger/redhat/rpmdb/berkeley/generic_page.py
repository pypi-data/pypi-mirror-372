from __future__ import (
    annotations,
)

import struct

from pydantic import (
    BaseModel,
)


class GenericMetadataPage(BaseModel):
    lsn: bytes
    page_no: int
    magic: int
    version: int
    page_size: int
    encryption_alg: int
    page_type: int
    meta_flags: int
    unused_1: int
    free: int
    last_page_no: int
    n_parts: int
    key_count: int
    record_count: int
    flags: bytes
    unique_file_id: int | None = None

    @classmethod
    def from_bytes(
        cls,
        data: bytes,
        byte_order: str,
    ) -> GenericMetadataPage:
        fmt = f"{'>' if byte_order == 'big' else '<'}8sIIIIBBBBIIIII20s"
        expected_size = struct.calcsize(fmt)
        if len(data) < expected_size:
            error_msg = (
                f"Data too short, expected at least {expected_size} bytes, got {len(data)} bytes"
            )

            raise ValueError(error_msg)
        try:
            unpacked_data = struct.unpack(fmt, data[:expected_size])
        except struct.error as exc:
            error_msg = f"Failed to unpack GenericMetadataPage: {exc}"
            raise ValueError(error_msg) from exc

        # Unpack the fields
        (
            lsn,
            page_no,
            magic,
            version,
            page_size,
            encryption_alg,
            page_type,
            meta_flags,
            unused_1,
            free,
            last_page_no,
            n_parts,
            key_count,
            record_count,
            flags,
            # UniqueFileID,
        ) = unpacked_data

        return cls(
            lsn=lsn,
            page_no=page_no,
            magic=magic,
            version=version,
            page_size=page_size,
            encryption_alg=encryption_alg,
            page_type=page_type,
            meta_flags=meta_flags,
            unused_1=unused_1,
            free=free,
            last_page_no=last_page_no,
            n_parts=n_parts,
            key_count=key_count,
            record_count=record_count,
            flags=flags,
            # UniqueFileID,
        )

    def __repr__(self) -> str:
        return (
            "GenericMetadataPage("
            f"LSN={self.lsn.hex()}, PageNo={self.page_no}, Magic={self.magic},"
            f" Version={self.version}, PageSize={self.page_size}, "
            f"EncryptionAlg={self.encryption_alg}, PageType={self.page_type}, "
            f"MetaFlags={self.meta_flags}, Unused1={self.unique_file_id}, "
            f"Free={self.free}, LastPageNo={self.last_page_no}, "
            f"NParts={self.n_parts}, "
            f"KeyCount={self.key_count}, RecordCount={self.record_count}, "
            f"Flags={self.flags.hex()}, UniqueFileID={self.unique_file_id})"
        )


def parse_generic_metadata_page(data: bytes) -> GenericMetadataPage:
    return GenericMetadataPage.from_bytes(data, "little")
