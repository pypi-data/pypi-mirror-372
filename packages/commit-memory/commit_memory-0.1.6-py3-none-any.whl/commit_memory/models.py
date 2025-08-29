"""
Data models for the Commit Memory application.

This module defines the core data structures used throughout the application:
- Memo: Represents a single memo attached to a commit or file
- Store: Represents the storage container for all memos
- Visibility: Type definition for memo visibility options

These models are serialized to and deserialized from JSON for persistence.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional

Visibility = Literal["private", "shared"]


@dataclass
class SharedRef:
    path: str
    digest: str
    title: Optional[str] = None


@dataclass
class Memo:
    """
    Represents a memo attached to a commit or a specific line in a file.

    A memo contains the actual note text, metadata about its creation,
    and optional references to a specific file and line number.

    Attributes:
        memo: The text content of the memo
        author: The name of the person who created the memo
        created: The timestamp when the memo was created (UTC)
        visibility: Whether the memo is private or shared with others
        file: Optional path to the file the memo is attached to
        line: Optional line number in the file the memo is attached to
        commit: Optional commit hash the memo is attached to
    """

    memo: str
    author: str
    created: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    visibility: Literal["private", "shared"] = "private"
    file: Optional[str] = None
    line: Optional[int] = None
    commit: Optional[str] = None
    shared: Optional[SharedRef] = None


@dataclass
class Store:
    """
    Container for storing all memos in the application.

    This class represents the root data structure that is serialized to and
    deserialized from JSON for persistence. It maintains collections of memos
    organized by commit hash and file blob SHA.

    Attributes:
        version: Schema version number for backward compatibility
        commit_memos: Dictionary mapping commit hashes to lists of memo
        files: Dictionary mapping file blob SHAs to lists of memos
    """

    version: int = 2
    commit_memos: Dict[str, List["Memo"]] = field(default_factory=dict)
    files: Dict[str, List["Memo"]] = field(default_factory=dict)
