import logging
import struct

LOGGER = logging.getLogger(__name__)


def htonl(val: int) -> int:
    try:
        # Convert from little-endian (host byte order)
        # to big-endian (network byte order)
        return struct.unpack(">i", struct.pack("<i", val))[0]
    except struct.error:
        LOGGER.exception("Failed to convert integer: %s")
        return 0


def htonlu(val: int) -> int:
    try:
        # Convert from little-endian (host byte order)
        # to big-endian (network byte order)
        return struct.unpack(">I", struct.pack("<I", val))[0]
    except struct.error:
        LOGGER.exception("Failed to convert unsigned integer: %s")
        return 0
