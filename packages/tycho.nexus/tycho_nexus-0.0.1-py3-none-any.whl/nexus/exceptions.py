"""

All exceptions in use by the package.

"""

# Base Exception


class NexusException(Exception):
    """Base exception, can be used to catch all package exception"""

    def __init__(self, message: str):
        super().__init__(message)


class APIException(NexusException):
    """Base exception to catch all Nexus API error responses"""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

        super().__init__(f"({code}) {message}")


# Exceptions


class UnknownDiscordUser(APIException):
    """Exception raised when a non-existing Discord user is used."""

    def __init__(self):
        super().__init__(10_003, "Unknown Discord user")


class UnknownKey(APIException):
    """Exception raised when a non-existing API key is used."""

    def __init__(self):
        super().__init__(10_006, "Unknown API key")


class UnknownDiscordAccount(APIException):
    """Exception raised when a Discord account was queried but not found."""

    def __init__(self):
        super().__init__(10_007, "Unknown Discord account")


class UnknownRobloxAccount(APIException):
    """Exception raised when a Roblox account was queried but not found."""

    def __init__(self):
        super().__init__(10_008, "Unknown Roblox account")


class InternalError(APIException):
    """Exception raised when an internal server-side error occurs."""

    def __init__(self):
        super().__init__(30_001, "Internal server error")


class InvalidParameter(APIException):
    """Exception raised when an invalid parameter is used."""

    def __init__(self):
        super().__init__(40_006, "Invalid paramater")


class RateLimited(APIException):
    """Exception raised when (somehow) a rate limit is hit."""

    def __init__(self):
        super().__init__(40_022, "Too many requests")
