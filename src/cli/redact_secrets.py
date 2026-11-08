"""Mask known credential formats in generated report and data files.

This is the last check before scan output is committed, uploaded as an
artifact or deployed to GitHub Pages.  Scanners mask credentials when they
capture a URL (see :mod:`src.lib.secret_redaction`), but a new scanner or a new
field can miss that step, and older rows in the metadata database predate it.
Running this over every generated file means a missed case is masked before it
is published, not after a secret-scanning alert.

Only format-based matching is applied (Google API keys, GitHub tokens and
similar).  Parameter-name matching is deliberately not used here: published
files also list seed page URLs, and some of those are addressed by parameters
such as ``?key=SiteNotices_CookiesPolicy`` that must stay intact.

Files are rewritten in place only when something was masked.  The tool prints
how many values it masked in each file, never the values, and always exits 0
so it cannot block report publishing.

Usage::

    python3 -m src.cli.redact_secrets docs/third-party-tools-data.json docs/domains/
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path

from src.lib.secret_redaction import redact_known_formats

TEXT_SUFFIXES: frozenset[str] = frozenset(
    {".json", ".jsonl", ".csv", ".md", ".html", ".txt"}
)


def iter_text_files(paths: Iterable[Path]) -> Iterator[Path]:
    """Yield text files named directly or found under the given directories.

    Args:
        paths: Files or directories.  Missing paths are skipped, because
            several report files are optional.

    Yields:
        Paths of regular files whose suffix is in :data:`TEXT_SUFFIXES`.
    """
    for path in paths:
        if path.is_dir():
            candidates = sorted(p for p in path.rglob("*") if p.is_file())
        elif path.is_file():
            candidates = [path]
        else:
            continue
        for candidate in candidates:
            if candidate.suffix.lower() in TEXT_SUFFIXES:
                yield candidate


def redact_file(path: Path) -> int:
    """Mask known credential formats in one file, rewriting it if needed.

    Args:
        path: A UTF-8 text file.  A byte-order mark is preserved.

    Returns:
        Number of values masked; 0 when the file is unchanged or not UTF-8.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"Skipped (not UTF-8): {path}", file=sys.stderr)
        return 0
    masked, count = redact_known_formats(text)
    if count:
        path.write_text(masked, encoding="utf-8")
    return count


def main(argv: list[str] | None = None) -> int:
    """Mask credentials in the given files and directories.

    Args:
        argv: Command-line arguments; defaults to ``sys.argv[1:]``.

    Returns:
        Process exit code, always 0.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="+", type=Path, help="Files or directories to check")
    args = parser.parse_args(argv)

    total = 0
    for path in iter_text_files(args.paths):
        count = redact_file(path)
        if count:
            print(f"::warning file={path}::Masked {count} credential value(s) in {path}")
            total += count
    print(f"Credential check complete: {total} value(s) masked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
