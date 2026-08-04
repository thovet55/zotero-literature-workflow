class ZoteroError(Exception):
    """Base class for safe, user-facing Zotero errors."""


class ZoteroHTTPError(ZoteroError):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"Zotero API returned HTTP {status}: {message}")


class ZoteroUnavailableError(ZoteroError):
    pass
