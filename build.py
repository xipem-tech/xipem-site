#!/usr/bin/env python3
"""Builds the static xipem.com site into public/ (upload its contents to
Hostinger's public_html).

Pages are Markdown in src/ (a small subset: headings, paragraphs, bullet
lists, tables, **bold**, `code`, [links](url), bare https:// links).
A page can instead name an external Markdown source in src/pages.txt, so a
policy can live next to its app (e.g. the Monlings repo) and stay the single
source of truth; only the part after the first line that is exactly '---'
is published.

Usage: python3 build.py
"""
from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "public"
STATIC = ["style.css", "app-ads.txt", "robots.txt"]


def inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', out)
    out = re.sub(r'(?<!href=")(?<!">)(https://[^\s<)]+[^\s<).,;])', r'<a href="\1">\1</a>', out)
    out = re.sub(r"\b([\w.+-]+@[\w-]+\.[\w.]+[a-z])\b", r'<a href="mailto:\1">\1</a>', out)
    return out


def md_to_html(md: str) -> tuple[str, str]:
    """Returns (title, body html)."""
    lines = md.splitlines()
    body: list[str] = []
    title = ""
    i = 0
    para: list[str] = []

    def flush() -> None:
        if para:
            body.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            flush()
            i += 1
            continue
        m = re.match(r"^(#{1,3}) (.*)", line)
        if m:
            flush()
            level = len(m.group(1))
            if level == 1 and not title:
                title = m.group(2)
            body.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue
        if line.startswith("- "):
            flush()
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append("<li>" + inline(lines[i][2:].strip()) + "</li>")
                i += 1
            body.append("<ul>" + "".join(items) + "</ul>")
            continue
        if line.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i].strip().strip("|").split("|"))
                i += 1
            head, data = rows[0], [r for r in rows[1:] if not set("".join(r)) <= set("-: ")]
            t = ["<div class=\"table\"><table><thead><tr>"]
            t += [f"<th>{inline(c.strip())}</th>" for c in head]
            t.append("</tr></thead><tbody>")
            for r in data:
                t.append("<tr>" + "".join(
                    f'<td data-label="{html.escape(h.strip())}">{inline(c.strip())}</td>'
                    for h, c in zip(head, r)) + "</tr>")
            t.append("</tbody></table></div>")
            body.append("".join(t))
            continue
        para.append(line.strip())
        i += 1
    flush()
    return title, "\n".join(body)


def page(title: str, body: str, depth: int) -> str:
    up = "../" * depth
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{up}style.css">
</head>
<body>
<header><a href="{up or './'}">Xipem</a></header>
<main>
{body}
</main>
<footer>Xipem Digital Ltda · CNPJ 66.506.226/0001-77 · <a href="mailto:support@xipem.com">support@xipem.com</a></footer>
</body>
</html>
"""


def published_part(md: str) -> str:
    parts = re.split(r"^---$", md, maxsplit=1, flags=re.M)
    return parts[1] if len(parts) == 2 else md


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for name in STATIC:
        shutil.copy(SRC / name, OUT / name)
    sources: list[tuple[str, str]] = []
    for md in SRC.rglob("*.md"):
        rel = md.relative_to(SRC).with_suffix("")
        target = "" if rel.name == "index" else str(rel)
        if rel.name == "index":
            target = str(rel.parent) if str(rel.parent) != "." else ""
        sources.append((target, md.read_text()))
    pages_txt = SRC / "pages.txt"
    if pages_txt.exists():
        for row in pages_txt.read_text().splitlines():
            row = row.strip()
            if not row or row.startswith("#"):
                continue
            target, src = [p.strip() for p in row.split("=", 1)]
            sources.append((target, published_part((ROOT / src).resolve().read_text())))
    for target, md in sources:
        title, body = md_to_html(md)
        dest = OUT / target / "index.html" if target else OUT / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        depth = len(Path(target).parts) if target else 0
        dest.write_text(page(title or "Xipem", body, depth))
        print("built", "/" + (target + "/" if target else ""))


if __name__ == "__main__":
    build()
