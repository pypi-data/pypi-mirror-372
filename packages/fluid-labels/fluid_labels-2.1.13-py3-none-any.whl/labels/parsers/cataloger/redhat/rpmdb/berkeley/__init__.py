import io
import logging
from collections.abc import Generator
from pathlib import Path

from labels.parsers.cataloger.redhat.rpmdb.berkeley.constants import (
    HASH_OF_INDEX_PAGE_TYPE,
    HASH_PAGE_TYPE,
    HASH_UNSORTED_PAGE_TYPE,
    VALID_PAGE_SIZES,
)
from labels.parsers.cataloger.redhat.rpmdb.berkeley.hash_metadata_page import (
    HashMetadataPage,
    parse_hash_metadata_page,
)
from labels.parsers.cataloger.redhat.rpmdb.berkeley.hash_page import (
    hash_page_value_content,
    hash_page_value_indexes,
    parse_hash_page,
)
from labels.parsers.cataloger.redhat.rpmdb.rpmdb_interface import (
    RpmDBInterface,
)
from labels.utils.exceptions import (
    InvalidDBFormatError,
    InvalidMetadataError,
)

LOGGER = logging.getLogger(__name__)


class BerkeleyDB(RpmDBInterface):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.file = Path(file_path).open("rb")  # noqa: SIM115
        self.hash_metadata = self._read_metadata()

    def _read_metadata(self) -> HashMetadataPage:
        # Read the first 512 bytes to parse metadata
        self.file.seek(0)
        metadata_buff = self.file.read(512)
        if len(metadata_buff) < 512:
            error_msg = "Failed to read metadata: insufficient data"
            raise InvalidDBFormatError(error_msg)

        # Parse the hash metadata page
        hash_metadata = parse_hash_metadata_page(metadata_buff)

        # Validate the page size
        if hash_metadata.hash_metadata.generic_metadata_page.page_size not in VALID_PAGE_SIZES:
            raise InvalidDBFormatError(
                "Unexpected page size: "
                + str(hash_metadata.hash_metadata.generic_metadata_page.page_size),
            )

        return hash_metadata

    def close(self) -> None:
        self.file.close()

    def read(self) -> Generator[bytes, None, None]:
        page_size = self.hash_metadata.hash_metadata.generic_metadata_page.page_size
        swapped = self.hash_metadata.swapped
        last_page_no = self.hash_metadata.hash_metadata.generic_metadata_page.last_page_no

        self.file.seek(0, io.SEEK_SET)

        for _ in range(last_page_no + 1):
            page_data = self._read_page(page_size)
            if not page_data:
                return

            hash_page_header = parse_hash_page(page_data, swapped=swapped)
            if hash_page_header.page_type not in (
                HASH_UNSORTED_PAGE_TYPE,
                HASH_PAGE_TYPE,
            ):
                continue

            hash_page_indexes = hash_page_value_indexes(
                page_data,
                hash_page_header.num_entries,
                swapped=swapped,
            )

            for hash_page_index in hash_page_indexes:
                if page_data[hash_page_index] != HASH_OF_INDEX_PAGE_TYPE:
                    continue

                current_file_position = self.file.tell()
                try:
                    value_content = hash_page_value_content(
                        self.file,
                        page_data,
                        hash_page_index,
                        page_size,
                        swapped=swapped,
                    )
                    yield value_content
                except ValueError:
                    return
                finally:
                    self.file.seek(current_file_position, io.SEEK_SET)

    def _read_page(self, page_size: int) -> bytes:
        page_data = self.file.read(page_size)
        if len(page_data) != page_size:
            LOGGER.error(
                "Failed to read page",
                extra={"extra": {"location": self.file_path}},
            )
            return b""
        return page_data


def open_berkeley(file_path: str) -> BerkeleyDB:
    try:
        berkeley_db = BerkeleyDB(file_path)
    except InvalidMetadataError as exc:
        LOGGER.warning(
            "Invalid Berkeley database file",
            extra={
                "extra": {
                    "location": file_path,
                },
            },
        )
        raise InvalidDBFormatError from exc
    return berkeley_db
