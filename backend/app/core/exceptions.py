class DomainException(Exception):
    """Base exception class for all domain and architecture exceptions."""
    def __init__(self, message: str = "A domain error occurred"):
        self.message = message
        super().__init__(self.message)

class RepositoryException(DomainException):
    """Raised when repository storage operation encounters an error."""
    pass

class DataNotFoundException(DomainException):
    """Raised when requested entity or price record is not found."""
    pass

class InfrastructureException(DomainException):
    """Raised when infrastructure check or external system ping fails."""
    pass

class ValidationException(DomainException):
    """Raised when data validation fails."""
    pass
