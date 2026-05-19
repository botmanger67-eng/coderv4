import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union


def safe_get(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    Safely retrieve a value from a nested dictionary.

    Args:
        data: The dictionary to traverse.
        *keys: Sequence of keys to follow.
        default: Default value if path is not found.

    Returns:
        The value at the specified path or default.
    """
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
            if current is None:
                return default
        else:
            return default
    return current


def format_timestamp(dt: Optional[datetime] = None, fmt: str = "%Y-%m-%d %H:%M:%S UTC") -> str:
    """
    Format a datetime object to a string. Defaults to current UTC time.

    Args:
        dt: Datetime object. If None, uses current UTC time.
        fmt: Format string.

    Returns:
        Formatted timestamp string.
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.strftime(fmt)


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length, appending a suffix if truncated.

    Args:
        text: Input text.
        max_length: Maximum allowed length.
        suffix: Suffix to append when truncated.

    Returns:
        Truncated text string.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def parse_json_safe(data: str) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """
    Safely parse a JSON string.

    Args:
        data: JSON string to parse.

    Returns:
        Parsed JSON object or None if parsing fails.
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return None


def extract_code_blocks(text: str) -> List[str]:
    """
    Extract code blocks from markdown text.

    Args:
        text: Markdown text containing code blocks.

    Returns:
        List of code block contents.
    """
    pattern = r"```(?:\w+)?\n([\s\S]*?)```"
    matches = re.findall(pattern, text)
    return [match.strip() for match in matches]


def sanitize_filename(name: str, replacement: str = "_") -> str:
    """
    Sanitize a string to be used as a filename.

    Args:
        name: Input string.
        replacement: Character to replace invalid characters with.

    Returns:
        Sanitized filename string.
    """
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, replacement, name)
    sanitized = sanitized.strip(". ")
    return sanitized if sanitized else "untitled"


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.

    Args:
        items: List to split.
        chunk_size: Maximum size of each chunk.

    Returns:
        List of chunks.

    Raises:
        ValueError: If chunk_size is less than 1.
    """
    if chunk_size < 1:
        raise ValueError("chunk_size must be at least 1")
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries. Override values take precedence.

    Args:
        base: Base dictionary.
        override: Dictionary with overriding values.

    Returns:
        Merged dictionary.
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.

    Args:
        url: URL string to validate.

    Returns:
        True if valid URL, False otherwise.
    """
    pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    return bool(re.match(pattern, url, re.IGNORECASE))


def retry_async(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator for async functions to retry on failure.

    Args:
        max_retries: Maximum number of retry attempts.
        delay: Delay between retries in seconds.

    Returns:
        Decorated async function.
    """
    import asyncio
    import functools

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (attempt + 1))
            raise last_exception  # type: ignore
        return wrapper
    return decorator