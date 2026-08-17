#!/usr/bin/env python3
"""Read text-like files and run OCR on image files without relying on model vision."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".markdown",
    ".json",
    ".csv",
    ".tsv",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
    ".log",
    ".html",
    ".htm",
    ".xml",
}

IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".gif",
    ".tiff",
    ".tif",
    ".svg",
}

PDF_EXTENSIONS = {".pdf"}


@dataclass
class FileReadResult:
    path: str
    exists: bool
    size_bytes: int
    kind: str
    extracted_text: str
    used_tool: Optional[str]
    truncated: bool
    error: Optional[str]


def run_command(command: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        check=False,
    )


def detect_kind(path: Path, mime: Optional[str]) -> str:
    ext = path.suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in PDF_EXTENSIONS:
        return "pdf"
    if ext in TEXT_EXTENSIONS:
        return "text"
    if mime and mime.startswith("text/"):
        return "text"
    if mime and mime.startswith("image/"):
        return "image"
    if mime == "application/pdf":
        return "pdf"
    return "binary"


def maybe_truncate(text: str, max_chars: int) -> tuple[str, bool]:
    if max_chars <= 0 or len(text) <= max_chars:
        return text, False
    return text[:max_chars] + "\n... [truncated]", True


def read_text_file(path: Path, max_chars: int) -> tuple[str, str]:
    for encoding in ("utf-8", "utf-8-sig", "utf-16", "latin-1"):
        try:
            raw = path.read_text(encoding=encoding)
            return maybe_truncate(raw, max_chars)
        except UnicodeDecodeError:
            continue
    raw = path.read_bytes().decode("latin-1", errors="replace")
    return maybe_truncate(raw, max_chars)


def ocr_image(path: Path, max_chars: int, language: str) -> tuple[str, str, Optional[str]]:
    tesseract = shutil.which("tesseract")
    if not tesseract:
        return "", "tesseract", "tesseract not found in PATH"

    # Tesseract writes text output to stdout with `stdout` format in newer versions when output base is '-' for some versions.
    # Keep a temp file to maximize compatibility.
    tmp_output = path.with_suffix(".ocr.txt")
    cmd = [
        tesseract,
        str(path),
        str(tmp_output.with_suffix("") ),
        "--oem",
        "3",
        "--psm",
        "6",
        "-l",
        language,
    ]
    proc = run_command(cmd, timeout=120)
    text = ""
    if proc.returncode == 0:
        txt_path = tmp_output.with_suffix(".txt")
        if txt_path.exists():
            text, _ = maybe_truncate(txt_path.read_text(encoding="utf-8", errors="replace"), max_chars)
            try:
                txt_path.unlink()
            except OSError:
                pass
    else:
        err = proc.stderr.strip() or "OCR command failed"
        return "", "tesseract", err
    return text, "tesseract", None


def read_pdf(path: Path, max_chars: int) -> tuple[str, str, Optional[str]]:
    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        return "", "pdftotext", "pdftotext not found in PATH"

    cmd = [pdftotext, "-layout", str(path), "-"]
    proc = run_command(cmd, timeout=120)
    if proc.returncode != 0:
        return "", "pdftotext", proc.stderr.strip() or "pdftotext command failed"
    text, _ = maybe_truncate(proc.stdout, max_chars)
    return text, "pdftotext", None


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_file(path: Path, args: argparse.Namespace) -> FileReadResult:
    info = FileReadResult(
        path=str(path),
        exists=False,
        size_bytes=0,
        kind="unknown",
        extracted_text="",
        used_tool=None,
        truncated=False,
        error=None,
    )

    if not path.exists():
        info.error = "File not found"
        return info

    st = path.stat()
    mime, _ = mimetypes.guess_type(str(path))
    kind = detect_kind(path, mime)
    info.exists = True
    info.size_bytes = st.st_size
    info.kind = kind

    if kind == "text":
        text, truncated = maybe_truncate(path.read_text(encoding="utf-8", errors="replace"), args.max_chars)
        info.extracted_text = text
        info.truncated = truncated
        info.used_tool = "native"
        return info

    if kind == "image":
        if args.ocr:
            text, tool, err = ocr_image(path, args.max_chars, args.ocr_lang)
            if err:
                info.error = err
                info.used_tool = tool
            else:
                info.extracted_text = text
            if text:
                info.extracted_text = text
                info.truncated = len(text) > args.max_chars
            return info
        info.error = "Image file requires --ocr to extract text"
        info.used_tool = None
        return info

    if kind == "pdf":
        text, tool, err = read_pdf(path, args.max_chars)
        if err:
            info.error = err
            info.used_tool = tool
            return info
        info.used_tool = "pdftotext"
        info.extracted_text, info.truncated = maybe_truncate(text, args.max_chars)
        return info

    info.error = "Unsupported binary file. Use a dedicated parser or --ocr for images."
    return info


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Read text from files and images")
    p.add_argument("paths", nargs="+", help="One or more files to read")
    p.add_argument("--ocr", action="store_true", help="Run OCR for image files")
    p.add_argument(
        "--ocr-lang",
        default="eng+chi_tra",
        help="OCR language pack for tesseract (default: eng+chi_tra)",
    )
    p.add_argument("--max-chars", type=int, default=4000)
    p.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    return p.parse_args(argv)


def to_dict(result: FileReadResult, include_hash: bool = False) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "path": result.path,
        "exists": result.exists,
        "size_bytes": result.size_bytes,
        "kind": result.kind,
        "used_tool": result.used_tool,
        "extracted_text": result.extracted_text,
        "truncated": result.truncated,
        "error": result.error,
    }
    if include_hash and result.exists:
        data["sha256"] = file_hash(Path(result.path))
    return data


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    results: List[Dict[str, Any]] = []

    for file_path in args.paths:
        path = Path(file_path)
        res = read_file(path, args)
        results.append(to_dict(res, include_hash=True))
        # For non-json output, keep one-line friendly details.
        if args.json:
            continue
        print(f"==> {res.path}")
        if not res.exists:
            print("ERROR:", res.error)
            continue
        print(f"kind={res.kind} tool={res.used_tool or '-'} size={res.size_bytes}")
        if res.error:
            print("ERROR:", res.error)
            continue
        print(res.extracted_text)
        print()

    if args.json:
        payload = {
            "items": results,
            "count": len(results),
            "failed": len([item for item in results if item.get("error")]),
            "success": len([item for item in results if item.get("exists") and not item.get("error")]),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    failed = [item for item in results if item.get("error")]
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
