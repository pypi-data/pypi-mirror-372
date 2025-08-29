# commit_memory/trust.py

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, cast

TRUST_FILE = Path(".commit-memos/trust.yml")
GROUPS_FILE = Path(".commit-memos/groups.yml")

yaml: Any
try:
    import yaml as _yaml

    yaml = _yaml
except ModuleNotFoundError:
    yaml = cast(Any, None)


def _require_yaml() -> None:
    if yaml is None:
        raise RuntimeError("PyYAML is required. Install with: pip install PyYAML")


def _uniq_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


@dataclass
class Trust:
    users: Dict[str, str]

    @classmethod
    def load(cls) -> "Trust":
        _require_yaml()
        if not TRUST_FILE.exists():
            TRUST_FILE.parent.mkdir(parents=True, exist_ok=True)
            TRUST_FILE.write_text("users: {}\n")
        data = yaml.safe_load(TRUST_FILE.read_text()) or {"users": {}}
        return cls(users={k: str(v) for k, v in (data.get("users") or {}).items()})

    def save(self) -> None:
        _require_yaml()
        TRUST_FILE.parent.mkdir(parents=True, exist_ok=True)
        TRUST_FILE.write_text(yaml.safe_dump({"users": self.users}, sort_keys=True))


@dataclass
class Groups:
    groups: Dict[str, List[str]] = field(default_factory=dict)

    @classmethod
    def load(cls) -> "Groups":
        _require_yaml()
        if not GROUPS_FILE.exists():
            GROUPS_FILE.parent.mkdir(parents=True, exist_ok=True)
            GROUPS_FILE.write_text("groups: {}\n")
        data = yaml.safe_load(GROUPS_FILE.read_text()) or {"groups": {}}
        out = {
            g: [str(a) for a in (alist or [])]
            for g, alist in (data.get("groups") or {}).items()
        }
        return cls(groups=out)

    def save(self) -> None:
        _require_yaml()
        GROUPS_FILE.parent.mkdir(parents=True, exist_ok=True)
        GROUPS_FILE.write_text(yaml.safe_dump({"groups": self.groups}, sort_keys=True))

    def exists(self, name: str) -> bool:
        return name in self.groups

    def ensure_group(self, name: str) -> None:
        self.groups.setdefault(name, [])

    def set_members(self, name: str, aliases: List[str]) -> None:
        self.groups[name] = _uniq_keep_order(aliases)

    def add_members(self, name: str, aliases: List[str]) -> None:
        self.ensure_group(name)
        cur = _uniq_keep_order(self.groups[name] + aliases)
        self.groups[name] = cur

    def remove_members(self, name: str, aliases: List[str]) -> None:
        if name not in self.groups:
            return
        rm = set(aliases)
        self.groups[name] = [a for a in self.groups[name] if a not in rm]


def aliases_missing_in_trust(aliases: List[str]) -> List[str]:
    """Return aliases that are not present in trust.yml."""
    t = Trust.load()
    return [a for a in _uniq_keep_order(aliases) if a not in t.users]


def expand_recipients(
    user_aliases: List[str] | None, group_names: List[str] | None
) -> List[str]:
    """
    Expand explicit aliases and group names into a unique alias list.
    Validates that all resulting aliases exist in Trust.users.
    """
    t = Trust.load()
    g = Groups.load()

    wanted: List[str] = []
    if user_aliases:
        for item in user_aliases:
            wanted.extend([p.strip() for p in item.split(",") if p.strip()])
    if group_names:
        for grp in group_names:
            grp = grp.strip()
            if not grp:
                continue
            if grp not in g.groups:
                raise ValueError(
                    f"Unknown group: "
                    f"{grp}. Define it with `cm group create {grp} --members ...`"
                )
            wanted.extend(g.groups[grp])

    uniq = _uniq_keep_order(wanted)
    missing = [a for a in uniq if a not in t.users]
    if missing:
        raise ValueError(
            "Unknown alias(es) in trust.yml: "
            + ", ".join(missing)
            + ". Add with `cm trust add <alias> --age <age-recipient>`"
        )
    return uniq
