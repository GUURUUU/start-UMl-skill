#!/usr/bin/env python3
"""Extract PDF text and render pages to PNG for UML / diagram work.

The StarUML workflow needs both halves:
  * text  -> read exercise statements (pdfplumber preferred)
  * PNG   -> see correction diagrams the text layer does not describe (pymupdf)

Usage:
    python scripts/pdf_extract.py file1.pdf file2.pdf
    python scripts/pdf_extract.py folder/ --outdir .extract --dpi 150
    python scripts/pdf_extract.py file.pdf --text-only
    python scripts/pdf_extract.py file.pdf --images-only

Outputs next to --outdir (default: .extract):
    <stem>.txt          UTF-8, page markers "=== PAGE N ==="
    <stem>_pN.png       one image per page

Dependencies (all optional, at least one per job):
    text  : pdfplumber  or  pymupdf  or  PyPDF2
    images: pymupdf
Install:  pip install pdfplumber pymupdf PyPDF2
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:  # keep non-ASCII output from crashing cp1252 consoles
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def _load_pymupdf():
    try:
        import pymupdf  # type: ignore

        return pymupdf
    except ImportError:
        try:
            import fitz  # type: ignore

            return fitz
        except ImportError:
            return None


def extract_text(pdf_path: Path) -> tuple[str, str]:
    """Return (text, backend). Tries pdfplumber -> pymupdf -> PyPDF2."""
    try:
        import pdfplumber  # type: ignore

        pages = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                pages.append(f"=== PAGE {i} ===\n{page.extract_text() or ''}")
        return "\n\n".join(pages), "pdfplumber"
    except ImportError:
        pass

    mupdf = _load_pymupdf()
    if mupdf is not None:
        doc = mupdf.open(str(pdf_path))
        pages = [
            f"=== PAGE {i} ===\n{page.get_text()}"
            for i, page in enumerate(doc, start=1)
        ]
        doc.close()
        return "\n\n".join(pages), "pymupdf"

    try:
        from PyPDF2 import PdfReader  # type: ignore

        reader = PdfReader(str(pdf_path))
        pages = [
            f"=== PAGE {i} ===\n{page.extract_text() or ''}"
            for i, page in enumerate(reader.pages, start=1)
        ]
        return "\n\n".join(pages), "PyPDF2"
    except ImportError:
        return "", "none"


def render_pages(pdf_path: Path, outdir: Path, dpi: int) -> list[Path]:
    mupdf = _load_pymupdf()
    if mupdf is None:
        raise RuntimeError(
            "pymupdf is required for image rendering: pip install pymupdf"
        )
    doc = mupdf.open(str(pdf_path))
    saved: list[Path] = []
    try:
        for i, page in enumerate(doc, start=1):
            out = outdir / f"{pdf_path.stem}_p{i}.png"
            page.get_pixmap(dpi=dpi).save(str(out))
            saved.append(out)
    finally:
        doc.close()
    return saved


def collect_inputs(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            files.extend(sorted(p.glob("*.pdf")))
        elif p.is_file() and p.suffix.lower() == ".pdf":
            files.append(p)
        else:
            print(f"skip (not a PDF): {raw}", file=sys.stderr)
    # de-duplicate while preserving order
    seen = set()
    unique = []
    for f in files:
        key = str(f.resolve()).lower()
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract PDF text and render pages to PNG."
    )
    parser.add_argument("inputs", nargs="+", help="PDF files and/or directories")
    parser.add_argument(
        "--outdir", default=".extract", help="output directory (default: .extract)"
    )
    parser.add_argument(
        "--dpi", type=int, default=150, help="render resolution (default: 150)"
    )
    parser.add_argument("--text-only", action="store_true", help="skip PNG rendering")
    parser.add_argument("--images-only", action="store_true", help="skip text extraction")
    args = parser.parse_args(argv)

    pdfs = collect_inputs(args.inputs)
    if not pdfs:
        print("No PDF files found.", file=sys.stderr)
        return 1

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    failures = 0
    for pdf in pdfs:
        print(f"\n[{pdf.name}]")
        if not args.images_only:
            text, backend = extract_text(pdf)
            if backend == "none":
                print("  text : SKIPPED (no pdfplumber/pymupdf/PyPDF2 installed)")
                failures += 1
            else:
                out = outdir / f"{pdf.stem}.txt"
                out.write_text(text, encoding="utf-8")
                print(f"  text : {out}  ({backend}, {len(text)} chars)")
        if not args.text_only:
            try:
                saved = render_pages(pdf, outdir, args.dpi)
                print(f"  image: {len(saved)} page(s) at {args.dpi} dpi -> {outdir}")
            except RuntimeError as exc:
                print(f"  image: SKIPPED ({exc})", file=sys.stderr)
                failures += 1

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
