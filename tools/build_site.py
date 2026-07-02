#!/usr/bin/env python3
"""Assemble the static HTML site from per-paper make4ht output.

Given a list of paper directories on the command line, this script:

1. recreates the ``site/`` output directory (plus a ``.nojekyll`` marker);
2. for each paper, copies the make4ht HTML/CSS into ``site/<slug>/`` as
   ``index.html`` and injects a back-navigation link and a collapsible
   "Source code" section embedding the paper's Python and Lean sources;
3. writes a landing page ``site/index.html`` listing every paper.

It uses only the Python standard library. Each paper is expected to have
been converted with ``make -C <paper> html`` first, producing
``<paper>/main.html`` and ``<paper>/main.css``.
"""

from __future__ import annotations

import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

# Highlight.js language class per source extension. Lean is not a
# highlight.js language, so it is shown as plain (readable) text.
_LANG = {".py": "language-python", ".lean": "language-plaintext"}

# Directories inside a paper whose source files are embedded on its page,
# in display order.
_CODE_GROUPS = [
    ("Python implementation", "code", [".py"]),
    ("Lean formalisation", "lean", [".lean"]),
]

# Build artifacts and environments never embedded or listed.
_SKIP_PARTS = {".venv", ".lake", "__pycache__", ".mypy_cache", ".ruff_cache",
               ".pytest_cache", "build", "dist"}

_HIGHLIGHT = """\
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/\
highlight.js/11.9.0/styles/github.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/\
highlight.min.js"></script>
<script>document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('pre code.language-python').forEach(function (el) {
    window.hljs.highlightElement(el);
  });
});</script>
"""

_INJECTED_STYLE = """\
<style>
  .site-nav { font-family: sans-serif; margin: 1rem 0 2rem; }
  .site-nav a { text-decoration: none; }
  .paper-code { font-family: sans-serif; margin-top: 3rem;
    border-top: 1px solid #ddd; padding-top: 1.5rem; }
  .paper-code details { margin: 0.5rem 0; border: 1px solid #e2e2e2;
    border-radius: 6px; padding: 0.25rem 0.75rem; background: #fafafa; }
  .paper-code summary { cursor: pointer; font-family: monospace;
    padding: 0.35rem 0; }
  .paper-code pre { overflow-x: auto; background: #fff; padding: 0.75rem;
    border-radius: 6px; }
</style>
"""


def _title_of(html_text: str, fallback: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html_text, re.DOTALL)
    if match:
        title = re.sub(r"\s+", " ", match.group(1)).strip()
        if title:
            return title
    return fallback


def _description_of(paper: Path) -> str:
    """First prose paragraph of the paper's README, if any."""
    readme = paper / "README.md"
    if not readme.is_file():
        return ""
    paragraph: list[str] = []
    for line in readme.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if not stripped:
            if paragraph:
                break
            continue
        paragraph.append(stripped)
    return " ".join(paragraph)


def _iter_source_files(base: Path, exts: list[str]) -> list[Path]:
    if not base.is_dir():
        return []
    found: list[Path] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file() or path.suffix not in exts:
            continue
        if any(part in _SKIP_PARTS for part in path.relative_to(base).parts):
            continue
        found.append(path)
    return found


def _code_section(paper: Path) -> str:
    blocks: list[str] = []
    for heading, subdir, exts in _CODE_GROUPS:
        files = _iter_source_files(paper / subdir, exts)
        if not files:
            continue
        blocks.append(f"<h3>{html.escape(heading)}</h3>")
        for path in files:
            rel = path.relative_to(paper).as_posix()
            lang = _LANG.get(path.suffix, "language-plaintext")
            body = html.escape(path.read_text(encoding="utf-8"))
            blocks.append(
                f"<details open><summary>{html.escape(rel)}</summary>"
                f'<pre><code class="{lang}">{body}</code></pre></details>'
            )
    if not blocks:
        return ""
    intro = (
        "The implementation and the machine-checked proofs accompanying "
        "this paper. Click a file heading to collapse or expand it."
    )
    return (
        '<section class="paper-code"><h2>Source code</h2>'
        f"<p>{intro}</p>" + "".join(blocks) + "</section>"
    )


def _copy_assets(paper: Path, dest: Path) -> None:
    for asset in paper.glob("main.*"):
        if asset.suffix in {".html"}:
            continue
        if asset.suffix in {".css", ".svg", ".png", ".woff", ".woff2"}:
            shutil.copy2(asset, dest / asset.name)


def _build_paper(paper: Path) -> tuple[str, str, str]:
    slug = paper.name
    src_html = paper / "main.html"
    if not src_html.is_file():
        raise SystemExit(
            f"missing {src_html}; run 'make -C {slug} html' first"
        )
    text = src_html.read_text(encoding="utf-8")
    title = _title_of(text, slug)

    nav = '<nav class="site-nav"><a href="../index.html">'
    nav += "&larr; All papers</a></nav>"
    text = re.sub(
        r"(<body[^>]*>)", r"\1" + nav + _INJECTED_STYLE, text, count=1
    )
    tail = _code_section(paper) + _HIGHLIGHT + "</body>"
    text = text.replace("</body>", tail, 1)

    dest = SITE / slug
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "index.html").write_text(text, encoding="utf-8")
    _copy_assets(paper, dest)
    return slug, title, _description_of(paper)


_INDEX_STYLE = """\
<style>
  body { font-family: -apple-system, system-ui, sans-serif; max-width: 48rem;
    margin: 3rem auto; padding: 0 1.25rem; line-height: 1.55; color: #1a1a1a; }
  h1 { font-size: 1.9rem; }
  .paper { border: 1px solid #e2e2e2; border-radius: 8px; padding: 1rem 1.25rem;
    margin: 1.25rem 0; }
  .paper h2 { font-size: 1.2rem; margin: 0 0 0.35rem; }
  .paper .slug { font-family: monospace; color: #666; font-size: 0.85rem; }
  a { color: #0a58ca; }
  footer { margin-top: 3rem; color: #666; font-size: 0.85rem; }
</style>
"""


def _build_index(papers: list[tuple[str, str, str]]) -> None:
    cards: list[str] = []
    for slug, title, desc in papers:
        card = f'<div class="paper"><h2><a href="{html.escape(slug)}/'
        card += f'index.html">{html.escape(title)}</a></h2>'
        card += f'<div class="slug">{html.escape(slug)}</div>'
        if desc:
            card += f"<p>{html.escape(desc)}</p>"
        card += "</div>"
        cards.append(card)
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Papers</title>
{_INDEX_STYLE}</head>
<body>
<h1>Papers</h1>
<p>Research papers in mathematics and computer science, with accompanying
code and, where relevant, machine-checked proofs. Each paper is readable
as HTML (mathematics rendered with MathJax) with its source code embedded
on the page.</p>
{''.join(cards)}
<footer>Built from the LaTeX sources with make4ht. Source repository:
<a href="https://github.com/dannywillems/papers">dannywillems/papers</a>.
</footer>
</body>
</html>
"""
    (SITE / "index.html").write_text(page, encoding="utf-8")


def main(argv: list[str]) -> int:
    paper_dirs = argv[1:]
    if not paper_dirs:
        print("usage: build_site.py <paper-dir> [<paper-dir> ...]")
        return 2
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    (SITE / ".nojekyll").write_text("", encoding="utf-8")

    built: list[tuple[str, str, str]] = []
    for name in paper_dirs:
        paper = (ROOT / name).resolve()
        built.append(_build_paper(paper))
        print(f"built site/{paper.name}/index.html")
    _build_index(built)
    print(f"built site/index.html ({len(built)} paper(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
