from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable


class AgeNotInstalled(RuntimeError):
    ...


def _ensure_age() -> str:
    from shutil import which

    age = which("age")
    if not age:
        raise AgeNotInstalled(
            "age not found in PATH. Install https://age-encryption.org/"
        )
    return age


def encrypt_for(recipients: Iterable[str], plaintext: bytes) -> bytes:
    age = _ensure_age()
    with tempfile.NamedTemporaryFile(
        "w", delete=False
    ) as rfile, tempfile.NamedTemporaryFile(
        "wb", delete=False
    ) as pfile, tempfile.NamedTemporaryFile(
        "rb", delete=False
    ) as cfile:
        for r in recipients:
            rfile.write(r.strip() + "\n")
        rfile.flush()
        pfile.write(plaintext)
        pfile.flush()
        subprocess.run(
            [age, "-R", rfile.name, "-o", cfile.name, pfile.name],
            check=True,
            capture_output=True,
        )
        cfile.seek(0)
        return cfile.read()


def decrypt(ciphertext: bytes, identity: str | None = None) -> bytes:
    age = _ensure_age()
    key = identity or os.getenv("AGE_KEY_FILE")
    if not key:
        default = Path.home() / ".config" / "age" / "key.txt"
        if default.exists():
            key = str(default)

    if os.getenv("CM_DEBUG") == "1":
        print(f"[decrypt] using identity: {key or '(none)'}", file=sys.stderr)

    with tempfile.NamedTemporaryFile("wb", delete=False) as cfile:
        cfile.write(ciphertext)
        cfile.flush()
        cmd = [age, "-d"]
        if key:
            cmd += ["-i", key]
        cmd += [cfile.name]
        try:
            proc = subprocess.run(cmd, check=True, capture_output=True)
            return proc.stdout
        except subprocess.CalledProcessError as e:
            if os.getenv("CM_DEBUG") == "1":
                sys.stderr.write(
                    f"[decrypt] age stderr: {e.stderr.decode(errors='ignore')}\n"
                )
            raise


def sha256(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()
