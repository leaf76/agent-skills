# Usage Notes

## File-type behavior

- Text-like extensions (`.txt`, `.md`, `.json`, `.csv`, `.html`, `.xml`, `.yml`, `.yaml`, `.log`) are read directly.
- `.pdf` uses `pdftotext` when available.
- Image extensions (`.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.gif`, `.tiff`, `.svg`) use OCR with `--ocr`.

## Recommended OCR workflow

1. Generate a clean screenshot (no scaled UI compression).
2. If OCR result is weak, crop to the relevant region.
3. Increase resolution first if possible, then rerun.
4. Use `--max-chars 4000` for long chat contexts.

## Error handling

If tool reports missing dependency:

- Install OCR: `brew install tesseract` (macOS)
- Install PDF text tool: `brew install poppler` (for `pdftotext`)
