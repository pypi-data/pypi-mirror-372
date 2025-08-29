"""
Storage mechanism for commit memos.

This module provides functionality for persisting and retrieving memos using JSON files.
It includes:
- JsonStore: Main class for storing and retrieving memos
- Serialization/deserialization functions for converting between Store objects and JSON
- Support for both private and shared memo storage
- Performance optimizations including caching, lazy loading, and incremental updates

The storage format uses a versioned schema to support backward compatibility.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from .json_compat import dumps as jdumps
from .json_compat import loads as jloads
from .models import Memo, Store

STORE_PRIVATE = ".commit-memos.private.json"
STORE_SHARED = ".commit-memos.shared.json"

_ISO = "%Y-%m-%dT%H:%M:%S.%fZ"


CACHE_SIZE = 128


# Note: The following optimizations have been implemented:
# 1. Incremental updates: Only modified commits/files are tracked and updated
# 2. Caching: Frequently accessed data is cached using lru_cache
# 3. Lazy loading: Data is loaded only when needed, not at initialization
def _to_jsonable(o: Any) -> Any:
    """
    Convert Python objects (dataclasses, datetime, containers) into JSON-friendly
    structures. Datetime are formatted in ISO with Z suffix.
    """
    if isinstance(o, datetime):
        # Ensure UTC with Z suffix
        if o.tzinfo is None:
            o = o.replace(tzinfo=timezone.utc)
        return o.astimezone(timezone.utc).strftime(_ISO)

    if is_dataclass(o):
        return _to_jsonable(asdict(o))

    if isinstance(o, dict):
        return {k: _to_jsonable(v) for k, v in o.items()}

    if isinstance(o, (list, tuple)):
        return [_to_jsonable(v) for v in o]

    return o


def _serialize(store: Store) -> bytes:
    """
    Convert Store dataclass to JSON string with ISO datetime formatting.

    This function handles the serialization of the Store object to JSON,
    with special handling for datetime objects and dataclasses.

    Args:
        store: The Store object to serialize

    Returns:
        str: JSON string representation of the store

    Raises:
        TypeError: If an object cannot be serialized
    """

    payload = _to_jsonable(store)
    return jdumps(payload)


def _deserialize(raw: Union[str, bytes]) -> Store:
    """
    Load JSON into a Store object with automatic migration.

    This function handles the deserialization of JSON data to a Store object,
    with special handling for:
    - Converting dictionaries to Memo objects
    - Migrating old data layouts (version 1) to the current schema (version 2)

    Args:
        raw: JSON string or bytes to deserialize

    Returns:
        Store: The deserialized Store object
    """

    def to_memo(d: dict) -> Memo:
        """Convert a dictionary to a Memo object."""
        return Memo(
            memo=d["memo"],
            author=d["author"],
            created=_parse_dt(d["created"]),
            visibility=d["visibility"],
            file=d.get("file"),
            line=d.get("line"),
            commit=d.get("commit"),
        )

    data = jloads(raw)

    if "version" not in data or data.get("version") == 1:
        data["commit_memos"] = data.pop("commits", {})
        data.setdefault("files", {})
        data["version"] = 2

    for bucket in ("commit_memos", "files"):
        data[bucket] = {
            k: [m if isinstance(m, Memo) else to_memo(m) for m in v if m]
            for k, v in data.get(bucket, {}).items()
        }

    for commit_sha, lst in data.get("commit_memos", {}).items():
        for m in lst:
            if getattr(m, "commit", None) is None:
                m.commit = commit_sha

    return Store(**data)


def _parse_dt(ts: str) -> datetime:
    """
    Parse a datetime string in various formats to a datetime object.

    This function attempts to parse a datetime string using multiple
    formats, ensuring compatibility with different datetime representations.
    It also ensures that all datetime objects have a UTC timezone.

    Args:
        ts: The datetime string to parse

    Returns:
        datetime: The parsed datetime object with UTC timezone

    Raises:
        ValueError: If the datetime string cannot be parsed with any format
    """
    formats = [
        _ISO,
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(ts, fmt)
            return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
        except ValueError:
            continue

    raise ValueError(f"Unable to parse datetime string: {ts}")


class JsonStore:
    """
    Provides persistent storage for memos using JSON files.

    This class handles the loading, saving, and caching of memo data.
    It implements performance optimizations including lazy loading,
    incremental updates, and caching of frequently accessed data.

    Attributes:
        path: Path to the JSON storage file
        _data: In-memory representation of the store (loaded lazily)
        _modified_commits: Set of commit hashes that have been modified
        _modified_files: Set of file blob SHAs that have been modified
        _last_loaded: Timestamp of when the data was last loaded
        _cache: Dictionary for caching frequently accessed data
    """

    def __init__(self, path: Union[str, Path] = STORE_PRIVATE):
        """
        Initialize a new JsonStore.

        Args:
            path: Path to the JSON storage file. Defaults to the private store.
        """
        self.path = Path(path)
        self._data: Optional[Store] = None
        self._modified_commits: Set[str] = set()
        self._modified_files: Set[str] = set()
        self._last_loaded: Optional[datetime] = None
        self._cache: Dict[str, Any] = {}

    @property
    def data(self) -> Store:
        """
        Lazy loading of store data.

        This property ensures that data is only loaded from the disk when needed,
        improving performance for operations that don't require the full dataset.

        Returns:
            Store: The loaded store data
        """
        if self._data is None:
            self._data = self._load_or_init()
            self._last_loaded = datetime.now(timezone.utc)
        return self._data

    @lru_cache(maxsize=CACHE_SIZE)
    def get_commit_memos(self, commit: str) -> List[Memo]:
        """
        Get memos for a specific commit with caching.

        This method uses LRU caching to avoid repeated lookups for
        frequently accessed commits.

        Args:
            commit: The commit hash to retrieve memos for

        Returns:
            List[Memo]: A list of memos associated with the commit,
                       or an empty list if none exist
        """
        return self.data.commit_memos.get(commit, [])

    @lru_cache(maxsize=CACHE_SIZE)
    def get_file_memos(self, blob_sha: str) -> List[Memo]:
        """
        Get memos for a specific file blob with caching.

        This method uses LRU caching to avoid repeated lookups for
        frequently accessed file blobs.

        Args:
            blob_sha: The blob SHA of the file to retrieve memos for

        Returns:
            List[Memo]: A list of memos associated with the file blob,
                       or an empty list if none exist
        """
        return self.data.files.get(blob_sha, [])

    def _load_or_init(self) -> Store:
        """
        Load the store from disk or initialize a new one if it doesn't exist.

        Returns:
            Store: The loaded or newly initialized store
        """
        if self.path.exists():
            return _deserialize(self.path.read_bytes())
        return Store()

    def reload(self):
        """
        Reload the store from disk.

        This method clears all caches and reloads the data from the disk,
        discarding any unsaved changes.
        """
        self.get_commit_memos.cache_clear()
        self.get_file_memos.cache_clear()
        self._cache.clear()
        self._data = self._load_or_init()
        self._last_loaded = datetime.now(timezone.utc)
        self._modified_commits.clear()
        self._modified_files.clear()

    def mark_commit_modified(self, commit: str):
        """
        Mark a commit as modified for incremental updates.

        This method is used to track which commits have been modified
        so that only those need to be updated when saving.

        Args:
            commit: The commit hash that has been modified
        """
        self._modified_commits.add(commit)

    def mark_file_modified(self, blob_sha: str):
        """
        Mark a file as modified for incremental updates.

        This method is used to track which file blobs have been modified
        so that only those need to be updated when saving.

        Args:
            blob_sha: The blob SHA of the file that has been modified
        """
        self._modified_files.add(blob_sha)

    def save(self):
        """
        Write the current store to disk.

        This method serializes the store to JSON and writes it to the
        configured file path. It also clears the relevant caches for
        modified commits and files to ensure fresh data is loaded next time.

        If no data has been loaded yet, this method does nothing.
        """
        if self._data is None:
            return

        if self._modified_commits:
            self.get_commit_memos.cache_clear()

        if self._modified_files:
            self.get_file_memos.cache_clear()

        self.path.write_bytes(_serialize(self._data))
        self._modified_commits.clear()
        self._modified_files.clear()
