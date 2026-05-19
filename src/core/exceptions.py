class BaseAppError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str = "An application error occurred") -> None:
        self.message = message
        super().__init__(self.message)


class ConfigurationError(BaseAppError):
    """Raised when there is a configuration issue."""

    def __init__(self, message: str = "Configuration error") -> None:
        super().__init__(message)


class DatabaseError(BaseAppError):
    """Raised when a database operation fails."""

    def __init__(self, message: str = "Database error") -> None:
        super().__init__(message)


class APIError(BaseAppError):
    """Raised when an external API call fails."""

    def __init__(self, message: str = "API error", status_code: int | None = None) -> None:
        self.status_code = status_code
        detail = f" (status {status_code})" if status_code else ""
        super().__init__(f"{message}{detail}")


class TelegramError(BaseAppError):
    """Raised when a Telegram bot operation fails."""

    def __init__(self, message: str = "Telegram error") -> None:
        super().__init__(message)


class OpenAIError(BaseAppError):
    """Raised when an OpenAI API operation fails."""

    def __init__(self, message: str = "OpenAI error") -> None:
        super().__init__(message)


class GitHubError(BaseAppError):
    """Raised when a GitHub API operation fails."""

    def __init__(self, message: str = "GitHub error") -> None:
        super().__init__(message)


class ValidationError(BaseAppError):
    """Raised when data validation fails."""

    def __init__(self, message: str = "Validation error") -> None:
        super().__init__(message)


class NotFoundError(BaseAppError):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message)


class AuthenticationError(BaseAppError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication error") -> None:
        super().__init__(message)


class AuthorizationError(BaseAppError):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Authorization error") -> None:
        super().__init__(message)


class RateLimitError(BaseAppError):
    """Raised when a rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message)


class TimeoutError(BaseAppError):
    """Raised when an operation times out."""

    def __init__(self, message: str = "Operation timed out") -> None:
        super().__init__(message)


class NetworkError(BaseAppError):
    """Raised when a network operation fails."""

    def __init__(self, message: str = "Network error") -> None:
        super().__init__(message)


class FileOperationError(BaseAppError):
    """Raised when a file operation fails."""

    def __init__(self, message: str = "File operation error") -> None:
        super().__init__(message)


class SerializationError(BaseAppError):
    """Raised when serialization or deserialization fails."""

    def __init__(self, message: str = "Serialization error") -> None:
        super().__init__(message)


class DependencyError(BaseAppError):
    """Raised when a required dependency is missing or fails."""

    def __init__(self, message: str = "Dependency error") -> None:
        super().__init__(message)


class StateError(BaseAppError):
    """Raised when an operation is attempted in an invalid state."""

    def __init__(self, message: str = "Invalid state error") -> None:
        super().__init__(message)