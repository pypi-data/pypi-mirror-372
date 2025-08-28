class PGCryptError(Exception):
    """Base PGCrypt error."""


class PGCryptHeaderError(ValueError):
    """Error header signature."""


class PGCryptMetadataCrcError(ValueError):
    """Error metadata crc32."""


class PGCryptModeError(ValueError):
    """Error fileobject mode."""
