#!/usr/bin/env python3
"""Run fast structural checks against a rendered resume PDF."""

from __future__ import annotations

import argparse
from pathlib import Path

import pdfplumber
from pypdf import PdfReader


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--max-pages", type=int, default=2)
    parser.add_argument("--require", action="append", default=[])
    args = parser.parse_args()

    reader = PdfReader(str(args.pdf))
    if not reader.pages:
        raise SystemExit("PDF has no pages")
    if len(reader.pages) > args.max_pages:
        raise SystemExit(f"PDF has {len(reader.pages)} pages; expected at most {args.max_pages}")

    with pdfplumber.open(args.pdf) as document:
        text = "\n".join(page.extract_text() or "" for page in document.pages)

    for required in args.require:
        if required not in text:
            raise SystemExit(f"Required text not found: {required}")
    if "\ufffd" in text:
        raise SystemExit("PDF text contains replacement characters")

    print(f"verified: {args.pdf} ({len(reader.pages)} page(s), {len(text)} extracted characters)")


if __name__ == "__main__":
    main()
