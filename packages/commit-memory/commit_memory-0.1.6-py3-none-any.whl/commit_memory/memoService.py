"""
Business logic service for managing commit memos.

This module provides the MemoService class, which serves as the central component
for all memo-related operations. It acts as an intermediary between the CLI interface
and the storage layer, implementing the core business logic of the application.

The MemoService handles:
- Adding memos to commits and files
- Retrieving memos by commit or file
- Updating existing memos
- Deleting memos
- Searching for memos by various criteria

It uses the GitService for repository interactions and the JsonStore for persistence,
maintaining a clean separation of concerns in the application architecture.
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from . import git_service, models
from .memo_store import JsonStore
from .models import Memo, SharedRef
from .security import decrypt, encrypt_for, sha256
from .trust import Trust
from .validation import (
    ValidationError,
    validate_author,
    validate_file_path,
    validate_line_number,
    validate_memo_text,
)

log = logging.getLogger(__name__)


class MemoService:
    """
    Service class for managing memos in the Commit Memory application.

    This class provides methods for creating, updating, deleting, and searching
    for memos. All user inputs are validated and sanitized before processing to
    ensure data integrity and security.

    Validation rules:
    - Memo text: Cannot be empty, maximum length of 2000 characters
    - Author name: Cannot be empty, maximum length of 100 characters
    - File path: Cannot be empty, maximum length
        of 260 characters, no directory traversal
    - Line number: Must be a positive integer

    All text inputs are sanitized to prevent injection issues.
    """

    def __init__(self, store: JsonStore):
        self.store = store
        log.debug("MemoService initialised with store %s", store.path)

    def add_commit_memo(
        self, memo: str, commit: Optional[str] = None, shared: bool = False
    ) -> str:
        """
        Add a memo to a commit.

        Args:
            memo: The memo text to add (will be validated and sanitized)
            commit: Optional commit hash or reference (defaults to HEAD)
            shared: Whether the memo should be shared with others

        Returns:
            The resolved commit hash

        Raises:
            ValidationError: If the memo text is invalid (empty or too long)
        """
        try:
            sanitized_memo = validate_memo_text(memo)
        except ValidationError as e:
            log.error("Validation error: %s", str(e))
            raise

        commit = git_service.resolve_commit(commit or "HEAD")
        visibility = "shared" if shared else "private"

        log.info("Adding %s commit-level memo to %s", visibility, commit[:7])
        log.debug("memo text: %s", sanitized_memo)
        self.store.data.commit_memos.setdefault(commit, []).append(
            models.Memo(
                memo=sanitized_memo,
                author=git_service.current_author(),
                visibility="shared" if shared else "private",
            )
        )
        self.store.mark_commit_modified(commit)
        self.store.save()
        return commit

    def add_file_memo(
        self,
        file: Path,
        line: int,
        memo: str,
        commit: Optional[str] = None,
        shared: bool = False,
    ) -> tuple[str, str]:
        """
        Add a memo to a specific file and line.

        Args:
            file: Path to the file (will be validated and sanitized)
            line: Line number in the file (will be validated)
            memo: The memo text to add (will be validated and sanitized)
            commit: Optional commit hash or reference
            shared: Whether the memo should be shared with others

        Returns:
            A tuple of (commit_hash, blob_sha)

        Raises:
            ValidationError: If any input is invalid:
                - a File path is empty, too long, or contains dangerous patterns
                - Line number is not a positive integer
                - a Memo text is empty or too long
            FileNotFoundError: If the file does not exist
        """
        try:
            file_path = validate_file_path(str(file))
            validated_line = validate_line_number(line)
            sanitized_memo = validate_memo_text(memo)
        except ValidationError as e:
            log.error("Validation error: %s", str(e))
            raise

        repo_root = git_service.repo_root()
        abs_path = repo_root / file_path
        if not abs_path.exists():
            log.error("Path %s does not exist on disk", abs_path)
            raise FileNotFoundError(abs_path)

        if commit is None:
            if validated_line is None:
                raise ValidationError(
                    "Line number is required when commit is not specified"
                )
            commit = git_service.blame_commit(file, validated_line)
        commit = git_service.resolve_commit(commit)
        blob_sha = git_service.blob_sha_at(commit, file)

        visibility = "shared" if shared else "private"
        log.info(
            "Adding %s file-line memo to %s:%d @%s",
            visibility,
            file_path,
            validated_line,
            commit[:7],
        )
        log.debug("blob sha: %s  memo text: %s", blob_sha[:8], sanitized_memo)

        memo_obj = models.Memo(
            memo=sanitized_memo,
            author=git_service.current_author(),
            visibility="shared" if shared else "private",
            file=file_path,
            line=validated_line,
            commit=commit,
        )
        self.store.data.files.setdefault(blob_sha, []).append(memo_obj)
        self.store.mark_file_modified(blob_sha)
        self.store.save()
        return commit, blob_sha

    def get_commit_memos(
        self, commit: str
    ) -> tuple[list[models.Memo], list[models.Memo]]:
        commit = git_service.resolve_commit(commit)
        log.debug("Fetching memos for commit %s", commit)

        # Use the cached method to get commit memos
        raw_commit = self.store.get_commit_memos(commit)

        if isinstance(raw_commit, dict):
            raw_commit = [models.Memo(**raw_commit)]
        elif isinstance(raw_commit, models.Memo):
            raw_commit = [raw_commit]

        raw_file = self._get_file_memos_for_commit(commit)

        log.info(
            "Found %d commit memos and %d file-line memos for %s",
            len(raw_commit),
            len(raw_file),
            commit[:7],
        )

        if raw_commit and not isinstance(raw_commit[0], models.Memo):
            self.store.data.commit_memos[commit] = raw_commit
            self.store.mark_commit_modified(commit)
            self.store.save()

        return raw_commit, raw_file

    def _get_memo_at_index(
        self, commit: str, index: int, is_file_memo: bool
    ) -> tuple[models.Memo, Optional[str]]:
        """Helper method to get memo at index with all necessary validation
        Returns tuple of (memo, blob_sha). Blob_sha is None for commit memos"""
        commit = git_service.resolve_commit(commit)
        commit_memos, file_memos = self.get_commit_memos(commit)
        log.debug("Looking up memo for %s:%d", commit[:7], index)

        if is_file_memo:
            if not file_memos:
                log.debug("No file memos found for commit %s", commit[:7])
                raise ValueError(f"No file memos found for commit {commit[:7]}")
            file_memos = self._get_file_memos_for_commit(commit)
            if not (0 <= index < len(file_memos)):
                log.debug(
                    "File memo index %d out of range (0-%d)", index, len(file_memos) - 1
                )
                raise IndexError(
                    f"File memo index {index} out of range (0-{len(file_memos) - 1})"
                )
            target_memo = file_memos[index]
            if target_memo.file is None:
                raise ValueError("File path is missing in the memo")
            blob_sha = git_service.blob_sha_at(commit, target_memo.file)
            return target_memo, blob_sha
        else:
            if not commit_memos:
                log.debug("No commit memos found for commit %s", commit[:7])
                raise ValueError(f"No commit memos found for commit {commit[:7]}")
            if not (0 <= index < len(commit_memos)):
                log.debug(
                    "Commit memo index %d out of range (0-%d)",
                    index,
                    len(commit_memos) - 1,
                )
                raise IndexError(
                    f"Commit memo index {index} out of range "
                    f"(0-{len(commit_memos) - 1})"
                )
            return commit_memos[index], None

    def update_memo(
        self, commit: str, index: int, new_memo: str, is_file_memo: bool = False
    ) -> models.Memo:
        """
        Update a memo at the specified index for a given commit.

        Only PRIVATE memos can be updated. Shared memos are immutable; create a
        new shared memo (or reshare) instead.

        Raises:
            ValidationError: bad memo text
            ValueError: shared/immutable, not found, or invalid file memo
            IndexError: index out of range
        """
        try:
            sanitized_memo = validate_memo_text(new_memo)
        except ValidationError as e:
            log.error("Validation error: %s", str(e))
            raise

        target_memo, blob_sha = self._get_memo_at_index(commit, index, is_file_memo)

        if getattr(target_memo, "visibility", "private") == "shared":
            raise ValueError(
                "Refusing to update a shared memo. Shared memos are immutable; "
                "create a new shared memo with the desired text/recipients instead."
            )

        if is_file_memo:
            if blob_sha is None:
                raise ValueError("Invalid blob SHA for file memo")
            memo_list = self.store.data.files[blob_sha]
            for memo in memo_list:
                if (
                    memo.file == target_memo.file
                    and memo.line == target_memo.line
                    and memo.created == target_memo.created
                ):
                    memo.memo = sanitized_memo
                    self.store.mark_file_modified(blob_sha)
                    self.store.save()
                    return memo
            raise ValueError("Memo not found")
        else:
            target_memo.memo = sanitized_memo
            if target_memo.commit:
                commit_sha: str = target_memo.commit
            else:
                commit_sha = git_service.resolve_commit(commit)
                target_memo.commit = commit_sha

            self.store.mark_commit_modified(commit_sha)
            self.store.save()
            return target_memo

    def _get_file_memos_for_commit(self, sha: str) -> list[models.Memo]:
        out: list[models.Memo] = []
        for blob_sha in self.store.data.files.keys():
            memos = self.store.get_file_memos(blob_sha)
            for m in memos:
                if m.commit == sha:
                    out.append(m)
        log.debug("file-line memo scan for %s yielded %d items", sha[:7], len(out))
        return out

    def delete_memo(
        self, commit: str, index: int, is_file_memo: bool = False
    ) -> models.Memo:
        """Delete a memo at the specified index for a given commit.

        Only private memos can be deleted. Shared memos are immutable envelopes
        and must be rotated/reshared instead.
        """
        target_memo, blob_sha = self._get_memo_at_index(commit, index, is_file_memo)

        if getattr(target_memo, "visibility", "private") == "shared":
            raise ValueError(
                "Refusing to delete a shared memo. Shared memos are immutable; "
                "create a new shared memo with the desired recipients instead."
            )

        if is_file_memo:
            if blob_sha is None:
                raise ValueError("Invalid blob SHA for file memo")
            memo_list = self.store.data.files[blob_sha]
            for memo in memo_list:
                if (
                    memo.file == target_memo.file
                    and memo.line == target_memo.line
                    and memo.created == target_memo.created
                ):
                    self.store.data.files[blob_sha].remove(memo)
                    self.store.mark_file_modified(blob_sha)
                    self.store.save()
                    return memo
            raise ValueError("Memo not found")
        else:
            removed_memo = self.store.data.commit_memos[commit].pop(index)
            removed_memo.commit = commit
            self.store.mark_commit_modified(commit)
            self.store.save()
            return removed_memo

    def delete_last(self, commit: str, is_file_memo: bool = False) -> models.Memo:
        """Delete the most recent memo for the given commit."""
        if not is_file_memo:
            lst = self.store.data.commit_memos.get(commit) or []
            if not lst:
                raise IndexError(f"No commit memos found for {commit[:7]}")
            if getattr(lst[-1], "visibility", "private") == "shared":
                raise ValueError("Refusing to delete a shared memo.")
            removed = lst.pop()
            removed.commit = commit
            self.store.mark_commit_modified(commit)
            self.store.save()
            return removed

        pool: list[tuple[str, models.Memo]] = []
        for blob_sha, memos in (self.store.data.files or {}).items():
            for memo in memos:
                if getattr(memo, "commit", None) == commit:
                    pool.append((blob_sha, memo))

        if not pool:
            raise IndexError(f"No file memos found for {commit[:7]}")

        default_time = datetime.min.replace(tzinfo=timezone.utc)
        blob_sha, target_memo = max(
            pool,
            key=lambda pair: getattr(pair[1], "created", default_time),
        )

        if getattr(target_memo, "visibility", "private") == "shared":
            raise ValueError("Refusing to delete a shared memo.")

        self.store.data.files[blob_sha].remove(target_memo)
        self.store.mark_file_modified(blob_sha)
        self.store.save()
        return target_memo

    def delete_all(self, commit: Optional[str], is_file_memo: bool = False) -> int:
        """Delete ALL private memos.
        - If commit is None: operate across the entire scope.
        - If commit is set: operate only for that commit.
        Shared memos are preserved. Returns the number of deleted memos.
        """
        deleted = 0

        if commit is None:
            if not is_file_memo:
                for sha, lst in (self.store.data.commit_memos or {}).items():
                    keep_cm_global = [
                        m
                        for m in (lst or [])
                        if getattr(m, "visibility", "private") == "shared"
                    ]
                    if len(keep_cm_global) != len(lst or []):
                        deleted += len(lst or []) - len(keep_cm_global)
                        self.store.data.commit_memos[sha] = keep_cm_global
                        self.store.mark_commit_modified(sha)
                if deleted:
                    self.store.save()
                return deleted

            mutated_shas_global: set[str] = set()
            for blob_sha, memos in list((self.store.data.files or {}).items()):
                keep_fm_global = [
                    m
                    for m in (memos or [])
                    if getattr(m, "visibility", "private") == "shared"
                ]
                if len(keep_fm_global) != len(memos or []):
                    deleted += len(memos or []) - len(keep_fm_global)
                    self.store.data.files[blob_sha] = keep_fm_global
                    mutated_shas_global.add(blob_sha)
            if mutated_shas_global:
                for s in mutated_shas_global:
                    self.store.mark_file_modified(s)
                self.store.save()
            return deleted

        if not is_file_memo:
            lst = self.store.data.commit_memos.get(commit) or []
            keep_cm_commit = [
                m for m in lst if getattr(m, "visibility", "private") == "shared"
            ]
            deleted = len(lst) - len(keep_cm_commit)
            if deleted:
                self.store.data.commit_memos[commit] = keep_cm_commit
                self.store.mark_commit_modified(commit)
                self.store.save()
            return deleted

        mutated_shas_per_commit: set[str] = set()
        for blob_sha, memos in list((self.store.data.files or {}).items()):
            keep_fm_commit: list[models.Memo] = []
            drop_count_commit = 0
            for m in memos or []:
                same_commit = getattr(m, "commit", None) == commit
                is_shared = getattr(m, "visibility", "private") == "shared"
                if same_commit and not is_shared:
                    drop_count_commit += 1
                else:
                    keep_fm_commit.append(m)
            if drop_count_commit:
                self.store.data.files[blob_sha] = keep_fm_commit
                mutated_shas_per_commit.add(blob_sha)
                deleted += drop_count_commit
        if mutated_shas_per_commit:
            for s in mutated_shas_per_commit:
                self.store.mark_file_modified(s)
            self.store.save()
        return deleted

    def search(self, author: str) -> list[models.Memo]:
        """
        Search for memos by author name.

        Args:
            author: The author name to search for (will be
                    validated and sanitized if provided)
                   Is None or empty, returns all memos

        Returns:
            A list of Memo objects matching the search criteria

        Raises:
            ValidationError: If the author name is invalid (too long)
        """
        if author:
            try:
                sanitized_author = validate_author(author)
            except ValidationError as e:
                log.error("Validation error: %s", str(e))
                raise
        else:
            sanitized_author = author

        memos = []
        log.debug("Searching for memos by author %s", sanitized_author)

        for commit in self.store.data.commit_memos.keys():
            commit_memos = self.store.get_commit_memos(commit)
            for memo in commit_memos:
                if sanitized_author and memo.author.__contains__(sanitized_author):
                    memos.append(memo)
                elif not sanitized_author:
                    memos.append(memo)

        for blob_sha in self.store.data.files.keys():
            file_memos = self.store.get_file_memos(blob_sha)
            for memo in file_memos:
                if sanitized_author and memo.author.__contains__(sanitized_author):
                    memos.append(memo)
                elif not sanitized_author:
                    memos.append(memo)

        return memos

    def get_all_memos(self) -> list[models.Memo]:
        """Get all memos from both commit and file stores"""
        memos = []

        for commit in self.store.data.commit_memos.keys():
            commit_memos = self.store.get_commit_memos(commit)
            memos.extend(commit_memos)

        for blob_sha in self.store.data.files.keys():
            file_memos = self.store.get_file_memos(blob_sha)
            memos.extend(file_memos)

        return memos

    def add_shared_memo(
        self,
        commit: str,
        memo: str,
        recipients: List[str],
        file: Optional[Path] = None,
        line: Optional[int] = None,
        include_self: bool = True,
    ):
        """Create an encrypted memo for selected
        recipients and attach it to a commit (or file@line)."""
        full = git_service.resolve_commit(commit)
        author = git_service.current_author()

        trust = Trust.load()
        missing = [r for r in recipients if r not in trust.users]
        if missing:
            raise ValueError(f"Unknown recipients in trust.yml: {', '.join(missing)}")

        rkeys = [trust.users[r] for r in recipients]

        if include_self:
            for alias, key in trust.users.items():
                if alias.lower() in (
                    author.lower(),
                    "ilia",
                ):
                    if key not in rkeys:
                        rkeys.append(key)
                    break

        title = memo.splitlines()[0][:80]
        payload = {
            "v": 1,
            "commit": full,
            "title": title,
            "body": memo,
            "author": author,
            "created": datetime.now(timezone.utc).isoformat(),
            "recipients": recipients,
        }
        if file is not None and line is not None:
            payload["file"] = str(file).replace("\\", "/")
            payload["line"] = int(line)

        plaintext = json.dumps(
            payload, ensure_ascii=False, separators=(",", ":")
        ).encode("utf-8")

        ciphertext = encrypt_for(rkeys, plaintext)
        digest = sha256(ciphertext)
        short = full[:12]

        rel_dir = Path(".commit-memos/shared") / short
        rel_dir.mkdir(parents=True, exist_ok=True)
        rel_path = rel_dir / f"{digest[:12]}.json.age"
        rel_path.write_bytes(ciphertext)

        note = json.dumps(
            {"v": 1, "paths": [str(rel_path).replace("\\", "/")], "sha": digest}
        )
        git_service.add_note(full, note)

        m = Memo(
            memo=f"[shared] {title}",
            author=author,
            visibility="shared",
            file=str(file) if file is not None else None,
            line=int(line) if line is not None else None,
            commit=full,
            shared=SharedRef(
                path=str(rel_path).replace("\\", "/"), digest=digest, title=title
            ),
        )

        data = self.store.data
        if file is None or line is None:
            data.commit_memos.setdefault(full, []).append(m)
            self.store.mark_commit_modified(full)
        else:
            data.commit_memos.setdefault(full, []).append(m)
            self.store.mark_commit_modified(full)

        self.store.save()
        return (
            (full, str(rel_path)) if (file is not None and line is not None) else full
        )

    def _ensure_shared_stub(
        self, commit_sha: str, path: str, digest: str, title: Optional[str]
    ) -> bool:
        """
        Make sure the local store has a stub Memo for this shared ciphertext.
        Returns True if a new stub was added.
        """
        path = str(Path(path).as_posix())
        existing = self.store.data.commit_memos.get(commit_sha, [])
        for m in existing:
            if (
                getattr(m, "visibility", "private") == "shared"
                and m.shared
                and m.shared.digest == digest
            ):
                return False

        stub_title = title or "[shared memo]"
        author = None
        try:
            plaintext = decrypt(Path(path).read_bytes())
            obj = json.loads(plaintext.decode("utf-8"))
            author = obj.get("author")
            if not title:
                stub_title = f"[shared] {obj.get('title', 'memo')}"
        except Exception as e:
            logging.debug(
                "Failed to decrypt/parse shared file at %s for commit %s: %s",
                path,
                commit_sha,
                e,
            )
            pass

        memo = Memo(
            memo=stub_title,
            author=author or "(unknown)",
            visibility="shared",
            commit=commit_sha,
            shared=SharedRef(path=path, digest=digest, title=stub_title),
        )
        self.store.data.commit_memos.setdefault(commit_sha, []).append(memo)
        if hasattr(self.store, "mark_commit_modified"):
            self.store.mark_commit_modified(commit_sha)
        return True

    def pull(self) -> None:
        """
        1) Fetch refs/notes/memos
        2) Parse each note payload
        3) Ensure there is a local stub for each shared memo
        """
        git_service.fetch_notes()
        count = 0
        for commit_sha, payload in git_service.list_all_notes():
            paths = payload.get("paths") or []
            digest = payload.get("sha") or ""
            title = payload.get("title")
            for p in paths:
                created = self._ensure_shared_stub(
                    commit_sha=commit_sha,
                    path=p,
                    digest=digest,
                    title=title,
                )
                if created:
                    count += 1
        if count:
            self.store.save()
