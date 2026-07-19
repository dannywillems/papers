# Changelog

All notable changes to this repository are documented in this file.
Each paper lives in its own dated directory; entries reference the paper
they concern.

## [Unreleased]

### Added

- Repository scaffolding: root `Makefile` building every paper in
  sequence, `.editorconfig`, `.gitignore` for LaTeX, Python, and Lean
  artifacts.
- Paper `2026-07-02-authenticated-data-structures`: an authenticated
  append-only Merkle log. Includes the LaTeX source (`main.tex`), a
  Python reference implementation (`code/`), and a Lean 4 formalisation
  (`lean/`) proving completeness, soundness, and the proof-size bound
  with no `sorry`.

- HTML site (`make site`, `tools/build_site.py`): every paper converted
  from LaTeX to HTML with `make4ht` (MathJax for mathematics), its source
  code embedded in collapsible blocks, and a landing page listing all
  papers. Deployed to GitHub Pages at
  <https://dannywillems.github.io/papers>.

- Runnable code on the site, generic for every paper: embedded Python
  files get a Run button and execute in the browser on Pyodide (pinned
  CDN version; test files run under pytest, other files as
  `__main__`); embedded Lean files get a "Run in Lean 4 playground"
  button opening live.lean-lang.org with project-local imports inlined
  at build time. The runner scripts are strict TypeScript
  (`tools/site_assets/src/`), compiled with `tsc` by `make site-assets`.
- Lean syntax highlighting on the site via a custom highlight.js
  grammar (declarations, tactics, nested block and doc comments,
  attributes, `#`-commands).
- Paper `2026-07-02-authenticated-data-structures`: runnable
  demonstration module (`python -m ads`) printing digest, proof, and
  verification results; also the entry point for the in-browser Run
  button.
- `AGENTS.md`: guidelines for AI coding agents, including the
  mandatory "With the assistance of <model>" attribution in
  agent-generated commits and texts.

### Fixed

- Site rendering: teach MathJax the papers' custom `\newcommand` macros
  (they were showing as red literal text), run biber on make4ht's own
  control file so the HTML bibliography is populated, rewrite make4ht's
  `main.html#` links to the served `index.html` so citations and
  cross-references are clickable, give cleveref a name for the custom
  `construction` environment (fixed a `??` reference), and replace
  `\textsc` in the algorithm with a MathJax-supported command.
- Add a light/dark theme with a persisted toggle so text is legible
  regardless of the browser's colour preference.

### Infrastructure

- CI: sequential paper build, GitHub Pages deploy, Python checks (ruff,
  mypy, pytest), Lean build and demo run, changelog hygiene, PR hygiene,
  and shellcheck. LaTeX runs in a TeX Live container via `docker run`.
- Dependabot for GitHub Actions and the Python code.
- CI: site-assets workflow compiling the TypeScript runner scripts with
  strict `tsc` on every PR; the Pages deploy compiles them on the
  runner (Node 24) before the TeX Live container assembles the site
  (`make site-assets` / `make assemble-site` split).
