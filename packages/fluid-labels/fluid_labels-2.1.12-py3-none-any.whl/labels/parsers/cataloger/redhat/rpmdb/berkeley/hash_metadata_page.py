from __future__ import (
    annotations,
)

import struct

from pydantic import (
    BaseModel,
)

from labels.parsers.cataloger.redhat.rpmdb.berkeley.constants import (
    HASH_MAGIC_NUMBER,
    HASH_MAGIC_NUMBER_BE,
    HASH_METADATA_PACKAGE_TYPE,
)
from labels.parsers.cataloger.redhat.rpmdb.berkeley.generic_page import (
    GenericMetadataPage,
)
from labels.utils.exceptions import (
    InvalidMetadataError,
)


class HashMetadata(BaseModel):
    """Represents the Hash Metadata in the RPM database."""

    generic_metadata_page: GenericMetadataPage
    max_bucket: int
    high_mask: int
    low_mask: int
    fill_factor: int
    num_keys: int
    char_key_hash: int

    @classmethod
    def from_bytes(cls, data: bytes, byte_order: str) -> HashMetadata:
        expected_size = 96  # Up to CharKeyHash (bytes 0-95)
        if len(data) < expected_size:
            error_msg = (
                f"Data too short, expected at least {expected_size} bytes, got {len(data)} bytes"
            )
            raise ValueError(error_msg)

        # Parse the GenericMetadataPage part
        generic_metadata = GenericMetadataPage.from_bytes(data[:72], byte_order)

        # Parse the additional fields (MaxBucket to CharKeyHash)
        fmt = f"{'>' if byte_order == 'big' else '<'}6I"
        additional_fields_size = struct.calcsize(fmt)
        try:
            unpacked_data = struct.unpack(fmt, data[72 : 72 + additional_fields_size])
        except struct.error as exc:
            error_msg = f"Failed to unpack HashMetadata additional fields: {exc}"
            raise ValueError(error_msg) from exc

        (
            max_bucket,
            high_mask,
            low_mask,
            fill_factor,
            num_keys,
            char_key_hash,
        ) = unpacked_data

        return cls(
            generic_metadata_page=generic_metadata,
            max_bucket=max_bucket,
            high_mask=high_mask,
            low_mask=low_mask,
            fill_factor=fill_factor,
            num_keys=num_keys,
            char_key_hash=char_key_hash,
        )

    @classmethod
    def validate(cls, value: HashMetadata) -> None:  # type: ignore[override]
        """Validate the HashMetadata.

        :raises InvalidMetadata: If validation fails.
        """
        if value.generic_metadata_page.magic != HASH_MAGIC_NUMBER:
            error_msg = f"Unexpected DB magic number: {hex(value.generic_metadata_page.magic)}"
            raise InvalidMetadataError(error_msg)

        if value.generic_metadata_page.page_type != HASH_METADATA_PACKAGE_TYPE:
            raise InvalidMetadataError(
                "Unexpected page type: " + str(value.generic_metadata_page.page_type),
            )


class HashMetadataPage:
    """Represents a Hash Metadata Page with endian information."""

    def __init__(self, hash_metadata: HashMetadata, *, swapped: bool) -> None:
        self.hash_metadata = hash_metadata
        self.swapped = swapped  # Indicates if the byte order is swapped (big-endian)

    @classmethod
    def from_bytes(cls, data: bytes) -> HashMetadataPage:
        """Parse a HashMetadataPage from a bytes object.

        :param data: The bytes object containing the page data.
        :return: An instance of HashMetadataPage.
        :raises ValueError: If the data is invalid or parsing fails.
        """
        swapped = False
        byte_order = "little"

        # First attempt to parse using little-endian byte order
        hash_metadata = HashMetadata.from_bytes(data, byte_order)

        if hash_metadata.generic_metadata_page.magic == HASH_MAGIC_NUMBER_BE:
            # Re-read the GenericMetadataPage using big-endian byte order
            swapped = True
            byte_order = "big"

            # Re-parse only the GenericMetadataPage portion
            generic_metadata = GenericMetadataPage.from_bytes(data[:72], byte_order)

            # Create a new HashMetadata instance with the corrected
            # GenericMetadataPage
            metadata = HashMetadata(
                generic_metadata_page=generic_metadata,
                max_bucket=hash_metadata.max_bucket,
                high_mask=hash_metadata.high_mask,
                low_mask=hash_metadata.low_mask,
                fill_factor=hash_metadata.fill_factor,
                num_keys=hash_metadata.num_keys,
                char_key_hash=hash_metadata.char_key_hash,
            )
            hash_metadata = metadata

        # Validate the metadata
        HashMetadata.validate(hash_metadata)

        return cls(hash_metadata, swapped=swapped)

    def __repr__(self) -> str:
        return f"HashMetadataPage(hash_metadata={self.hash_metadata}, swapped={self.swapped})"


def parse_hash_metadata_page(data: bytes) -> HashMetadataPage:
    """Parse a HashMetadataPage from a bytes object.

    :param data: A bytes object containing the metadata page data.
    :type data: bytes
    :return: An instance of HashMetadataPage.
    :rtype: HashMetadataPage
    :raises ValueError | InvalidMetadataError: If the data is invalid or parsing
        fails.
    """
    return HashMetadataPage.from_bytes(data)
