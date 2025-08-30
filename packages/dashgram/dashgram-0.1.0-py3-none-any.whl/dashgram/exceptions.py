"""
Dashgram SDK Exceptions Module.

This module contains all custom exceptions used by the Dashgram SDK
for error handling and debugging.
"""


class DashgramError(Exception):
    """
    Base exception class for all Dashgram SDK errors.
    
    This is the parent class for all custom exceptions raised by the
    Dashgram SDK. It provides a consistent interface for error handling.
    
    Attributes:
        message: The error message describing what went wrong
    """
    
    def __init__(self, message: str):
        """
        Initialize the DashgramError exception.
        
        Args:
            message: A descriptive error message
        """
        self.message = message
        super().__init__(self.message)


class InvalidCredentials(DashgramError):
    """
    Exception raised when API credentials are invalid or missing.
    
    This exception is raised when the Dashgram API returns a 403 status code,
    indicating that the provided project_id or access_key is invalid.
    
    Attributes:
        message: The error message (defaults to "Invalid project_id or access_key")
    
    Example:
        >>> try:
        ...     await sdk.track_event(event)
        ... except InvalidCredentials:
        ...     print("Please check your project_id and access_key")
    """
    
    def __init__(self, message: str = "Invalid project_id or access_key"):
        """
        Initialize the InvalidCredentials exception.
        
        Args:
            message: Custom error message (optional)
        """
        super().__init__(message)


class DashgramApiError(DashgramError):
    """
    Exception raised when the Dashgram API returns an error response.
    
    This exception is raised when the Dashgram API returns a non-200 status code
    or when the response indicates an error. It contains details about the
    specific API error that occurred.
    
    Attributes:
        status_code: The HTTP status code returned by the API
        details: Additional error details from the API response
        message: The formatted error message combining status code and details
    
    Example:
        >>> try:
        ...     await sdk.track_event(event, suppress_exceptions=False)
        ... except DashgramApiError as e:
        ...     print(f"API Error {e.status_code}: {e.details}")
    """
    
    def __init__(self, status_code: int, details: str):
        """
        Initialize the DashgramApiError exception.
        
        Args:
            status_code: The HTTP status code from the API response
            details: Additional error details from the API response
        """
        self.status_code = status_code
        self.details = details
        super().__init__(f"{self.details} - Status Code: {self.status_code}")
