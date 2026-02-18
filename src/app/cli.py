"""Command-line entrypoints for local workflows."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from app.indexing.pipeline import IndexingPipeline
from app.logging_config import setup_logging

if TYPE_CHECKING:
    from collections.abc import Sequence


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="index-repo",
        description="Index a code repository into Qdrant.",
    )
    parser.add_argument("repo_id", help="Logical repository identifier")
    parser.add_argument("path", type=Path, help="Path to the repository root")
    parser.add_argument(
        "--glob",
        dest="globs",
        action="append",
        default=None,
        help="Include glob (repeatable). Default: **/*",
    )
    parser.add_argument(
        "--language",
        dest="languages",
        action="append",
        default=None,
        help="Language allowlist entry (repeatable). Example: python",
    )
    parser.add_argument(
        "--delete-existing",
        dest="delete_existing",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Delete existing points for repo_id before indexing (default: true)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--exit-nonzero-on-errors",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Exit non-zero if any files fail to index (default: true)",
    )
    return parser


async def _run_index(args: argparse.Namespace) -> int:
    pipeline = IndexingPipeline(delete_existing=bool(args.delete_existing))
    result = await pipeline.index_repo(
        args.repo_id,
        args.path,
        globs=args.globs,
        languages=args.languages,
    )

    if result.errors and args.exit_nonzero_on_errors:
        return 1
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    setup_logging(str(args.log_level))

    try:
        return asyncio.run(_run_index(args))
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"index-repo failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
