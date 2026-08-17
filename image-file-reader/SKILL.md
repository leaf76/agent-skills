---
name: image-file-reader
description: Read files and images in automation-friendly way when multimodal parsing is not available. Use for OCR on screenshots, extracting text from PDFs/TXT/JSON/CSV, and returning structured output for downstream processing. Use when you need deterministic, local file inspection instead of model vision.
---

# Image and File Reader

## Goal

Extract readable content from image and file inputs using local tools so the model can continue analyzing without native multimodal input.

## Tools

- `scripts/read_file.py` — one command to inspect one or many files.

## Core Workflow

1. Choose files and run the reader.
2. If the file is image format, use OCR mode (`--ocr`) when needed.
3. Return the extracted text (or clear error messages) for downstream reasoning.

## Command Patterns

Read one file:

```bash
python3 scripts/read_file.py ./screenshot.png --ocr
```

Read multiple files and output JSON:

```bash
python3 scripts/read_file.py ./a.png ./b.pdf ./note.txt --ocr --json
```

Use JSON mode when you need consistent parsing for scripts/agents.

```bash
python3 scripts/read_file.py ./doc.pdf --json > doc_payload.json
```

### Common flags

- `--ocr` : Enable OCR for image files.
- `--ocr-lang` : OCR language (default `eng+chi_tra`).
- `--max-chars` : Truncate long text output for a safer payload.
- `--json` : Output machine-readable JSON object.

## Notes

- OCR needs one of:
  - `tesseract` CLI (preferred)
- PDF text extraction prefers `pdftotext` CLI.
- If no extractor is available, the tool will return a clear, actionable error and suggestions.

## Output Rules

- Keep only extracted content and metadata needed for triage.
- Preserve raw text and mention truncation when it happens.
- Never invent content.

## Next-Step Guidance

If OCR confidence is low or output is empty:

- Re-run with a higher-resolution image.
- Pre-process image (crop/contrast) before OCR.
- Provide a manual transcript if needed.
