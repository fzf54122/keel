# -*- coding: utf-8 -*-
"""Resolve template / project roots for the Keel CLI."""

from __future__ import annotations

import os
from pathlib import Path

# Published template (used when the local checkout is not available).
DEFAULT_TEMPLATE = "gh:fzf54122/keel"


def package_root() -> Path:
    """Directory that contains the `keel` package."""
    return Path(__file__).resolve().parent


def discover_template_root() -> Path | None:
    """Return a local checkout root that looks like a Keel template, if any."""
    env = os.environ.get("KEEL_TEMPLATE")
    if env:
        path = Path(env).expanduser().resolve()
        if _looks_like_template(path):
            return path
        raise SystemExit(f"KEEL_TEMPLATE is not a Keel template: {path}")

    # editable install / repo checkout: keel/ sits next to application/
    candidate = package_root().parent
    if _looks_like_template(candidate):
        return candidate
    return None


def resolve_template_src() -> str:
    """Copier src_path: local path string or remote git shorthand."""
    local = discover_template_root()
    if local is not None:
        return str(local)
    return os.environ.get("KEEL_TEMPLATE_URL", DEFAULT_TEMPLATE)


def _looks_like_template(path: Path) -> bool:
    return (
        path.is_dir()
        and (path / "copier.yml").is_file()
        and (path / "application").is_dir()
        and (path / "common").is_dir()
        and (path / "conf").is_dir()
    )


def find_project_root(start: Path | None = None) -> Path:
    """Walk up from *start* (default cwd) until we find a Keel project root."""
    cur = (start or Path.cwd()).resolve()
    for path in (cur, *cur.parents):
        if (path / "application" / "modules").is_dir() and (path / "conf").is_dir():
            return path
    raise SystemExit(
        "not a Keel project (missing application/modules and conf/). "
        "Run from the project root or pass --path."
    )
