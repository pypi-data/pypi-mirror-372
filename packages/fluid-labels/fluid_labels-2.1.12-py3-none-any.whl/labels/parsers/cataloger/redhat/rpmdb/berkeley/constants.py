# Magic numbers
HASH_MAGIC_NUMBER = 0x00061561
HASH_MAGIC_NUMBER_BE = 0x61150600

# Sizes in bytes
# The size (in bytes) of an in-page offset
HASH_INDEX_ENTRY_SIZE = 2
# All DB pages have the same sized header (in bytes)
PAGE_HEADER_SIZE = 26
# Hash off-page size (in bytes)
HASH_OFF_PAGE_SIZE = 12

# All page types supported
# Source: https://github.com/berkeleydb/libdb/blob/v5.3.28/src/dbinc
# /db_page.h#L35-L53

# Hash pages created pre 4.6 (DEPRECATED)
HASH_UNSORTED_PAGE_TYPE = 2
OVERFLOW_PAGE_TYPE = 7
HASH_METADATA_PACKAGE_TYPE = 8
# Sorted hash page
HASH_PAGE_TYPE = 13

# Hash off-index page type (aka HOFFPAGE)
# Source: https://github.com/berkeleydb/libdb/blob/v5.3.28/src/dbinc
# /db_page.h#L569-L573
HASH_OF_INDEX_PAGE_TYPE = 3

# PageType is an alias for uint8 in Go.


VALID_PAGE_SIZES = {
    512,
    1024,
    2048,
    4096,
    8192,
    16384,
    32768,
    65536,
}
