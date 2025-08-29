"""
Command-line interface for the Commit Memory application.

This module defines the CLI commands and
their implementations using the Typer framework.
It provides commands for:

- add: Adding memos to commits or specific lines in files
- update: Updating existing memos
- delete: Deleting memos
- search: Searching for memos by various criteria
- show: Displaying memos for a specific commit
- log: Displaying a log of commits with memos

The module uses Rich for formatted terminal output and delegates business logic
to the MemoService. It handles command-line arguments, options, and user feedback
while maintaining a separation between the interface and the underlying functionality.
"""
import json
import logging
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, cast

import rich
import typer
from rich.console import Console

from commit_memory import git_service, memo_store
from commit_memory.git_service import _get_repo
from commit_memory.memo_formatter import (
    MemoFormatter,
    add_overview_row,
    commit_header_row,
    format_memo_line,
    format_memo_panel,
    format_shared_panel,
    locked_shared_panel,
    make_overview_table,
    shared_to_panel,
)
from commit_memory.memoService import MemoService
from commit_memory.security import decrypt
from commit_memory.trust import (
    Groups,
    Trust,
    aliases_missing_in_trust,
    expand_recipients,
)

app = typer.Typer()
store = memo_store.JsonStore()
console = Console()
formatter = MemoFormatter(console)
memo_service = MemoService(store)
logger = logging.getLogger(__name__)
group_app = typer.Typer(help="Manage recipient groups")
app.add_typer(group_app, name="group")


@app.command()
def philosophy():
    """Explain why this tool is intentionally simple"""
    typer.echo("🎯 Commit Memory Philosophy:")
    typer.echo("")
    typer.echo("This tool is designed for SIMPLE, MANUAL memo management:")
    typer.echo("• ✅ Add individual memos with 'cm add'")
    typer.echo("• ✅ View memos with 'cm log' and 'cm show'")
    typer.echo("• ✅ Delete specific memos with 'cm delete'")
    typer.echo("")
    typer.echo("❌ NO bulk operations, imports, syncing, or automation")
    typer.echo("❌ This prevents data corruption and keeps things predictable")
    typer.echo("")
    typer.echo("💡 Use git to backup/restore your memo files instead!")


@app.command()
def add(
    file: Optional[Path] = typer.Argument(None, help="path relative to repo root"),
    line: Optional[int] = typer.Argument(None, help="1-based line number"),
    commit: Optional[str] = typer.Option(
        None, "--commit", "-c", help="commit hash / ref (defaults to HEAD)"
    ),
    memo: str = typer.Option(..., prompt=True),
    shared: bool = typer.Option(False, "--shared", help="store in shared file"),
    to: Optional[List[str]] = typer.Option(
        None,
        "--to",
        help="comma-separated recipients (aliases from "
        ".commit-memos/trust.yml);repeatable: --to alice --to bob",
    ),
    group: Optional[List[str]] = typer.Option(
        None,
        "--group",
        "-g",
        help="group name(s) from .commit-memos/groups.yml; "
        "repeatable: --group dev --group team-infra",
    ),
):
    """
    Add a new memo to a commit or a specific line in a file.

    This command creates a new memo and associates it with either a commit
    or a specific line in a file at a particular commit. If both file and line
    are provided, the memo is attached to that specific line. Otherwise, it's
    attached to the commit as a whole.

    Args:
        file: Path to the file, relative to the repository root
        line: Line number in the file (1-based)
        commit: Commit hash or reference to attach the memo to
        memo: The text content of the memo
        shared: Whether to store the memo in the shared file (visible to others)
        :param file:
        :param line:
        :param commit:
        :param memo:
        :param shared:
        :param group:
        :param to:
    """
    logger.info("shared=%s  file=%s  line=%s", shared, file, line)

    try:
        recipients: List[str] = expand_recipients(user_aliases=to, group_names=group)
    except ValueError as e:
        logger.error(str(e))
        raise typer.Exit(1)

    try:
        cm_ref = commit or "HEAD"

        if shared:
            if not recipients:
                raise typer.BadParameter(
                    "--shared requires recipients. Use --to alice,bob "
                    "and/or --group dev,team-infra"
                )

            if file is None or line is None:
                commit_hash = memo_service.add_shared_memo(
                    commit=cm_ref, memo=memo, recipients=recipients
                )
                logger.info(f"✅ " f"shared memo saved for commit {commit_hash[:7]}")
            else:
                commit_hash, _ = memo_service.add_shared_memo(
                    commit=cm_ref,
                    memo=memo,
                    recipients=recipients,
                    file=file,
                    line=line,
                )
                logger.info(
                    f"✅ " f"shared memo saved for {file}:{line} @{commit_hash[:7]}"
                )
            return

        if file is None or line is None:
            commit_hash = memo_service.add_commit_memo(memo, cm_ref, shared=False)
            logger.info(f"✅ " f"memo saved for commit {commit_hash[:7]}")
        else:
            commit_hash, _ = memo_service.add_file_memo(
                file, line, memo, cm_ref, shared=False
            )
            logger.info(f"✅ " f"memo saved for {file}:{line} @{commit_hash[:7]}")
    except FileNotFoundError:
        logger.debug("❌ file not found")
        raise typer.Exit(1)


@app.command()
def update(
    commit: str = typer.Option(..., "--commit", "-c", help="commit hash / ref"),
    index: int = typer.Option(..., "--index", "-i", help="memo index (0-based)"),
    memo: str = typer.Option(..., prompt=True, help="new memo text"),
    file_memo: bool = typer.Option(
        False, "--file", "-f", help="update file memo instead of commit memo"
    ),
):
    """
    Update an existing memo by its index.

    This command updates the text of an existing memo identified by its
    commit and index. The index is 0-based and refers to the position of
    the memo in the list of memos for the specified commit.

    By default, this command updates commit memos. Use the --file flag
    to update file memos instead.

    Args:
        commit: Commit hash or reference that the memo is attached to
        index: Zero-based index of the memo to update
        memo: The new text content for the memo
        file_memo: Whether to update a file memo instead of a commit memo

    Raises:
        typer.Exit: If the memo cannot be found or updated
    """
    try:
        updated_memo = memo_service.update_memo(commit, index, memo, file_memo)
        type_str = "file" if file_memo else "commit"
        if file_memo:
            logger.info(
                f"✅ Updated {type_str} memo at {updated_memo.file}:{updated_memo.line}"
            )
        else:
            logger.info(f"✅ Updated {type_str} memo for commit {commit[:7]}")
    except IndexError as e:
        logger.error(str(e))
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(str(e))
        raise typer.Exit(1)


@app.command()
def delete(
    commit: Optional[str] = typer.Option(
        None,
        "--commit",
        "-c",
        help="Commit hash "
        "/ ref. If omitted with --all, deletes across the chosen scope.",
    ),
    index: Optional[int] = typer.Option(
        None,
        "--index",
        "-i",
        help="Memo index " "(0-based). Required for file deletes unless --all.",
    ),
    file_memo: bool = typer.Option(
        False, "--file", "-f", help="Operate on file memos instead of commit memos"
    ),
    delete_all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Delete all private memos. "
        "With --commit: only "
        "for that commit. Without --commit: across the selected scope.",
    ),
):
    """
    Delete memo(s).

    - Default: commit-level
    delete (commit_memos). If no --index, deletes the most recent memo.
    - With --file: operate
    on file memos (then --index is required unless --all).
    - With --all: delete
    ONLY private memos; shared memos are kept.
      * With --commit: limit to that commit.
      * Without --commit: operate across the entire scope.
    """
    resolved_commit: Optional[str] = None
    if commit:
        try:
            resolved_commit = git_service.resolve_commit(commit)
        except Exception as e:
            logger.error(f"Unable to resolve commit: {e}")
            raise typer.Exit(1)

    try:
        if delete_all:
            removed_count = memo_service.delete_all(
                resolved_commit, is_file_memo=file_memo
            )
            scope = "file memos" if file_memo else "commit memos"
            where = (
                f"for {resolved_commit[:7]}"
                if resolved_commit
                else "across all commits"
            )
            logger.info(f"✅ Deleted {removed_count} {scope} {where} (kept shared)")
            return

        if file_memo:
            if resolved_commit is None:
                logger.error(
                    "Provide --commit for file deletes (or use --all for global)."
                )
                raise typer.Exit(1)
            if index is None:
                logger.error(
                    "For file memo deletes, --index is required (or use --all)."
                )
                raise typer.Exit(1)
            deleted_memo = memo_service.delete_memo(
                resolved_commit, index, is_file_memo=True
            )
            logger.info(
                f"✅ Deleted "
                f"file memo at "
                f"{deleted_memo.file or 'unknown'}:"
                f"{str(deleted_memo.line or '?')} @ {resolved_commit[:7]}"
            )
        else:
            if resolved_commit is None:
                logger.error("Provide --commit (or use --all for global delete).")
                raise typer.Exit(1)
            if index is None:
                deleted_memo = memo_service.delete_last(
                    resolved_commit, is_file_memo=False
                )
            else:
                deleted_memo = memo_service.delete_memo(
                    resolved_commit, index, is_file_memo=False
                )
            logger.info(
                f"✅ Deleted commit memo for {resolved_commit[:7]} "
                f"(created {getattr(deleted_memo, 'created', '')})"
            )

    except (IndexError, ValueError) as e:
        logger.error(str(e))
        raise typer.Exit(1)


def _resolve(path_str: str) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = git_service.repo_root() / p
    return p


def _note_paths_for(commit_sha: str) -> List[str]:
    paths: List[str] = []
    try:
        raw = _get_repo().git.notes("--ref=refs/notes/memos", "show", commit_sha)
        obj = json.loads(raw)
        paths = list(obj.get("paths") or [])
    except Exception as e:
        logging.debug("Failed to get note paths for %s: %s", commit_sha, e)
    return paths


@app.command()
def search(
    author: str = typer.Option(None, "--author", "-auth", help="Author name"),
    commit: str = typer.Option(None, "--commit", "-c", help="Commit hash or reference"),
    file: str = typer.Option(None, "--file", "-f", help="File path"),
    visibility: str = typer.Option(
        None, "--visibility", "-vs", help="Memo visibility (private/shared)"
    ),
    limit: int = typer.Option(
        10, "--max", "-n", help="Maximum number of results to show"
    ),
    page: int = typer.Option(1, "--page", help="Page number to display"),
    page_size: int = typer.Option(
        5, "--page-size", "-p", help="Number of memos per page"
    ),
):
    """
    Search only shows memos you can read:
    - private memos
    - shared memos that decrypt with your current identity (AGE_KEY_FILE)
    Locked shared memos are hidden from results.
    """
    if not any([author, commit, file, visibility]):
        logger.error("At least one search filter must be provided")
        raise typer.Exit(1)

    filters: List[str] = []
    if author:
        filters.append(f"author='{author}'")
    if commit:
        filters.append(f"commit='{commit}'")
    if file:
        filters.append(f"file='{file}'")
    if visibility:
        filters.append(f"visibility='{visibility}'")
    logger.info("Searching with filters: %s", " AND ".join(filters))

    def _decrypt_shared_for_commit(
        m, commit_sha: str
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Try a stored path first;
        if missing/fails, try every path in the commit's note."""
        shared = getattr(m, "shared", None)
        tried: List[str] = []
        if shared and getattr(shared, "path", None):
            path_str = shared.path
            tried.append(path_str)
            p = _resolve(path_str)
            if p.exists():
                try:
                    result_obj = json.loads(decrypt(p.read_bytes()).decode("utf-8"))
                    return True, result_obj
                except Exception as e:
                    logging.debug(
                        "Failed to decrypt shared file at %s: %s", path_str, e
                    )

        for path_str in _note_paths_for(commit_sha):
            if path_str in tried:
                continue
            p = _resolve(path_str)
            if not p.exists():
                continue
            try:
                result_obj = json.loads(decrypt(p.read_bytes()).decode("utf-8"))
                return True, result_obj
            except Exception as e:
                logging.debug(
                    "Failed to decrypt file at %s for commit %s: %s",
                    path_str,
                    commit_sha,
                    e,
                )
                continue

        return False, None

    with console.status("[bold green]Searching for memos...[/bold green]"):
        if commit:
            resolved_commit = git_service.resolve_commit(commit)
            cm_memos, file_memos = memo_service.get_commit_memos(resolved_commit)
            candidates = cm_memos + file_memos
        else:
            candidates = memo_service.get_all_memos()

        if author:
            a = author.strip().lower()
            candidates = [
                m
                for m in candidates
                if getattr(m, "author", None) and a in m.author.lower()
            ]

        if file:
            file_norm = file.replace("\\", "/")
            candidates = [
                m
                for m in candidates
                if m.file and file_norm in m.file.replace("\\", "/")
            ]

        if visibility:
            candidates = [m for m in candidates if m.visibility == visibility]
        visible: List[Tuple[Any, Optional[Dict[str, Any]]]] = []
        hidden_locked = 0
        for m in candidates:
            if getattr(m, "visibility", "private") != "shared":
                visible.append((m, None))
                continue

            if m.commit is None:
                ok, obj = _decrypt_shared_for_commit(m, "")
            else:
                ok, obj = _decrypt_shared_for_commit(m, cast(str, m.commit))

            if ok and obj is not None:
                visible.append((m, obj))
            else:
                hidden_locked += 1

    if not visible:
        if hidden_locked:
            console.print(
                "[dim]No readable memos matched the filters "
                f"(hidden locked: {hidden_locked}).[/dim]"
            )
        else:
            logger.info("No memos found matching the criteria.")
        return

    visible.sort(key=lambda pair: pair[0].created)
    if limit:
        visible = visible[-limit:]

    total = len(visible)
    total_pages = calculate_total_pages(total, page_size)
    page = min(max(1, page), total_pages)
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total)

    hdr_hidden = f" (hidden locked: {hidden_locked})" if hidden_locked else ""
    console.print(
        f"[bold]Found "
        f"{total} readable memos. Showing page {page}/{total_pages}{hdr_hidden}[/bold]"
    )

    for i, (m, obj) in enumerate(visible[start_idx:end_idx], start=start_idx + 1):
        console.print(f"[bold]Result {i}/{total}:[/bold]")
        if obj is None:
            console.print(format_memo_panel(m, include_file=bool(m.file)))
        else:
            base_title = (
                getattr(getattr(m, "shared", None), "title", None) or "shared memo"
            )
            title_val = obj.get("title") or base_title
            body_val = obj.get("body") or m.memo
            author_val = obj.get("author") or m.author
            created_val = obj.get("created") or (
                m.created.strftime("%Y-%m-%d %H:%M:%S")
                if getattr(m, "created", None)
                else ""
            )
            border = "yellow" if getattr(m, "file", None) else "green"
            format_shared_panel(
                title=f"🔓 [shared] {title_val}",
                body=body_val,
                author=author_val,
                created=created_val,
                border_style=border,
            )

    if total_pages > 1:
        nxt = page + 1
        prv = page - 1
        console.print(
            f"[italic]Use --page {nxt} to see the next page[/italic]"
            if page < total_pages
            else f"[italic]Use --page {prv} to see the previous page[/italic]"
        )


def _print_one(memo, title: str, border_color: str):
    """
    Prints one memo. Decrypts shared memos (path first, then note paths).
    """
    include_file = bool(getattr(memo, "file", None))

    if getattr(memo, "visibility", "private") != "shared":
        console.print(
            format_memo_panel(
                memo, title=title, border_style=border_color, include_file=include_file
            )
        )
        return

    commit_sha = getattr(memo, "commit", None)

    def _note_paths_for(csha: str) -> list[str]:
        paths: list[str] = []
        try:
            for raw in git_service.list_notes(csha):
                try:
                    result_obj = json.loads(raw)
                    paths.extend(list(result_obj.get("paths") or []))
                except Exception as ex:
                    logging.debug(
                        "Failed to parse note JSON for commit %s: %s", csha, ex
                    )
                    continue
        except Exception as exs:
            logging.debug("Failed to list notes for commit %s: %s", csha, exs)
            pass
        return paths

    obj = None
    path_hint = None
    shared = getattr(memo, "shared", None)

    if shared and getattr(shared, "path", None):
        path_hint = shared.path
        p = _resolve(shared.path)
        if p.exists():
            try:
                obj = json.loads(decrypt(p.read_bytes()).decode("utf-8"))
            except Exception as e:
                logging.debug("Failed to decrypt shared file at %s: %s", shared.path, e)
                obj = None

    if obj is None and commit_sha:
        for candidate in _note_paths_for(commit_sha):
            p = _resolve(candidate)
            if not p.exists():
                continue
            try:
                obj = json.loads(decrypt(p.read_bytes()).decode("utf-8"))
                path_hint = candidate
                break
            except Exception as e:
                logging.debug(
                    "Failed to decrypt file at %s for commit %s: %s",
                    candidate,
                    commit_sha,
                    e,
                )
                continue

    if obj:
        title_val = obj.get("title") or (
            shared.title if shared and getattr(shared, "title", None) else "shared memo"
        )
        body = obj.get("body") or memo.memo
        author = obj.get("author") or memo.author
        created = obj.get("created") or memo.created.strftime("%Y-%m-%d %H:%M:%S")
        console.print(
            shared_to_panel(
                title=title_val,
                body=body,
                author=author,
                created=created,
                border_style=("yellow" if include_file else "green"),
            )
        )
    else:
        console.print(
            locked_shared_panel(title=title, path=path_hint, border_style=border_color)
        )


@app.command()
def show(
    commit: str = typer.Argument(..., help="commit hash / ref"),
    kind: str = typer.Option(
        "all",
        "--kind",
        "-k",
        help="what to show: commit | file | all",
        case_sensitive=False,
    ),
):
    """
    Show memos for a given commit.

    By default, shows BOTH commit memos and file/line memos (kind=all).
    Use --kind commit or --kind file to filter.
    """
    kind = (kind or "all").lower().strip()
    if kind not in {"all", "commit", "file"}:
        raise typer.BadParameter("--kind must be one of: all, commit, file")

    storex = memo_store.JsonStore()
    service = MemoService(storex)

    resolved_commit = git_service.resolve_commit(commit)
    commit_memos, file_memos = service.get_commit_memos(resolved_commit)

    shown_any = False

    def _emit_header(label: str):
        console.rule(f"" f"[bold cyan]{label}")

    if kind in {"all", "commit"}:
        if commit_memos:
            _emit_header("Commit memos")
            for idx, memo in enumerate(commit_memos, start=1):
                title = f"{resolved_commit[:7]} • {idx}/{len(commit_memos)}"
                _print_one(memo, title, "green")
            shown_any = True
        elif kind == "commit":
            rich.print("[yellow]No commit memos[/]")

    if kind in {"all", "file"}:
        if file_memos:
            _emit_header("File/line memos")
            for idx, memo in enumerate(file_memos, start=1):
                title = (
                    f"{memo.file}:"
                    f"{memo.line}  •  {resolved_commit[:7]} • {idx}/{len(file_memos)}"
                )
                _print_one(memo, title, "yellow")
            shown_any = True
        elif kind == "file":
            rich.print("[yellow]No file memos[/]")

    if not shown_any and kind == "all":
        rich.print("[yellow]No memos on this commit[/]")


@app.command()
def log(
    limit: int = typer.Option(None, "--max", "-n", help="show N latest commits"),
    page_size: int = typer.Option(
        10, "--page-size", "-p", help="number of commits per page"
    ),
    page: int = typer.Option(1, "--page", help="page number to display"),
    debug: bool = typer.Option(False, "--debug", help="print decrypt diagnostics"),
    mode: str = typer.Option(
        "overview", "--mode", "-m", help="overview or detailed", case_sensitive=False
    ),
    compact: bool = typer.Option(
        False, "--compact", "-c", help="compact one-line memos (detailed mode)"
    ),
    branch: Optional[str] = typer.Option(
        None,
        "--branch",
        "-b",
        help="branch/ref/revspec to log "
        "(e.g. main, feature/x, HEAD~50..HEAD). "
        "Defaults to current HEAD.",
    ),
):
    """
    A stable, clear log view.

    Modes:
      - overview (default): one aligned
      table of commits (P/S/L counts)
      - detailed: header per commit
       and that commit's memos underneath
    """
    mode = (mode or "overview").lower().strip()
    if mode not in {"overview", "detailed"}:
        raise typer.BadParameter("--mode must be 'overview' or 'detailed'")

    console.rule("[bold bright_magenta]Commit Memory Log")

    target = branch or "HEAD"
    try:
        git_service.ensure_rev_exists(target)
    except Exception as e:
        logger.error(str(e))
        raise typer.Exit(1)

    all_commits = list(git_service.iter_commits(rev=target, max_count=limit))
    total_commits = len(all_commits)
    if total_commits == 0:
        logger.info("No commits found.")
        return

    total_pages = calculate_total_pages(total_commits, page_size)
    page = min(max(1, page), total_pages)
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_commits)

    console.print(
        f"[bold]Branch/ref:[/bold] {target} • "
        f"[bold]Showing page "
        f"{page}/{total_pages} ({total_commits} commits total)[/bold]"
    )
    console.print(
        "[dim]Legend: P=private(commit+file)  "
        "S=shared(decrypted)  L=locked(shared)  • times in UTC[/dim]"
    )

    def _decrypt_shared(
        memo, commit_sha: str
    ) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Return (ok, obj, path_str_if_known)."""
        if getattr(memo, "visibility", "private") != "shared":
            return False, None, None

        shared = getattr(memo, "shared", None)
        tried: list[str] = []

        if shared and getattr(shared, "path", None):
            p = _resolve(shared.path)
            tried.append(shared.path)
            if p.exists():
                try:
                    res_obj = json.loads(decrypt(p.read_bytes()).decode("utf-8"))
                    return True, res_obj, shared.path
                except Exception as ex:
                    logging.debug("Failed to decrypt shared file at %s: %s", p, ex)
                    if debug:
                        console.print(f"[dim]decrypt failed: {p}[/dim]")

        for candidate in _note_paths_for(commit_sha):
            if candidate in tried:
                continue
            p = _resolve(candidate)
            if not p.exists():
                continue
            try:
                res_obj = json.loads(decrypt(p.read_bytes()).decode("utf-8"))
                return True, res_obj, candidate
            except Exception as es:
                logging.debug(
                    "Failed to decrypt note file at %s for commit %s: %s",
                    p,
                    commit_sha,
                    es,
                )
                if debug:
                    console.print(f"[dim]decrypt failed note: {p}[/dim]")

        titled = getattr(getattr(memo, "shared", None), "title", None) or "shared memo"
        path_hint = getattr(getattr(memo, "shared", None), "path", None)
        return False, {"title": titled}, path_hint

    def _extract_shared_memo_data(memos, result_obj):
        """Extract standardized data from a shared memo object."""
        result_title = (
            result_obj.get("title")
            or (getattr(memos, "shared", None) and getattr(memos.shared, "title", None))
            or "shared memo"
        )
        result_body = obj.get("body") or memos.memo
        result_author = obj.get("author") or memos.author
        result_created = obj.get("created") or memos.created.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        return result_title, result_body, result_author, result_created

    result_store = (
        memo_store.get_store()
        if hasattr(memo_store, "get_store")
        else memo_store.JsonStore()
    )
    result_memo_service = MemoService(result_store)

    if mode == "overview":
        table = make_overview_table()

        total_previous = total_shared = total_locked = 0
        for i, commit in enumerate(all_commits[start_idx:end_idx], start=start_idx + 1):
            commit_memos, file_memos = result_memo_service.get_commit_memos(
                commit.hexsha
            )

            previous = 0
            shared_ok = 0
            locked = 0

            for memo in [*commit_memos, *file_memos]:
                if getattr(memo, "visibility", "private") != "shared":
                    previous += 1
                else:
                    ok, obj, _ = _decrypt_shared(memo, commit.hexsha)
                    if ok and obj:
                        shared_ok += 1
                    else:
                        locked += 1

            add_overview_row(table, i, commit, previous, shared_ok, locked)
            total_previous += previous
            total_shared += shared_ok
            total_locked += locked

        console.print(table)
        console.print(
            f"[dim]visible: "
            f"private={total_previous}, "
            f"shared(decrypted)={total_shared}; "
            f"hidden locked={total_locked}[/dim]"
        )
        if total_pages > 1:
            console.print(
                f"[italic]Use --page " f"{page + 1} to see the next page[/italic]"
                if page < total_pages
                else f"[italic]Use --page "
                f"{page - 1} to see the "
                f"previous page[/italic]"
            )
        console.print(
            "[dim]Tip: use --mode detailed "
            "to expand memos, and --compact for one-liners.[/dim]"
        )
        return

    total_previous = total_shared = total_locked = 0

    for i, commit in enumerate(all_commits[start_idx:end_idx], start=start_idx + 1):
        commit_memos, file_memos = result_memo_service.get_commit_memos(commit.hexsha)

        previous_commit: list = []
        previous_file: list = []
        shared_panels: list[tuple[str, str, str, str, str]] = []
        locked = 0

        for memo in commit_memos:
            if getattr(memo, "visibility", "private") != "shared":
                previous_commit.append(memo)
            else:
                ok, obj, _ = _decrypt_shared(memo, commit.hexsha)
                if ok and obj:
                    title, body, author, created = _extract_shared_memo_data(memo, obj)
                    shared_panels.append((title, body, author, created, "green"))
                else:
                    locked += 1

        for memo in file_memos:
            if getattr(memo, "visibility", "private") != "shared":
                previous_file.append(memo)
            else:
                ok, obj, _ = _decrypt_shared(memo, commit.hexsha)
                if ok and obj:
                    title, body, author, created = _extract_shared_memo_data(memo, obj)
                    shared_panels.append((title, body, author, created, "yellow"))
                else:
                    locked += 1

        previous_count = len(previous_commit) + len(previous_file)
        shared_count = len(shared_panels)

        console.print(
            commit_header_row(i, commit, previous_count, shared_count, locked)
        )

        for memo in previous_commit:
            if compact:
                console.print(format_memo_line(memo, include_file=False))
            else:
                console.print(format_memo_panel(memo, include_file=False))

        for memo in previous_file:
            if compact:
                console.print(format_memo_line(memo, include_file=True))
            else:
                console.print(
                    format_memo_panel(memo, include_file=True, border_style="yellow")
                )

        for title, body, author, created, color in shared_panels:
            console.print(
                shared_to_panel(
                    title=title,
                    body=body,
                    author=author,
                    created=created,
                    border_style=color,
                )
            )

        total_previous += previous_count
        total_shared += shared_count
        total_locked += locked
        console.print()

    console.print(
        f"[dim]visible: private={total_previous}, "
        f"shared(decrypted)={total_shared}; hidden locked={total_locked}[/dim]"
    )
    if total_pages > 1:
        console.print(
            f"[italic]Use --page {page + 1} to see the next page[/italic]"
            if page < total_pages
            else f"[italic]Use --page {page - 1} to see the previous page[/italic]"
        )


def _split_members(members: List[str] | None) -> List[str]:
    out: List[str] = []
    for item in members or []:
        out.extend([p.strip() for p in item.split(",") if p.strip()])
    seen = set()
    uniq = []
    for a in out:
        if a not in seen:
            uniq.append(a)
            seen.add(a)
    return uniq


@group_app.command("create")
def group_create(
    name: str,
    members: List[str] = typer.Option(None, "--members", "-m"),
    force: bool = typer.Option(
        False, "--force", help="Create even if group exists; merges members"
    ),
):
    g = Groups.load()
    to_add = _split_members(members)

    if to_add:
        missing = aliases_missing_in_trust(to_add)
        if missing:
            logger.error(
                "Unknown alias(es) (not in trust.yml): %s. "
                "Add them first with `cm trust add <alias> --age <recipient>`",
                ", ".join(missing),
            )
            raise typer.Exit(2)

    if g.exists(name) and not force:
        logger.error(
            f"Group '{name}' "
            f"already exists. Use "
            f"`cm group add {name} --members ...` or pass --force to merge."
        )
        raise typer.Exit(1)

    if not g.exists(name):
        g.set_members(name, to_add)
    else:
        g.add_members(name, to_add)

    g.save()
    rich.print(
        f"[green]✔ Group[/] {name}: {', '.join(g.groups.get(name, [])) or '(empty)'}"
    )


@group_app.command("add")
def group_add(name: str, members: List[str] = typer.Option(..., "--members", "-m")):
    g = Groups.load()
    if not g.exists(name):
        logger.error(f"Unknown group: {name}. Create it with `cm group create {name}`.")
        raise typer.Exit(1)

    to_add = _split_members(members)
    if not to_add:
        raise typer.BadParameter("Provide at least one member via --members")

    missing = aliases_missing_in_trust(to_add)
    if missing:
        logger.error(
            "Unknown alias(es) (not in trust.yml): %s. "
            "Add them first with `cm trust add <alias> --age <recipient>`",
            ", ".join(missing),
        )
        raise typer.Exit(2)

    g.add_members(name, to_add)
    g.save()
    rich.print(f"[green]✔ Updated group[/] {name}: {', '.join(g.groups[name])}")


@group_app.command("rm")
def group_rm(name: str, members: List[str] = typer.Option(..., "--members", "-m")):
    g = Groups.load()
    if not g.exists(name):
        logger.error(f"Unknown group: {name}.")
        raise typer.Exit(1)
    to_rm = _split_members(members)
    if not to_rm:
        raise typer.BadParameter("Provide at least one member via --members")
    g.remove_members(name, to_rm)
    g.save()
    rich.print(
        f"[green]✔ "
        f"Updated group[/] {name}: {', '.join(g.groups.get(name, [])) or '(empty)'}"
    )


@group_app.command("validate")
def group_validate():
    g = Groups.load()
    any_bad = False
    for name, members in sorted(g.groups.items()):
        missing = aliases_missing_in_trust(members)
        if missing:
            any_bad = True
            rich.print(f"[red]✖ {name}[/]: unknown in trust.yml → {', '.join(missing)}")
        else:
            rich.print(f"[green]✔ {name}[/]: ok")
    if any_bad:
        raise typer.Exit(2)


@group_app.command("list")
def group_list():
    """List all groups and their members."""
    g = Groups.load()
    if not g.groups:
        rich.print(
            "[dim]No groups defined. "
            "Use `cm group create <name> --members alice,bob`[/dim]"
        )
        return
    for name, members in sorted(g.groups.items()):
        rich.print(f"[bold]{name}[/]: {', '.join(members) if members else '(empty)'}")


@group_app.command("show")
def group_show(name: str):
    """Show one group's members."""
    g = Groups.load()
    members = g.groups.get(name)
    if members is None:
        logger.error(f"Unknown group: {name}")
        raise typer.Exit(1)
    rich.print(f"[bold]{name}[/]: {', '.join(members) if members else '(empty)'}")


def _set_log_level(verbosity: int):
    level = logging.WARNING - min(verbosity, 2) * 10
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def calculate_total_pages(total_items: int, page_size: int) -> int:
    return (total_items + page_size - 1) // page_size


@app.command("trust")
def trust_add(name: str = typer.Argument(...), age: str = typer.Option(None, "--age")):
    """Add/update a collaborator's public key."""
    t = Trust.load()
    if age is None:
        raise typer.BadParameter("Provide --age <age-recipient-string>")
    t.users[name] = age
    t.save()
    rich.print(f"Added {name}")


@app.command("pull")
def pull():
    """
    Fetch memo notes and index them into the local store so show/log look up to date.
    """
    memo_service.pull()
    logger.info("✅ Pulled memo pointers and updated local index.")


@app.callback()
def common(
    verbosity: int = typer.Option(0, "--verbose", "-v", count=True),
    quiet: bool = typer.Option(False, "--quiet", "-q"),
):
    if quiet:
        _set_log_level(-1)
    else:
        _set_log_level(verbosity)


@app.command("version")
def version_cmd():
    """Show version."""
    try:
        v = _pkg_version("commit-memory")
    except PackageNotFoundError:
        from . import __version__ as v
    typer.echo(v)


def main() -> None:
    """Console entry point for `cm`."""
    app()


def _print_version_and_exit(value: bool):
    if not value:
        return
    try:
        v = _pkg_version("commit-memory")
    except PackageNotFoundError:
        from . import __version__ as v
    typer.echo(v)
    raise typer.Exit()


if __name__ == "__main__":
    main()
