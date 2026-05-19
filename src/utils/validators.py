"""Input validators for the application.

This module provides utility functions for validating various types of input
data, ensuring they meet expected formats and constraints before processing.
"""

import re
from typing import Any, Optional
from urllib.parse import urlparse


def validate_not_empty(value: Any, field_name: str = "value") -> str:
    """Validate that a value is a non-empty string.

    Args:
        value: The value to validate.
        field_name: The name of the field for error messages.

    Returns:
        The validated string.

    Raises:
        ValueError: If the value is not a non-empty string.
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string, got {type(value).__name__}")
    if not value.strip():
        raise ValueError(f"{field_name} cannot be empty or whitespace only")
    return value.strip()


def validate_positive_integer(value: Any, field_name: str = "value") -> int:
    """Validate that a value is a positive integer.

    Args:
        value: The value to validate.
        field_name: The name of the field for error messages.

    Returns:
        The validated integer.

    Raises:
        ValueError: If the value is not a positive integer.
    """
    if not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer, got {type(value).__name__}")
    if value <= 0:
        raise ValueError(f"{field_name} must be positive, got {value}")
    return value


def validate_non_negative_integer(value: Any, field_name: str = "value") -> int:
    """Validate that a value is a non-negative integer.

    Args:
        value: The value to validate.
        field_name: The name of the field for error messages.

    Returns:
        The validated integer.

    Raises:
        ValueError: If the value is not a non-negative integer.
    """
    if not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer, got {type(value).__name__}")
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative, got {value}")
    return value


def validate_boolean(value: Any, field_name: str = "value") -> bool:
    """Validate that a value is a boolean.

    Args:
        value: The value to validate.
        field_name: The name of the field for error messages.

    Returns:
        The validated boolean.

    Raises:
        ValueError: If the value is not a boolean.
    """
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean, got {type(value).__name__}")
    return value


def validate_url(value: str, field_name: str = "URL") -> str:
    """Validate that a string is a well-formed URL.

    Args:
        value: The URL string to validate.
        field_name: The name of the field for error messages.

    Returns:
        The validated URL string.

    Raises:
        ValueError: If the value is not a valid URL.
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string, got {type(value).__name__}")
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} cannot be empty")
    try:
        parsed = urlparse(value)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"{field_name} is not a valid URL: {value}")
        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"{field_name} scheme must be http or https, got {parsed.scheme}")
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Invalid {field_name}: {e}") from e
    return value


def validate_email(value: str, field_name: str = "email") -> str:
    """Validate that a string is a valid email address.

    Args:
        value: The email string to validate.
        field_name: The name of the field for error messages.

    Returns:
        The validated email string.

    Raises:
        ValueError: If the value is not a valid email address.
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string, got {type(value).__name__}")
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} cannot be empty")
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, value):
        raise ValueError(f"{field_name} is not a valid email address: {value}")
    return value


def validate_telegram_chat_id(value: Any, field_name: str = "chat_id") -> int:
    """Validate that a value is a valid Telegram chat ID.

    Args:
        value: The chat ID to validate.
        field_name: The name of the field for error messages.

    Returns:
        The validated chat ID as an integer.

    Raises:
        ValueError: If the value is not a valid Telegram chat ID.
    """
    if isinstance(value, str):
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise ValueError(f"{field_name} must be an integer or numeric string, got '{value}'")
    if not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer, got {type(value).__name__}")
    if value >= 0:
        raise ValueError(f"{field_name} must be negative for non-supergroup chats, got {value}")
    return value


def validate_github_token(value: str, field_name: str = "GitHub token") -> str:
    """Validate that a string is a plausible GitHub token.

    Args:
        value: The token string to validate.
        field_name: The name of the field for error messages.

    Returns:
        The validated token string.

    Raises:
        ValueError: If the value is not a plausible GitHub token.
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string, got {type(value).__name__}")
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} cannot be empty")
    if len(value) < 10:
        raise ValueError(f"{field_name} is too short to be valid")
    if not re.match(r"^[a-zA-Z0-9_]+$", value):
        raise ValueError(f"{field_name} contains invalid characters")
    return value


def validate_openai_api_key(value: str, field_name: str = "OpenAI API key") -> str:
    """Validate that a string is a plausible OpenAI API key.

    Args:
        value: The API key string to validate.
        field_name: The name of the field for error messages.

    Returns:
        The validated API key string.

    Raises:
        ValueError: If the value is not a plausible OpenAI API key.
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string, got {type(value).__name__}")
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} cannot be empty")
    if not value.startswith("sk-"):
        raise ValueError(f"{field_name} must start with 'sk-'")
    if len(value) < 20:
        raise ValueError(f"{field_name} is too short to be valid")
    return value


def validate_in_range(value: Any, min_val: float, max_val: float, field_name: str = "value") -> float:
    """Validate that a numeric value falls within a specified range.

    Args:
        value: The value to validate.
        min_val: The minimum acceptable value (inclusive).
        max_val: The maximum acceptable value (inclusive).
        field_name: The name of the field for error messages.

    Returns:
        The validated numeric value as a float.

    Raises:
        ValueError: If the value is not a number or is outside the range.
    """
    if not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a number, got {type(value).__name__}")
    value = float(value)
    if value < min_val or value > max_val:
        raise ValueError(f"{field_name} must be between {min_val} and {max_val}, got {value}")
    return value


def validate_choice(value: Any, choices: list, field_name: str = "value") -> Any:
    """Validate that a value is one of the allowed choices.

    Args:
        value: The value to validate.
        choices: The list of allowed values.
        field_name: The name of the field for error messages.

    Returns:
        The validated value.

    Raises:
        ValueError: If the value is not in the allowed choices.
    """
    if value not in choices:
        choices_str = ", ".join(str(c) for c in choices)
        raise ValueError(f"{field_name} must be one of [{choices_str}], got {value}")
    return value


def validate_string_length(value: str, min_length: int = 0, max_length: Optional[int] = None, field_name: str = "value") -> str:
    """Validate that a string's length is within specified bounds.

    Args:
        value: The string to validate.
        min_length: The minimum length (inclusive). Defaults to 0.
        max_length: The maximum length (inclusive). If None, no upper bound.
        field_name: The name of the field for error messages.

    Returns:
        The validated string.

    Raises:
        ValueError: If the string length is outside the bounds.
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string, got {type(value).__name__}")
    value = value.strip()
    if len(value) < min_length:
        raise ValueError(f"{field_name} must be at least {min_length} characters long, got {len(value)}")
    if max_length is not None and len(value) > max_length:
        raise ValueError(f"{field_name} must be at most {max_length} characters long, got {len(value)}")
    return value


def validate_regex(value: str, pattern: str, field_name: str = "value") -> str:
    """Validate that a string matches a regular expression pattern.

    Args:
        value: The string to validate.
        pattern: The regex pattern to match against.
        field_name: The name of the field for error messages.

    Returns:
        The validated string.

    Raises:
        ValueError: If the string does not match the pattern.
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string, got {type(value).__name__}")
    value = value.strip()
    if not re.match(pattern, value):
        raise ValueError(f"{field_name} does not match the required pattern: {value}")
    return value