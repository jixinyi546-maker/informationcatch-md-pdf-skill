#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen


DOWNLOADS = Path.home() / "Downloads"
MD2PDF_SCRIPT = Path("C:/Users/Administrator/.codex/skills/md2pdf/scripts/md2pdf.py")


def _http_get_text(url: str, timeout: int = 45) -> str:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _safe_filename(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]+', "_", name).strip()
    return re.sub(r"\s+", " ", name) or "untitled"


def _detect_source(url: str) -> str:
    host = (urlparse(url).netloc or "").lower()
    if "youtube.com" in host or "youtu.be" in host:
        return "YouTube"
    if url.lower().endswith(".pdf"):
        return "PDF"
    return "Web"


def _decide_format(fmt: str, intent_text: str) -> str:
    if fmt in ("md", "pdf"):
        return fmt

    text = (intent_text or "").lower()
    pdf_kw = ["pdf", "print-ready", "export pdf", "to pdf", "转pdf", "导出pdf", "生成pdf"]
    md_kw = ["markdown", ".md", "md", "export md", "to md", "to markdown", "转markdown", "导出markdown", "生成md"]

    if any(k in text for k in pdf_kw):
        return "pdf"
    if any(k in text for k in md_kw):
        return "md"
    return "md"


def _fetch_generic_markdown(url: str) -> str:
    tries = [f"https://r.jina.ai/{url}", f"https://defuddle.md/{url}"]
    for u in tries:
        try:
            text = _http_get_text(u)
            if len(text.splitlines()) > 5 and "ERROR" not in text[:300]:
                return text
        except Exception:
            pass
    raise RuntimeError(f"Failed to fetch URL via proxy chain: {url}")


def _youtube_fetch(url: str) -> tuple[str, str, str]:
    py = Path(sys.executable)
    cmd = [str(py), "-m", "yt_dlp", "--dump-single-json", "--no-warnings", url]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "yt-dlp failed")
    data = json.loads(proc.stdout)

    title = data.get("title") or "YouTube Video"
    uploader = data.get("uploader") or ""
    duration = data.get("duration_string") or ""
    views = data.get("view_count")
    likes = data.get("like_count")
    comments = data.get("comment_count")
    upload_date = data.get("upload_date", "")
    if len(upload_date) == 8:
        upload_date = f"{upload_date[0:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
    chapters = data.get("chapters") or []
    description = data.get("description") or ""

    summary = (
        f"Video published by {uploader}, duration {duration}. "
        f"Stats: views {views}, likes {likes}, comments {comments}. "
        f"Published date: {upload_date or 'unknown'}."
    )

    lines = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append("## Metadata")
    lines.append(f"- Channel: {uploader}")
    lines.append(f"- Duration: {duration}")
    lines.append(f"- Views: {views}")
    lines.append(f"- Likes: {likes}")
    lines.append(f"- Comments: {comments}")
    lines.append(f"- Published: {upload_date or 'Unknown'}")
    lines.append(f"- URL: {data.get('webpage_url') or url}")
    lines.append("")
    if chapters:
        lines.append("## Chapters")
        for ch in chapters:
            st = int(ch.get("start_time", 0))
            mm = st // 60
            ss = st % 60
            lines.append(f"- {mm:02d}:{ss:02d} {ch.get('title','')}")
        lines.append("")
    lines.append("## Description")
    lines.append(description.strip() or "(empty)")
    lines.append("")
    return title, summary, "\n".join(lines)


def build_markdown(url: str) -> tuple[str, str]:
    source = _detect_source(url)
    if source == "YouTube":
        title, summary, body = _youtube_fetch(url)
    else:
        raw = _fetch_generic_markdown(url)
        title = "Fetched Document"
        m = re.search(r"(?im)^title:\s*(.+)$", raw)
        if m:
            title = m.group(1).strip().strip('"')
        summary = (
            "Content fetched through proxy chain. "
            "If the page depends on login or dynamic rendering, body text may be incomplete."
        )
        body = raw

    today = dt.date.today().isoformat()
    front = [
        "---",
        f'title: "{title}"',
        'author: ""',
        f'date: "{today}"',
        f'url: "{url}"',
        f'source: "{source}"',
        "---",
        "",
        f"# {title}",
        "",
        "## Summary",
        summary,
        "",
        "## Content",
        "",
        body,
        "",
    ]
    return title, "\n".join(front)


def to_pdf(md_path: Path, pdf_path: Path, theme: str, watermark: str) -> None:
    if not MD2PDF_SCRIPT.exists():
        raise RuntimeError(f"md2pdf script not found: {MD2PDF_SCRIPT}")
    cmd = [
        str(sys.executable),
        str(MD2PDF_SCRIPT),
        "--input",
        str(md_path),
        "--output",
        str(pdf_path),
        "--theme",
        theme,
    ]
    if watermark:
        cmd += ["--watermark", watermark]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "md2pdf failed")


def main() -> int:
    p = argparse.ArgumentParser(description="Fetch URL and export to markdown or pdf.")
    p.add_argument("--url", required=True, help="Target URL")
    p.add_argument("--format", choices=["md", "pdf", "auto"], default="auto")
    p.add_argument(
        "--intent",
        default="",
        help="Natural-language intent used when --format auto (e.g. 'export pdf').",
    )
    p.add_argument("--output", default="", help="Output file path")
    p.add_argument("--theme", default="warm-academic", help="PDF theme")
    p.add_argument("--watermark", default="", help="PDF watermark text")
    args = p.parse_args()

    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    title, md_text = build_markdown(args.url)
    safe = _safe_filename(title)
    final_format = _decide_format(args.format, args.intent)

    if args.output:
        out_path = Path(args.output)
    else:
        suffix = ".pdf" if final_format == "pdf" else ".md"
        out_path = DOWNLOADS / f"{safe}{suffix}"

    md_path = DOWNLOADS / f"{safe}.md"
    md_path.write_text(md_text, encoding="utf-8")

    if final_format == "md":
        if out_path != md_path:
            out_path.write_text(md_text, encoding="utf-8")
        print(str(out_path))
        return 0

    pdf_path = out_path if out_path.suffix.lower() == ".pdf" else out_path.with_suffix(".pdf")
    to_pdf(md_path, pdf_path, theme=args.theme, watermark=args.watermark)
    print(str(pdf_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
