import logging
from contextlib import (
    suppress,
)

from labels.parsers.cataloger.redhat.rpmdb import (
    berkeley,
    sqlite,
)
from labels.parsers.cataloger.redhat.rpmdb.entry import (
    header_import,
)
from labels.parsers.cataloger.redhat.rpmdb.ndb import (
    RpmNDB,
)
from labels.parsers.cataloger.redhat.rpmdb.package import (
    PackageInfo,
    get_nevra,
)
from labels.parsers.cataloger.redhat.rpmdb.rpmdb_interface import (
    RpmDBInterface,
)
from labels.utils.exceptions import (
    InvalidDBFormatError,
    InvalidMetadataError,
)

LOGGER = logging.getLogger(__name__)


class RpmDB:
    def __init__(self, database: RpmDBInterface) -> None:
        self.database = database

    def list_packages(
        self,
    ) -> list[PackageInfo]:
        packages: list[PackageInfo] = []
        for entry in self.database.read():
            try:
                index_entries = header_import(entry)
            except ValueError:
                LOGGER.exception("Failed to import header")
                continue
            if index_entries:
                try:
                    package = get_nevra(index_entries)
                except ValueError:
                    LOGGER.exception("Failed to get nevra from index entries")
                    continue
                packages.append(package)
        return packages


def open_db(file_path: str) -> RpmDB | None:
    """Attempt to open an RPM database from the specified file path and returns an RpmDB instance.

    If the database is invalid or the metadata cannot be
    validated, None is returned.

    The function first tries to open the database as an SQLite database, and
    if that fails, it attempts to open it as a Berkeley DB. If both attempts
    fail, None is returned.

    :param file_path: The path to the RPM database file.
    :type file_path: str
    :return: An RpmDB instance if the database is valid, otherwise None.
    :rtype: RpmDB | None
    """
    with suppress(InvalidDBFormatError):
        return RpmDB(sqlite.open_sqlite(file_path))

    with suppress(InvalidDBFormatError):
        return RpmDB(RpmNDB.open(file_path))

    try:
        return RpmDB(berkeley.open_berkeley(file_path))
    except InvalidDBFormatError:
        pass
    except (ValueError, InvalidMetadataError):
        LOGGER.exception("Failed to open RPM database")

    return None
