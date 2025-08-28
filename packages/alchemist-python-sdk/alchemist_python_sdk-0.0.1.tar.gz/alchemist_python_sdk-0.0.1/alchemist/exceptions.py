"""
Custom exceptions for the Alchemist Python SDK.
"""


class AlchemistError(Exception):
    """Base exception class for Alchemist SDK errors."""
    
    def __init__(self, message, error_code=None, details=None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class AuthenticationError(AlchemistError):
    """Raised when authentication fails or API key is invalid."""
    pass


class AgentNotFoundError(AlchemistError):
    """Raised when the specified agent ID cannot be found or accessed."""
    pass


class SessionError(AlchemistError):
    """Raised when session operations fail."""
    pass


class RateLimitError(AlchemistError):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, message, retry_after=None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class NetworkError(AlchemistError):
    """Raised when network requests fail."""
    
    def __init__(self, message, status_code=None, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code


class ValidationError(AlchemistError):
    """Raised when input validation fails."""
    pass


class StreamingError(AlchemistError):
    """Raised when streaming response encounters an error."""
    pass