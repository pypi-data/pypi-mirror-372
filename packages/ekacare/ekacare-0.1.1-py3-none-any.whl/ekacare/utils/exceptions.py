class EkaCareError(Exception):
    """Base exception for all Eka Care SDK errors."""
    pass


class EkaCareAPIError(EkaCareError):
    """Exception raised when the Eka Care API returns an error."""
    pass


class EkaCareAuthError(EkaCareError):
    """Exception raised when authentication with the Eka Care API fails."""
    pass


class EkaCareValidationError(EkaCareError):
    """Exception raised when input validation fails."""
    pass


class EkaCareResourceNotFoundError(EkaCareError):
    """Exception raised when a requested resource is not found."""
    pass
