---
name: jixinyi-catch-md-pdf-skill
description: Unified URL fetch skill that converts links to clean Markdown and optionally to PDF in one flow. Use when user provides a URL and wants output as md or pdf, including web pages, YouTube links, and remote PDFs.
version: 1.0.0
---

# jixinyi-catch-md-pdf-skill

Unified fetch-and-export skill:
- Input: URL
- Output: `md` or `pdf`
- Default save path: `~/Downloads`

This skill combines:
- URL-to-Markdown fetch workflow
- Markdown-to-PDF conversion

## When To Use

- User provides a URL and asks to:
  - save as markdown
  - save as pdf
  - choose between md/pdf in one integrated workflow

## Route Rules

- `youtube.com` / `youtu.be`:
  - Use `yt-dlp` metadata path in `scripts/fetch_and_convert.py`
- URL ending with `.pdf`:
  - Use remote PDF text fetch via `r.jina.ai` fallback path
- Others:
  - Use `r.jina.ai` then `defuddle.md` fallback

## Command

```bash
python scripts/fetch_and_convert.py --url "<URL>" --format auto --intent "export pdf"
python scripts/fetch_and_convert.py --url "<URL>" --format auto --intent "save as markdown"
```

Optional parameters:

```bash
python scripts/fetch_and_convert.py \
  --url "<URL>" \
  --format auto \
  --intent "export pdf with watermark" \
  --theme warm-academic \
  --watermark "<text>"
```

## Output

- `--format auto`: infer output from `--intent`
- Explicit `--format md`: writes `{title}.md`
- Explicit `--format pdf`: writes `{title}.pdf` (and keeps intermediate md by default)

Both outputs are saved to `~/Downloads` unless `--output` is provided.

## Notes

- PDF conversion calls local bundled script:
  - `scripts/md2pdf.py`
- Requires:
  - Python 3.8+
  - `reportlab` for PDF conversion
  - `yt-dlp` for YouTube route



