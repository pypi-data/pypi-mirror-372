from typing import Any

class LifecycleError(Exception):
    """Base exception for s3_lifecycle policy errors."""
    def __init__(self, message: str = None, *, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.details = details or {}

    def __str__(self):
        base = super().__str__()
        return f"{base} | details={self.details}" if self.details else base


class ValidationError(LifecycleError):
    """Raised when s3_lifecycle policy validation fails."""
    pass


class DiffError(LifecycleError):
    """Raised when diff computation encounters an error."""
    pass


class ApplyError(LifecycleError):
    """Raised when applying s3_lifecycle policy to S3 fails."""
    pass


class FetchError(LifecycleError):
    """Raised when fetching lifecycle configuration from S3 fails."""
    pass
