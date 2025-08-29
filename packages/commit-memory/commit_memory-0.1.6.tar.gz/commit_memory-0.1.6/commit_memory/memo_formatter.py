"""
Formatting utilities for Commit Memory.

Stable, aligned terminal output with Rich:
- Overview table for commits (compact summary).
- Per-commit header row (same columns as the overview).
- Memo renderers: panel (default) and compact one-liner.

Legend:
  P = private S = shared (decrypted) L = shared but locked (not decrypted)
"""

from __future__ import annotations

import logging
from datetime import timezone
from typing import Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from commit_memory import models


def make_overview_table() -> Table:
    """A single table used to list all commits on a page."""
    t = Table(
        show_header=True,
        header_style="bold cyan",
        box=box.SIMPLE_HEAVY,
        expand=True,
        padding=(0, 1),
    )
    t.add_column("#", justify="right", width=3, no_wrap=True, style="bright_black")
    t.add_column("Commit", width=8, no_wrap=True, style="bold cyan")
    t.add_column("Message", overflow="ellipsis", max_width=64, style="bold white")
    t.add_column("Author", overflow="ellipsis", max_width=18, style="white")
    t.add_column("UTC Time", no_wrap=True, style="white")
    t.add_column("P", justify="right", width=3, style="green")
    t.add_column("S", justify="right", width=3, style="cyan")
    t.add_column("L", justify="right", width=3, style="yellow")
    return t


def add_overview_row(
    table: Table,
    index: int,
    commit,
    priv_count: int,
    shared_count: int,
    locked_count: int,
) -> None:
    author_name = _safe_author(commit)
    dt = _safe_utc(commit)
    table.add_row(
        str(index),
        commit.hexsha[:7],
        (getattr(commit, "summary", None) or "(no subject)"),
        author_name,
        dt,
        str(priv_count),
        str(shared_count),
        str(locked_count),
    )


def commit_header_row(
    index: int,
    commit,
    priv_count: int,
    shared_count: int,
    locked_count: int,
) -> Table:
    """
    One-row table (same columns as overview) to precede the memos of that commit.
    Keeps column alignment stable while showing details underneath.
    """
    t = make_overview_table()
    t.show_header = False
    add_overview_row(t, index, commit, priv_count, shared_count, locked_count)
    return t


def format_memo_panel(
    memo: models.Memo,
    title: Optional[str] = None,
    border_style: str = "green",
    include_file: bool = False,
) -> Panel:
    """
    Private/file memo as a tidy panel.

    Backward-compatible signature, so older call sites like
    `format_memo_panel(memo, title, border_color)` continue to work,
    and newer ones can do `format_memo_panel(memo, include_file=True)`.
    """
    tbl = Table.grid(padding=(0, 1))
    tbl.add_column(justify="right", style="bold bright_black", no_wrap=True)
    tbl.add_column()

    if include_file and getattr(memo, "file", None):
        tbl.add_row("File", f"{memo.file}:{memo.line}")
    tbl.add_row("Memo", memo.memo)
    tbl.add_row("Author", memo.author)
    tbl.add_row("Created", memo.created.strftime("%Y-%m-%d %H:%M:%S"))
    tbl.add_row("Visibility", getattr(memo, "visibility", "private"))

    if title is None:
        title = (
            "🔒 private"
            if getattr(memo, "visibility", "private") != "shared"
            else "🔓 shared"
        )

    return Panel(tbl, title=title, box=box.ROUNDED, border_style=border_style)


def format_memo_line(memo: models.Memo, include_file: bool = False) -> Text:
    """Compact one-line memo (good for --compact mode)."""
    t = Text()
    if include_file and getattr(memo, "file", None):
        t.append(f"  ▸ {memo.file}:{memo.line}  ", style="yellow")
    t.append("“")
    t.append(memo.memo)
    t.append("”  ")
    t.append(f"[dim]{memo.author}  {memo.created:%Y-%m-%d %H:%M}[/dim]")
    return t


def shared_to_panel(
    *,
    title: str,
    body: str,
    author: str,
    created: str,
    border_style: str,
) -> Panel:
    grid = Table.grid(padding=(0, 1))
    grid.add_column(justify="right", style="bold bright_black", no_wrap=True)
    grid.add_column()
    grid.add_row("Memo", body)
    grid.add_row("Author", author)
    grid.add_row("Created", created)
    grid.add_row("Visibility", "shared")
    return Panel(grid, title=f"🔓 {title}", border_style=border_style, box=box.ROUNDED)


def locked_shared_panel(
    *, title: str, path: str | None, border_style="yellow"
) -> Panel:
    msg = "Encrypted shared memo is present but locked (cannot decrypt)"
    if path:
        msg += f"\npath: {path}"
    return Panel(msg, title=f"🔒 {title}", border_style=border_style, box=box.ROUNDED)


def format_shared_panel(
    title: str,
    body: str,
    author: str,
    created: str,
    border_style: str = "green",
):
    """Back-compat alias for older code; forwards to shared_to_panel()."""
    return shared_to_panel(
        title=title,
        body=body,
        author=author,
        created=created,
        border_style=border_style,
    )


def format_locked_shared_panel(
    title: str,
    hint: str,
    border_style: str = "yellow",
    path: str = "",
):
    """
    Back-compat alias for older code that passed a 'hint' string.
    Preserves the custom hint and optional path in the panel body.
    """
    msg = hint or "Encrypted shared memo is present but locked (cannot decrypt)"
    if path:
        msg += f"\npath: {path}"
    return Panel(msg, title=title, border_style=border_style, box=box.ROUNDED)


def format_memo_table(memo, include_file: bool = False):
    """Back-compat alias to the new panel renderer for private/file memos."""
    return format_memo_panel(memo, include_file=include_file)


class MemoFormatter:
    def __init__(self, console: Console):
        self.console = console


def _safe_author(commit) -> str:
    try:
        return getattr(commit.author, "name", None) or str(commit.author)
    except Exception as e:
        logging.debug(
            "Failed to get author for commit %s: %s",
            getattr(commit, "hexsha", "unknown"),
            e,
        )
        return "(unknown)"


def _safe_utc(commit) -> str:
    try:
        return commit.committed_datetime.astimezone(timezone.utc).strftime(
            "%Y-%m-%d %H:%MZ"
        )
    except Exception as e:
        logging.debug(
            "Failed to get UTC datetime for commit %s: %s",
            getattr(commit, "hexsha", "unknown"),
            e,
        )
        return ""
