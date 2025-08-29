"""
Input validation utilities for the Commit Memory application.

This module provides functions for validating and sanitizing user inputs
to ensure data integrity and security.
"""

import html
import re
from typing import Any, Optional

# Constants for validation
MAX_MEMO_LENGTH = 2000  # Maximum length for memo text
MAX_AUTHOR_LENGTH = 100  # Maximum length for author names
MAX_PATH_LENGTH = 260  # Maximum length for file paths (Windows limit)


class ValidationError(Exception):
    """Exception raised for validation errors."""

    pass


def validate_memo_text(memo: str) -> str:
    """
    Validate and sanitize memo text.

    Args:
        memo: The memo text to validate

    Returns:
        Sanitized memo text

    Raises:
        ValidationError: If the memo text is invalid
    """
    if not memo:
        raise ValidationError("Memo text cannot be empty")

    if len(memo) > MAX_MEMO_LENGTH:
        raise ValidationError(
            f"Memo text exceeds maximum length of {MAX_MEMO_LENGTH} characters"
        )

    sanitized_memo = sanitize_text(memo)

    return sanitized_memo


def validate_author(author: str) -> str:
    """
    Validate and sanitize author name.

    Args:
        author: The author name to validate

    Returns:
        Sanitized author name

    Raises:
        ValidationError: If the author name is invalid
    """
    if not author:
        raise ValidationError("Author name cannot be empty")

    if len(author) > MAX_AUTHOR_LENGTH:
        raise ValidationError(
            f"Author name exceeds maximum length of {MAX_AUTHOR_LENGTH} characters"
        )

    sanitized_author = sanitize_text(author)

    return sanitized_author


def validate_file_path(path: str) -> str:
    """
    Validate and sanitize a file path.

    Args:
        path: The file path to validate

    Returns:
        Sanitized a file path

    Raises:
        ValidationError: If the file path is invalid
    """
    if not path:
        raise ValidationError("File path cannot be empty")

    if len(path) > MAX_PATH_LENGTH:
        raise ValidationError(
            f"File path exceeds maximum length of {MAX_PATH_LENGTH} characters"
        )

    if re.search(r"\.\./", path) or re.search(r"\.\.\\", path):
        raise ValidationError("File path contains potentially dangerous patterns")

    sanitized_path = sanitize_text(path)

    return sanitized_path


def validate_line_number(line: Optional[int]) -> Optional[int]:
    """
    Validate line number.

    Args:
        line: The line number to validate

    Returns:
        Validated line number

    Raises:
        ValidationError: If the line number is invalid
    """
    if line is None:
        return None

    if not isinstance(line, int):
        raise ValidationError("Line number must be an integer")

    if line <= 0:
        raise ValidationError("Line number must be positive")

    return line


def sanitize_text(text: str) -> str:
    """
    Sanitize text to prevent injection issues.

    Args:
        text: The text to sanitize

    Returns:
        Sanitized text
    """
    sanitized = html.escape(text)
    return sanitized


def validate_input(
    value: Any, validator_func, error_prefix: str = "Invalid input"
) -> Any:
    """
    Generic function to validate input using a validator function.

    Args:
        value: The value to validate
        validator_func: The validation function to use
        error_prefix: Prefix for error messages

    Returns:
        Validated and sanitized value

    Raises:
        ValidationError: If the value is invalid
    """
    try:
        return validator_func(value)
    except ValidationError as e:
        raise ValidationError(f"{error_prefix}: {str(e)}")
    except Exception as e:
        raise ValidationError(f"{error_prefix}: Unexpected error - {str(e)}")
