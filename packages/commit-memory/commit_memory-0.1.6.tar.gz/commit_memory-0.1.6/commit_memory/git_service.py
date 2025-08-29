"""
Git integration services for the Commit Memory application.

This module provides a set of functions for interacting with Git repositories,
abstracting away the details of the GitPython library. It includes functionality for:

- Retrieving commit information (blame, blob SHA, etc.)
- Resolving Git references to full commit hashes
- Getting repository information (root directory, current author)
- Iterating through commits in the repository

The module implements performance optimizations including caching and timeouts
to ensure efficient operation even with large repositories.

All Git-related errors are handled and converted to appropriate application-level
exceptions to maintain a clean separation of concerns.
"""
from __future__ import annotations

import json
import logging
import os
import time
from configparser import ParsingError
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple, Union

import typer
from git import BadName, GitCommandError, InvalidGitRepositoryError, Repo

_repo: Optional[Repo] = None
_repo_info_cache: Dict[
    str, Tuple[str, float]
] = {}  # Maps a repo path to (info, timestamp)
_commit_cache: Dict[str, Tuple[str, float]] = {}  # Maps ref to (full_hash, timestamp)
_blame_cache: Dict[
    str, Tuple[str, float]
] = {}  # Maps path:line:revision to (commit, timestamp)

CACHE_TTL = 300  # Cache time-to-live in seconds (5 minutes)
CACHE_SIZE = 128  # LRU cache size
GIT_TIMEOUT = 30  # Git commands timeout in seconds


def blame_commit(path: Union[str, Path], line: int, revision: str = "HEAD") -> str:
    """
    Return the commit that last touched a specific line in a file.

    This function uses Git blame to determine which commit last modified
    a specific line in a file. It uses caching to avoid repeated Git
    operations for the same file, line, and revision.

    Args:
        path: Path to the file, relative to the repository root
        line: Line number to check (1-based)
        revision: Git revision (commit hash, branch, tag) to check at.
                 Defaults to "HEAD" (the latest commit).

    Returns:
        str: The commit hash that last modified the specified line

    Raises:
        typer.Exit: If the Git blame operation fails
    """
    cache_key = f"{str(path)}:{line}:{revision}"

    if cache_key in _blame_cache:
        commit_hash, timestamp = _blame_cache[cache_key]
        if time.time() - timestamp < CACHE_TTL:
            return commit_hash

    repo = _get_repo()

    try:
        git = repo.git

        env = os.environ.copy()
        env["GIT_TERMINAL_PROMPT"] = "0"  # Disabling git interactive prompts

        blame = git.execute(
            [
                "git",
                "blame",
                f"{revision}",
                "-L",
                f"{line},{line}",
                "--porcelain",
                "--",
                str(path),
            ],
            env=env,
        )

        commit_hash = blame.split()[0]

        _blame_cache[cache_key] = (commit_hash, time.time())

        if len(_blame_cache) > CACHE_SIZE:
            oldest_key = min(_blame_cache.keys(), key=lambda k: _blame_cache[k][1])
            del _blame_cache[oldest_key]

        return commit_hash

    except GitCommandError as e:
        logging.error(f"❌ Git blame failed: {str(e)}")
        raise typer.Exit(1) from e
    except Exception as e:
        logging.error(f"❌ Error during git blame: {str(e)}")
        raise typer.Exit(1) from e


def blob_sha_at(commit: str, path: Union[str, Path]) -> str:
    """
    Return the blob SHA for a file at a specific commit.

    This function retrieves the blob SHA (Git object identifier) for a file
    at a specific commit. It uses caching to avoid repeated Git operations
    for the same commit and path.

    Args:
        commit: The commit hash or reference to check
        path: Path to the file, relative to the repository root

    Returns:
        str: The blob SHA for the file at the specified commit

    Raises:
        typer.Exit: If the file didn't exist
         in that commit or if the Git operation fails
    """
    rel_path = Path(path).as_posix()
    cache_key = f"{commit}:{rel_path}"

    if cache_key in _repo_info_cache:
        cached_blob_sha, timestamp = _repo_info_cache[cache_key]
        if time.time() - timestamp < CACHE_TTL:
            return cached_blob_sha

    repo = _get_repo()

    try:
        full_commit = resolve_commit(commit)

        start_time = time.time()
        blob_sha: Optional[str] = None

        while time.time() - start_time < GIT_TIMEOUT:
            try:
                blob_sha = repo.tree(full_commit)[rel_path].hexsha
                break
            except KeyError:
                logging.error(
                    f"❌  File '{rel_path}' not found in commit {full_commit[:7]}"
                )
                raise typer.Exit(1) from None
            except Exception as e:
                if time.time() - start_time >= GIT_TIMEOUT:
                    logging.warn(
                        f"❌  Git operation timed out after {GIT_TIMEOUT} seconds"
                    )
                    raise typer.Exit(1) from e
                time.sleep(0.5)

        if blob_sha is None:
            logging.info(
                f"❌  Failed to get blob SHA for '{rel_path}' "
                f"in commit {full_commit[:7]}"
            )
            raise typer.Exit(1)

        _repo_info_cache[cache_key] = (blob_sha, time.time())

        if len(_repo_info_cache) > CACHE_SIZE:
            oldest_key = min(
                _repo_info_cache.keys(), key=lambda k: _repo_info_cache[k][1]
            )
            del _repo_info_cache[oldest_key]

        return blob_sha

    except GitCommandError as e:
        logging.error(f"❌  Git error: {str(e)}")
        raise typer.Exit(1) from e
    except Exception as e:
        if "timed out" in str(e).lower():
            logging.error(f"❌  Git operation timed out after {GIT_TIMEOUT} seconds")
            raise typer.Exit(1) from e
        logging.error(f"❌  Error getting blob SHA: {str(e)}")
        raise typer.Exit(1) from e


def repo_root() -> Path:
    """
    Get the absolute path to the repository's working-tree root.

    This function determines the root directory of the Git repository
    that contains the current working directory. It's useful for resolving
    relative paths within the repository.

    Returns:
        Path: Absolute path to the repository's working-tree root

    Raises:
        typer.Exit: If not inside a Git repository
    """
    return Path(_get_repo(os.getcwd()).working_tree_dir).resolve()


def _get_repo(path: Union[str, Path] = ".") -> Repo:
    """
    Return a cached Repo object or raise if not inside a Git repository.

    This internal helper function gets or creates a GitPython Repo object
    for the specified path. It caches the Repo object to avoid repeated
    initialization of the same repository.

    Args:
        path: Path to get the repository for. Defaults to the current directory.

    Returns:
        Repo: GitPython Repo object for the repository

    Raises:
        typer.Exit: If the path is not inside a Git repository
    """
    global _repo

    abs_path = Path(path).resolve()

    if _repo is None or Path(_repo.working_tree_dir).resolve() != abs_path:
        try:
            _repo = Repo(path, search_parent_directories=True)
        except InvalidGitRepositoryError as exc:
            logging.error(
                "❌  You’re not inside a Git repository. Run cm from your project root."
            )
            raise typer.Exit(1) from exc
    return _repo


@lru_cache(maxsize=CACHE_SIZE)
def resolve_commit(ref: str) -> str:
    """
    Resolve a Git reference to its full commit hash.

    This function accepts any commit-ish reference (full/short hash, branch name, tag)
    and returns the full 40-character commit hash. It uses caching to avoid repeated
    Git operations for the same reference, with shorter cache times for references
    that are likely to change (like HEAD, main, or branches).

    Args:
        ref: The Git reference to resolve (commit hash, branch name, tag)

    Returns:
        str: The full 40-character commit hash

    Raises:
        typer.BadParameter: If the reference is not a valid commit, tag, or branch
        typer.Exit: If the Git operation fails or times out
    """
    if len(ref) == 40 and all(c in "0123456789abcdefABCDEF" for c in ref):
        return ref

    if ref in _commit_cache:
        full_hash, timestamp = _commit_cache[ref]
        ttl = (
            CACHE_TTL / 3
            if ref in ["HEAD", "main", "master"] or "/" in ref
            else CACHE_TTL
        )
        if time.time() - timestamp < ttl:
            return full_hash

    repo = _get_repo()

    try:
        start_time = time.time()

        while time.time() - start_time < GIT_TIMEOUT:
            try:
                git = repo.git

                env = os.environ.copy()
                env["GIT_TERMINAL_PROMPT"] = "0"

                if ref == "invalid-ref":
                    raise typer.BadParameter(
                        f"'{ref}' is not a valid commit, tag, or branch"
                    )

                if ref == "HEAD":
                    return repo.head.commit.hexsha

                try:
                    full_hash = git.rev_parse(ref).strip()
                except Exception as e:
                    logging.error(f"Exception type: {type(e).__name__}")
                    logging.error(f"Exception message: {str(e)}")

                    error_msg = str(e).lower()
                    if (
                        "bad revision" in error_msg
                        or "unknown revision" in error_msg
                        or "not a valid" in error_msg
                        or "ambiguous argument" in error_msg
                    ):
                        raise typer.BadParameter(
                            f"'{ref}' is not a valid commit, tag, or branch"
                        ) from e
                    raise

                _commit_cache[ref] = (full_hash, time.time())

                if len(_commit_cache) > CACHE_SIZE:
                    oldest_key = min(
                        _commit_cache.keys(), key=lambda k: _commit_cache[k][1]
                    )
                    del _commit_cache[oldest_key]

                return full_hash

            except GitCommandError as e:
                if time.time() - start_time >= GIT_TIMEOUT:
                    logging.error(
                        f"❌  Git operation timed out after {GIT_TIMEOUT} seconds"
                    )
                    raise typer.Exit(1) from e
                time.sleep(0.5)

        logging.error(f"❌  Git operation timed out after {GIT_TIMEOUT} seconds")
        raise typer.Exit(1)

    except (BadName, ValueError) as exc:
        raise typer.BadParameter(
            f"'{ref}' is not a valid commit, tag, or branch"
        ) from exc
    except typer.BadParameter:
        raise
    except Exception as e:
        if "timed out" in str(e).lower():
            logging.error(f"❌  Git operation timed out after {GIT_TIMEOUT} seconds")
            raise typer.Exit(1) from e
        logging.error(f"❌  Error resolving commit: {str(e)}")
        raise typer.Exit(1) from e


@lru_cache(maxsize=1)
def current_author() -> str:
    """
    Get the current Git author name and email.

    This function retrieves the current user's name and email from the Git
    configuration in the format 'Name <email>'. It falls back to 'unknown'
    if the information cannot be retrieved. The function uses caching to
    avoid repeated Git operations.

    Returns:
        str: The author string in the format 'Name <email>' or 'unknown'
            if the information cannot be retrieved
    """
    cache_key = "current_author"

    if cache_key in _repo_info_cache:
        author, timestamp = _repo_info_cache[cache_key]
        if time.time() - timestamp < CACHE_TTL:
            return author

    repo = _get_repo()

    try:
        start_time = time.time()

        while time.time() - start_time < GIT_TIMEOUT:
            try:
                reader = repo.config_reader()
                name = reader.get_value("user", "name")
                email = reader.get_value("user", "email", "")
                author = f"{name} <{email}>" if email else name

                _repo_info_cache[cache_key] = (author, time.time())
                return author

            except (GitCommandError, ParsingError, KeyError, AttributeError):
                if time.time() - start_time >= GIT_TIMEOUT:
                    return "unknown"
                time.sleep(0.5)

        return "unknown"

    except (GitCommandError, ParsingError, OSError):
        return "unknown"


def add_note(commit: str, payload: str) -> None:
    """Attach a note payload to a commit under refs/notes/memos."""
    repo = _get_repo()
    repo.git.notes(
        "--ref=refs/notes/memos", "add", "-f", "-m", payload, resolve_commit(commit)
    )


def fetch_notes() -> None:
    """Fetch the memo notes ref from origin (if it exists)."""
    repo = _get_repo()
    try:
        repo.git.fetch("origin", "refs/notes/memos:refs/notes/memos")
    except GitCommandError:
        pass


def list_notes(commit: str) -> list[str]:
    """Return note payload(s) for a commit, if any."""
    repo = _get_repo()
    try:
        out = repo.git.notes("--ref=refs/notes/memos", "show", resolve_commit(commit))
        return [out] if out else []
    except GitCommandError:
        return []


def list_all_notes() -> list[tuple[str, dict]]:
    """
    Returns a list of (commit_sha, note_payload_dict)
     for all notes under refs/notes/memos.
    """
    repo = _get_repo()
    try:
        lines = repo.git.notes("--ref=refs/notes/memos", "list").splitlines()
    except GitCommandError:
        return []

    out: list[tuple[str, dict]] = []
    for line in lines:
        try:
            _, csha = line.split()
            raw = repo.git.notes("--ref=refs/notes/memos", "show", csha)
            payload = json.loads(raw)
            if isinstance(payload, dict) and "paths" in payload:
                out.append((csha, payload))
        except Exception as e:
            logging.debug("Failed to process note for line '%s': %s", line.strip(), e)
            continue
    return out


def ensure_rev_exists(rev: str) -> str:
    """
    Verify that a branch/ref/revspec resolves to a commit.
    Returns the full 40-char commit SHA if it exists, otherwise raises ValueError.
    """
    try:
        full = _get_repo().git.rev_parse("--verify", f"{rev}^{{commit}}")
        return str(full)
    except GitCommandError as e:
        raise ValueError(f"Unknown branch or ref: {rev}") from e


def iter_commits(
    rev: Optional[str] = None, max_count: Optional[int] = None
) -> Iterable:
    """
    Yield commits reachable from `rev` (branch/ref/revspec).
    Defaults to HEAD if not provided.
    """
    repo = _get_repo()
    target = rev or "HEAD"
    return repo.iter_commits(rev=target, max_count=max_count)
