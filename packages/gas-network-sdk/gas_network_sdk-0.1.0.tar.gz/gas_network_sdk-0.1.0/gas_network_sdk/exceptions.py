"""Exception classes for the Gas Network SDK."""

from typing import Optional


class GasNetworkError(Exception):
    """Base exception class for Gas Network SDK."""
    
    def __init__(self, message: str, response_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.message = message
        self.response_code = response_code


class APIError(GasNetworkError):
    """Raised when the API returns an error response."""
    
    def __init__(self, message: str, response_code: int, response_text: str = "") -> None:
        super().__init__(message, response_code)
        self.response_text = response_text


class UnsupportedChainError(GasNetworkError):
    """Raised when an operation is attempted on an unsupported chain."""
    
    def __init__(self, chain: str, operation: str) -> None:
        message = f"{operation} is not supported for chain: {chain}"
        super().__init__(message)
        self.chain = chain
        self.operation = operation


class InvalidAPIKeyError(GasNetworkError):
    """Raised when the provided API key is invalid."""
    
    def __init__(self, message: str = "Invalid API key provided") -> None:
        super().__init__(message, 401)


class NetworkError(GasNetworkError):
    """Raised when a network error occurs."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None) -> None:
        super().__init__(message)
        self.original_error = original_error


class TimeoutError(GasNetworkError):
    """Raised when a request times out."""
    
    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message)