class TlsClientError(Exception):
    """Base exception for TLS client errors."""
    pass

class ProfileError(TlsClientError):
    """Exception for profile-related errors."""
    pass

class RequestError(TlsClientError):
    """Exception for request-related errors."""
    pass

class PlatformNotSupportedError(TlsClientError):
    """Exception for unsupported platforms."""
    pass