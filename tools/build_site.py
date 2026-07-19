#!/usr/bin/env python3
"""Assemble the static HTML site from per-paper make4ht output.

Given a list of paper directories on the command line, this script:

1. recreates the ``site/`` output directory (plus a ``.nojekyll`` marker)
   and copies the shared static assets from ``tools/site_assets/`` to
   ``site/assets/``;
2. for each paper, copies the make4ht HTML/CSS into ``site/<slug>/`` as
   ``index.html``, teaches MathJax the paper's custom ``\\newcommand``
   macros, adds a light/dark theme toggle, and injects a collapsible
   "Source code" section embedding the paper's Python and Lean sources;
3. makes the embedded code runnable in the browser: Python files run
   in-page on Pyodide (see ``site_assets/python-runner.js``), and each
   Lean file gets a link opening it in the official Lean 4 web
   playground, with project-local imports inlined at build time so the
   file is self-contained;
4. writes a landing page ``site/index.html`` listing every paper.

Everything is driven by conventions (the ``code/`` and ``lean/``
directories, file extensions), never by per-paper logic, so a new paper
directory gets all of it for free.

It uses only the Python standard library. Each paper is expected to have
been converted with ``make -C <paper> html`` first, producing
``<paper>/main.html`` and ``<paper>/main.css``.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
ASSETS = ROOT / "tools" / "site_assets"

# Highlight.js language class per source extension. Lean is covered by
# the custom grammar in site_assets/hljs-lean.js.
_LANG = {".py": "language-python", ".lean": "language-lean"}

# data-lang attribute per source extension, used by the runner scripts
# to find the blocks they own.
_LANG_NAME = {".py": "python", ".lean": "lean"}

# Directories inside a paper whose source files are embedded on its page,
# in display order.
_CODE_GROUPS = [
    ("Python implementation", "code", [".py"]),
    ("Lean formalisation", "lean", [".lean"]),
]

# Build artifacts and environments never embedded or listed.
_SKIP_PARTS = {".venv", ".lake", "__pycache__", ".mypy_cache", ".ruff_cache",
               ".pytest_cache", "build", "dist"}

# Theme (light/dark) styling. Colours are always set explicitly so the
# page never renders black-on-black under a browser's dark preference.
_THEME_CSS = """\
<style>
  :root { --bg:#ffffff; --fg:#1a1a1a; --muted:#666; --border:#e2e2e2;
    --card:#fafafa; --link:#0a58ca; --pre:#f6f8fa; }
  html[data-theme="dark"] { --bg:#0d1117; --fg:#c9d1d9; --muted:#8b949e;
    --border:#30363d; --card:#161b22; --link:#58a6ff; --pre:#161b22; }
  html, body { background: var(--bg); color: var(--fg); }
  a { color: var(--link); }
  .site-nav { font-family: sans-serif; margin: 1rem 0 2rem; }
  .theme-toggle { position: fixed; top: 0.6rem; right: 0.6rem; z-index: 1000;
    font: inherit; padding: 0.35rem 0.6rem; border: 1px solid var(--border);
    border-radius: 6px; background: var(--card); color: var(--fg);
    cursor: pointer; }
  .paper-code { font-family: sans-serif; margin-top: 3rem;
    border-top: 1px solid var(--border); padding-top: 1.5rem; }
  .paper-code details { margin: 0.5rem 0; border: 1px solid var(--border);
    border-radius: 6px; padding: 0.25rem 0.75rem; background: var(--card); }
  .paper-code summary { cursor: pointer; font-family: monospace;
    padding: 0.35rem 0; }
  .paper-code pre { overflow-x: auto; background: var(--pre);
    padding: 0.75rem; border-radius: 6px; }
</style>
"""

# highlight.js: a light and a dark stylesheet, toggled by the theme script.
_HLJS_LINKS = """\
<link id="hljs-light" rel="stylesheet" href="https://cdnjs.cloudflare.com/\
ajax/libs/highlight.js/11.9.0/styles/github.min.css">
<link id="hljs-dark" rel="stylesheet" href="https://cdnjs.cloudflare.com/\
ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css" disabled>
"""

# Runs in <head> before the body paints, to avoid a flash of the wrong
# theme.
_EARLY_THEME_SCRIPT = """\
<script>(function () {
  try {
    var t = localStorage.getItem('theme') ||
      ((window.matchMedia &&
        window.matchMedia('(prefers-color-scheme: dark)').matches)
        ? 'dark' : 'light');
    document.documentElement.dataset.theme = t;
  } catch (e) {}
})();</script>
"""

# Wires the toggle button and swaps the highlight.js stylesheet.
_THEME_SCRIPT = """\
<script>(function () {
  var root = document.documentElement;
  function apply(t) {
    root.dataset.theme = t;
    var l = document.getElementById('hljs-light');
    var d = document.getElementById('hljs-dark');
    if (l) l.disabled = (t === 'dark');
    if (d) d.disabled = (t !== 'dark');
    try { localStorage.setItem('theme', t); } catch (e) {}
    var b = document.getElementById('theme-toggle');
    if (b) b.textContent = (t === 'dark' ? 'Light mode' : 'Dark mode');
  }
  apply(root.dataset.theme || 'light');
  var btn = document.getElementById('theme-toggle');
  if (btn) btn.addEventListener('click', function () {
    apply(root.dataset.theme === 'dark' ? 'light' : 'dark');
  });
})();</script>
"""

_TOGGLE_BUTTON = (
    '<button id="theme-toggle" class="theme-toggle" type="button">'
    "Dark mode</button>"
)

_HLJS_SCRIPT = """\
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/\
highlight.min.js"></script>
<script src="../assets/hljs-lean.js"></script>
<script>document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('pre code[class*="language-"]')
    .forEach(function (el) {
      if (window.hljs) window.hljs.highlightElement(el);
    });
});</script>
"""

# Stylesheet and scripts making the embedded code runnable. Relative to
# a paper page, the shared assets live at ../assets/.
_RUNNER_CSS = '<link rel="stylesheet" href="../assets/code-run.css">'
_RUNNER_SCRIPTS = (
    '<script src="../assets/python-runner.js"></script>'
    '<script src="../assets/lean-playground.js"></script>'
)

# Parses \newcommand{\name}[nargs]{body} from a paper's LaTeX source.
_NEWCOMMAND = re.compile(r"\\newcommand\{\\([A-Za-z]+)\}(?:\[(\d+)\])?\{")


def _balanced_body(text: str, open_brace: int) -> str | None:
    """Return the contents of the brace group starting at ``open_brace``."""
    depth = 0
    for i in range(open_brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace + 1 : i]
    return None


def _mathjax_macros(paper: Path) -> str:
    """Return a MathJax config script defining the paper's macros.

    make4ht passes raw TeX to MathJax, which does not know the preamble's
    custom commands. Without this they render as red literal text.
    """
    tex = (paper / "main.tex").read_text(encoding="utf-8")
    macros: dict[str, object] = {}
    for m in _NEWCOMMAND.finditer(tex):
        body = _balanced_body(tex, m.end() - 1)
        if body is None:
            continue
        name, nargs = m.group(1), m.group(2)
        macros[name] = [body, int(nargs)] if nargs else body
    if not macros:
        return ""
    payload = json.dumps(macros)
    return (
        "<script>window.MathJax=window.MathJax||{};"
        "window.MathJax.tex=window.MathJax.tex||{};"
        "window.MathJax.tex.macros=Object.assign({},"
        f"window.MathJax.tex.macros,{payload});</script>"
    )


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


_LEAN_IMPORT = re.compile(r"^import\s+([\w.]+)\s*$")


def _lean_bundle(
    root: Path, path: Path, seen: set[Path]
) -> tuple[list[str], list[tuple[Path, str]]]:
    """Inline the project-local imports of ``path``, depth first.

    ``root`` is the Lean source root against which module names resolve
    (``Ads.Merkle`` -> ``Ads/Merkle.lean``). Returns the external
    ``import`` lines and the ``(file, body)`` pairs in dependency order,
    each body stripped of its import lines. ``seen`` guards against
    duplicated and cyclic imports.
    """
    if path in seen:
        return [], []
    seen.add(path)
    externals: list[str] = []
    bodies: list[tuple[Path, str]] = []
    kept: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _LEAN_IMPORT.match(line)
        if not match:
            kept.append(line)
            continue
        local = root / (match.group(1).replace(".", "/") + ".lean")
        if local.is_file():
            ext, deps = _lean_bundle(root, local, seen)
            externals.extend(ext)
            bodies.extend(deps)
        else:
            externals.append(line)
    bodies.append((path, "\n".join(kept).strip("\n")))
    return externals, bodies


def _lean_playground_source(root: Path, path: Path, paper: Path) -> str:
    """Self-contained source for the Lean 4 web playground.

    The playground compiles a single buffer, so project-local imports
    are replaced by the imported files' contents (in dependency order);
    external imports (e.g. Mathlib) are kept, deduplicated, at the top.
    If the file defines ``main`` an ``#eval main`` is appended so the
    demonstration actually runs in the playground.
    """
    externals, bodies = _lean_bundle(root, path, set())
    parts: list[str] = list(dict.fromkeys(externals))
    if parts:
        parts.append("")
    for src, body in bodies:
        if not body:
            continue
        if src != path:
            rel = src.relative_to(paper).as_posix()
            parts.append(f"-- Inlined from {rel} (project-local import).")
        parts.append(body)
        parts.append("")
    text = "\n".join(parts).strip("\n") + "\n"
    if re.search(r"^def main\b", text, re.MULTILINE) \
            and "#eval main" not in text:
        text += "\n#eval main\n"
    return text


def _code_section(paper: Path) -> str:
    blocks: list[str] = []
    lean_sources: dict[str, str] = {}
    for heading, subdir, exts in _CODE_GROUPS:
        files = _iter_source_files(paper / subdir, exts)
        if not files:
            continue
        blocks.append(f"<h3>{html.escape(heading)}</h3>")
        for path in files:
            rel = path.relative_to(paper).as_posix()
            lang = _LANG.get(path.suffix, "language-plaintext")
            lang_name = _LANG_NAME.get(path.suffix, "")
            body = html.escape(path.read_text(encoding="utf-8"))
            blocks.append(
                f'<details open data-path="{html.escape(rel)}"'
                f' data-lang="{lang_name}">'
                f"<summary>{html.escape(rel)}</summary>"
                f'<pre><code class="{lang}">{body}</code></pre></details>'
            )
            if path.suffix == ".lean":
                lean_sources[rel] = _lean_playground_source(
                    paper / subdir, path, paper
                )
    if not blocks:
        return ""
    if lean_sources:
        # </ must not appear verbatim inside a script element.
        payload = json.dumps(lean_sources).replace("</", "<\\/")
        blocks.append(
            '<script type="application/json" id="lean-playground-src">'
            f"{payload}</script>"
        )
    intro = (
        "The implementation and the machine-checked proofs accompanying "
        "this paper. Click a file heading to collapse or expand it. "
        "Python files run directly in the browser (Pyodide); Lean files "
        "open in the Lean 4 web playground."
    )
    return (
        '<section class="paper-code"><h2>Source code</h2>'
        f"<p>{intro}</p>" + "".join(blocks) + "</section>"
    )


def _copy_assets(paper: Path, dest: Path) -> None:
    for asset in paper.glob("main.*"):
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

    # make4ht writes intra-document links (citations, cross-references) as
    # main.html#anchor, but the page is served as index.html, so those
    # links would 404. Rewrite them to point at the served file. This does
    # not touch main.css.
    text = text.replace("main.html", "index.html")

    # Head: theme CSS, highlight.js styles, runner stylesheet, early
    # no-flash theme script.
    head = _THEME_CSS + _HLJS_LINKS + _RUNNER_CSS + _EARLY_THEME_SCRIPT
    text = text.replace("</head>", head + "</head>", 1)

    # Teach MathJax the paper's macros, before the MathJax loader runs.
    macros = _mathjax_macros(paper)
    if macros:
        text = re.sub(
            r"(<script[^>]*id=['\"]MathJax-script['\"])",
            lambda m: macros + m.group(1),
            text,
            count=1,
        )

    # Body start: back-navigation and the theme toggle button.
    nav = '<nav class="site-nav"><a href="../index.html">'
    nav += "&larr; All papers</a></nav>"
    text = re.sub(
        r"(<body[^>]*>)", lambda m: m.group(1) + _TOGGLE_BUTTON + nav,
        text, count=1,
    )

    # Body end: embedded source code, highlighting, code runners, theme
    # wiring.
    tail = (
        _code_section(paper) + _HLJS_SCRIPT + _RUNNER_SCRIPTS
        + _THEME_SCRIPT + "</body>"
    )
    text = text.replace("</body>", tail, 1)

    dest = SITE / slug
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "index.html").write_text(text, encoding="utf-8")
    _copy_assets(paper, dest)
    return slug, title, _description_of(paper)


_INDEX_STYLE = """\
<style>
  body { font-family: -apple-system, system-ui, sans-serif; max-width: 48rem;
    margin: 3rem auto; padding: 0 1.25rem; line-height: 1.55; }
  h1 { font-size: 1.9rem; }
  .paper { border: 1px solid var(--border); border-radius: 8px;
    padding: 1rem 1.25rem; margin: 1.25rem 0; background: var(--card); }
  .paper h2 { font-size: 1.2rem; margin: 0 0 0.35rem; }
  .paper .slug { font-family: monospace; color: var(--muted);
    font-size: 0.85rem; }
  footer { margin-top: 3rem; color: var(--muted); font-size: 0.85rem; }
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
{_THEME_CSS}{_INDEX_STYLE}{_EARLY_THEME_SCRIPT}</head>
<body>
{_TOGGLE_BUTTON}
<h1>Papers</h1>
<p>Research papers in mathematics and computer science, with accompanying
code and, where relevant, machine-checked proofs. Each paper is readable
as HTML (mathematics rendered with MathJax) with its source code embedded
on the page: Python runs directly in the browser, and Lean files open in
the Lean 4 web playground.</p>
{''.join(cards)}
<footer>Built from the LaTeX sources with make4ht. Source repository:
<a href="https://github.com/dannywillems/papers">dannywillems/papers</a>.
</footer>
{_THEME_SCRIPT}</body>
</html>
"""
    (SITE / "index.html").write_text(page, encoding="utf-8")


def _copy_site_assets() -> None:
    """Copy the shared static assets into ``site/assets/``.

    The JavaScript is compiled from the TypeScript sources in
    ``tools/site_assets/src/`` into ``tools/site_assets/dist/`` by
    ``make site-assets`` (tsc); this script only copies the results.
    """
    dist = ASSETS / "dist"
    if not dist.is_dir() or not any(dist.glob("*.js")):
        raise SystemExit(
            "missing compiled site assets in tools/site_assets/dist; "
            "run 'make site-assets' first (requires Node)"
        )
    dest = SITE / "assets"
    dest.mkdir(parents=True)
    for asset in list(ASSETS.glob("*.css")) + list(dist.glob("*.js")):
        shutil.copy2(asset, dest / asset.name)


def main(argv: list[str]) -> int:
    paper_dirs = argv[1:]
    if not paper_dirs:
        print("usage: build_site.py <paper-dir> [<paper-dir> ...]")
        return 2
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    _copy_site_assets()

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
