#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Post-generate rebrand for Copier-created Keel projects.

Prefer CLI args (passed from copier.yml _tasks). Fall back to
``.copier-answers.yml`` when present.
"""

from __future__ import annotations

import argparse
import re
import secrets
import shutil
import sys
from pathlib import Path

ROOT = Path.cwd()


def _slug(project_name: str) -> str:
    return project_name.replace("-", "_")


def _load_answers_file() -> dict:
    try:
        import yaml
    except ImportError:
        return {}
    for name in (".copier-answers.yml", ".copier-answers.yaml"):
        path = ROOT / name
        if path.is_file():
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            return {k: v for k, v in data.items() if not str(k).startswith("_")}
    return {}


def _parse_args(argv: list[str]) -> dict:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--project-name")
    parser.add_argument("--app-title")
    parser.add_argument("--table-prefix")
    parser.add_argument("--author-name", default="developer")
    parser.add_argument("--author-email", default="dev@example.com")
    parser.add_argument("--include-demo", default="true")
    parser.add_argument("--include-celery", default="true")
    parser.add_argument("--use-postgres", default="true")
    ns, _ = parser.parse_known_args(argv)

    if ns.project_name:
        return {
            "project_name": ns.project_name,
            "app_title": ns.app_title or ns.project_name,
            "table_prefix": ns.table_prefix
            or f"{_slug(ns.project_name)}_",
            "author_name": ns.author_name,
            "author_email": ns.author_email,
            "include_demo": str(ns.include_demo).lower() in {"1", "true", "yes"},
            "include_celery": str(ns.include_celery).lower() in {"1", "true", "yes"},
            "use_postgres": str(ns.use_postgres).lower() in {"1", "true", "yes"},
        }
    return _load_answers_file()


def _set_pyproject(project: str, author: str, email: str, title: str) -> None:
    path = ROOT / "pyproject.toml"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'(?m)^name = "keel"$', f'name = "{project}"', text, count=1)
    text = re.sub(
        r'(?m)^description = ".*"$',
        f'description = "{title} — FastAPI app from Keel scaffold"',
        text,
        count=1,
    )
    text = re.sub(
        r'\{name = "fzf", email = "fzf54122@163\.com"\}',
        f'{{name = "{author}", email = "{email}"}}',
        text,
        count=1,
    )
    text = re.sub(
        r'(?ms)^\[project\.urls\]\nHomepage = ".*?"\nRepository = ".*?"\n',
        "",
        text,
        count=1,
    )
    path.write_text(text, encoding="utf-8")


def _write_env(
    *,
    project: str,
    title: str,
    table_prefix: str,
    use_postgres: bool,
    include_demo: bool,
) -> None:
    example = ROOT / ".env.example"
    if not example.is_file():
        return

    secret = secrets.token_urlsafe(32)
    swagger_pw = secrets.token_urlsafe(12)
    admin_pw = secrets.token_urlsafe(12)
    base = example.read_text(encoding="utf-8")

    def rebrand(text: str, *, secrets_ok: bool) -> str:
        text = text.replace("APP_TITLE=Keel", f"APP_TITLE={title}")
        text = text.replace("PROJECT_NAME=keel", f"PROJECT_NAME={project}")
        text = text.replace(
            "APP_DESCRIPTION=FastAPI scaffold with SQLAlchemy and RBAC",
            f"APP_DESCRIPTION={title} API",
        )
        text = text.replace("TABLE_PREFIX=keel_", f"TABLE_PREFIX={table_prefix}")
        text = text.replace(
            "ENABLE_DEMO=true",
            f"ENABLE_DEMO={'true' if include_demo else 'false'}",
        )
        if secrets_ok:
            text = text.replace(
                "SECRET_KEY=change-me-to-a-random-string-at-least-32-chars",
                f"SECRET_KEY={secret}",
            )
            text = text.replace(
                "SWAGGER_UI_PASSWORD=change-me-swagger",
                f"SWAGGER_UI_PASSWORD={swagger_pw}",
            )
            text = text.replace(
                "BOOTSTRAP_ADMIN_PASSWORD=AdminPass123",
                f"BOOTSTRAP_ADMIN_PASSWORD={admin_pw}",
            )
        if use_postgres:
            text = text.replace(
                "DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/keel",
                f"DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/{project}",
            )
        else:
            text = re.sub(
                r"(?m)^DATABASE_URL=.*$",
                "DATABASE_URL=sqlite+aiosqlite:///./dev.db",
                text,
                count=1,
            )
        return text

    example.write_text(rebrand(base, secrets_ok=False), encoding="utf-8")
    (ROOT / ".env").write_text(
        rebrand(example.read_text(encoding="utf-8"), secrets_ok=True),
        encoding="utf-8",
    )


def _patch_config(
    project: str, title: str, table_prefix: str, include_demo: bool
) -> None:
    path = ROOT / "conf" / "config.py"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    text = text.replace('APP_TITLE: str = "Keel"', f'APP_TITLE: str = "{title}"')
    text = text.replace('PROJECT_NAME: str = "keel"', f'PROJECT_NAME: str = "{project}"')
    text = text.replace(
        'APP_DESCRIPTION: str = "FastAPI scaffold with DRF-style ViewSets, SQLAlchemy and RBAC"',
        f'APP_DESCRIPTION: str = "{title} — FastAPI + SQLAlchemy + RBAC"',
    )
    text = text.replace(
        'TABLE_PREFIX: str = "keel_"', f'TABLE_PREFIX: str = "{table_prefix}"'
    )
    text = text.replace(
        "ENABLE_DEMO: bool = True",
        f"ENABLE_DEMO: bool = {'True' if include_demo else 'False'}",
    )
    path.write_text(text, encoding="utf-8")


def _patch_docker(project: str) -> None:
    path = ROOT / "docker-compose.yaml"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "container_name: keel_postgres", f"container_name: {project}_postgres"
    )
    text = text.replace(
        "container_name: keel_redis", f"container_name: {project}_redis"
    )
    text = text.replace("POSTGRES_DB: keel", f"POSTGRES_DB: {project}")
    path.write_text(text, encoding="utf-8")


def _strip_demo() -> None:
    demo = ROOT / "application" / "modules" / "demo"
    if demo.exists():
        shutil.rmtree(demo)

    apis = ROOT / "application" / "apis.py"
    if apis.is_file():
        text = apis.read_text(encoding="utf-8")
        text = re.sub(
            r"from application\.modules\.demo\.apis import api_router as demo_router\n",
            "",
            text,
        )
        text = re.sub(
            r"\nif settings\.ENABLE_DEMO:\n    api_router\.include_router\(demo_router\)\n",
            "\n",
            text,
        )
        if "settings." not in text:
            text = text.replace("from conf import settings\n", "")
        apis.write_text(text, encoding="utf-8")

    models = ROOT / "application" / "models" / "__init__.py"
    if models.is_file():
        text = models.read_text(encoding="utf-8")
        text = re.sub(
            r"from application\.modules\.demo\.models import ItemModel  # noqa: F401\n",
            "",
            text,
        )
        text = text.replace('    "ItemModel",\n', "")
        models.write_text(text, encoding="utf-8")


def _strip_celery() -> None:
    jobs = ROOT / "application" / "modules" / "jobs"
    if jobs.exists():
        shutil.rmtree(jobs)

    celery_app = ROOT / "application" / "celery_app.py"
    if celery_app.is_file():
        celery_app.unlink()

    apis = ROOT / "application" / "apis.py"
    if apis.is_file():
        text = apis.read_text(encoding="utf-8")
        text = re.sub(
            r"from application\.modules\.jobs\.apis import api_router as jobs_router\n",
            "",
            text,
        )
        text = text.replace("api_router.include_router(jobs_router)\n", "")
        apis.write_text(text, encoding="utf-8")

    makefile = ROOT / "Makefile"
    if makefile.is_file():
        text = makefile.read_text(encoding="utf-8")
        for target in ("celery-worker", "celery-beat", "celery-flower"):
            text = re.sub(rf"(?ms)^{re.escape(target)}:.*?^(?=\S|\Z)", "", text)
        text = text.replace(" celery-worker celery-beat celery-flower", "")
        makefile.write_text(text, encoding="utf-8")

    tests_jobs = ROOT / "tests" / "test_jobs.py"
    if tests_jobs.is_file():
        tests_jobs.unlink()


def main(argv: list[str] | None = None) -> None:
    answers = _parse_args(argv if argv is not None else sys.argv[1:])
    if not answers:
        print(
            "copier_post: no answers (pass --project-name or write .copier-answers.yml)",
            file=sys.stderr,
        )
        return

    raw_name = str(answers.get("project_name") or "app").strip()
    project = _slug(raw_name)
    title = str(answers.get("app_title") or project).strip()
    table_prefix = str(answers.get("table_prefix") or f"{project}_").strip()
    if not table_prefix.endswith("_"):
        table_prefix += "_"
    author = str(answers.get("author_name") or "developer").strip()
    email = str(answers.get("author_email") or "dev@example.com").strip()
    include_demo = bool(answers.get("include_demo", True))
    include_celery = bool(answers.get("include_celery", True))
    use_postgres = bool(answers.get("use_postgres", True))

    _set_pyproject(project, author, email, title)
    _patch_config(project, title, table_prefix, include_demo)
    _patch_docker(project)
    _write_env(
        project=project,
        title=title,
        table_prefix=table_prefix,
        use_postgres=use_postgres,
        include_demo=include_demo,
    )

    if not include_demo:
        _strip_demo()
    if not include_celery:
        _strip_celery()

    for readme in (ROOT / "README.md", ROOT / "README.en.md"):
        if readme.is_file():
            text = readme.read_text(encoding="utf-8")
            text = re.sub(r"(?m)^# Keel\s*$", f"# {title}", text, count=1)
            readme.write_text(text, encoding="utf-8")

    print(f"✓ project ready: {project}")
    print(f"  title={title}  table_prefix={table_prefix}")
    print("  next:")
    print(f"    cd {ROOT.name}")
    print("    uv sync --group dev   # or: pip install -e '.[dev]'")
    print("    make run-reload")


if __name__ == "__main__":
    main()
