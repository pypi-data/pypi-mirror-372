"""Library for read and write storage format for PGCopy dump
packed into LZ4, ZSTD or uncompressed
with meta data information packed into zlib."""

from .enums import CompressionMethod
from .errors import (
    PGCryptError,
    PGCryptHeaderError,
    PGCryptMetadataCrcError,
    PGCryptModeError,
)
from .reader import PGCryptReader
from .writer import PGCryptWriter


__all__ = (
    "CompressionMethod",
    "PGCryptError",
    "PGCryptHeaderError",
    "PGCryptMetadataCrcError",
    "PGCryptModeError",
    "PGCryptReader",
    "PGCryptWriter",
)
__author__ = "0xMihalich"
__version__ = "0.1.0"
