import atexit
import logging
import sqlite3
from pathlib import Path
from typing import Literal

import boto3
import zstd
from botocore import UNSIGNED
from botocore.config import Config
from platformdirs import user_data_dir

LOGGER = logging.getLogger(__name__)


class BaseDatabase:
    BUCKET_NAME = "skims.sca"
    S3_SERVICE_NAME: Literal["s3"] = "s3"
    CONFIG_DIRECTORY = user_data_dir(
        appname="fluid-labels",
        appauthor="fluidattacks",
        ensure_exists=True,
    )

    def __init__(self, db_name: str) -> None:
        self.db_name = db_name
        self.bucket_file_key = f"{db_name}.zst"
        self.db_local_path = str(Path(self.CONFIG_DIRECTORY, db_name))
        self.db_local_compressed_path = f"{self.db_local_path}.zst"
        self.connection: sqlite3.Connection | None = None
        self.s3_client = boto3.client(
            service_name=self.S3_SERVICE_NAME,
            config=Config(
                region_name="us-east-1",
                signature_version=UNSIGNED,
            ),
        )

    def _get_database_file(self) -> None:
        LOGGER.info("⬇️ Downloading advisories database")
        self.s3_client.download_file(
            Bucket=self.BUCKET_NAME,
            Key=self.bucket_file_key,
            Filename=self.db_local_compressed_path,
        )
        LOGGER.info("🗜️ Decompressing advisories database")

        try:
            with Path(self.db_local_compressed_path).open("rb") as compressed_file:
                compressed_data = compressed_file.read()
            uncompressed_data = zstd.decompress(compressed_data)
            with Path(self.db_local_path).open("wb") as output_file:
                output_file.write(uncompressed_data)
        except Exception:
            LOGGER.exception("❌ Unable to decompress database %s", self.db_name)

    def _initialize_db(self) -> bool:
        local_database_exists = Path(self.db_local_path).is_file()

        try:
            if self.is_up_to_date(local_database_exists=local_database_exists):
                LOGGER.info("✅ Advisories database is up to date")
                return True
            self._get_database_file()
            Path(self.db_local_compressed_path).unlink()
        except Exception:
            if local_database_exists:
                LOGGER.warning(
                    "⚠️ Advisories may be outdated, unable to update database",
                )
                return True

            LOGGER.exception(
                "❌ Advisories won't be included, unable to download database",
            )
            return False
        else:
            return True

    def is_up_to_date(self, *, local_database_exists: bool) -> bool:
        db_metadata = self.s3_client.head_object(
            Bucket=self.BUCKET_NAME,
            Key=self.bucket_file_key,
        )
        return (
            local_database_exists
            and Path(self.db_local_path).stat().st_mtime >= db_metadata["LastModified"].timestamp()
        )

    def initialize(self) -> None:
        if self.connection is None and self._initialize_db():
            self.connection = sqlite3.connect(
                self.db_local_path,
                check_same_thread=False,
            )
            atexit.register(self.connection.close)

    def get_connection(self) -> sqlite3.Connection:
        if self.connection is not None:
            return self.connection
        self.connection = sqlite3.connect(
            self.db_local_path,
            check_same_thread=False,
        )
        atexit.register(self.connection.close)
        return self.connection
