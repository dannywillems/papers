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
  `__main__`); embedded Lean files can be swapped in place for an
  embedded Lean4Web editor (the official Lean 4 web editor, which also
  provides the syntax highlighting) or opened in a new tab, with
  project-local imports inlined at build time. The runner scripts are
  strict TypeScript (`tools/site_assets/src/`), compiled with `tsc` by
  `make site-assets`.
- `AGENTS.md` principle: always use existing and standard tools
  (Lean4Web instead of a hand-written Lean highlight.js grammar).
- Paper `2026-07-02-authenticated-data-structures`: runnable
  demonstration module (`python -m ads`) printing digest, proof, and
  verification results; also the entry point for the in-browser Run
  button.
- `AGENTS.md`: guidelines for AI coding agents, including the
  mandatory "With the assistance of <model>" attribution in
  agent-generated commits and texts.
- `AGENTS.md`: three further conventions: per-source reading notes
  under each paper's `notes/` directory, no context compaction while
  reading a paper (warn instead), and eprint papers supplied manually
  by the human into a gitignored `eprint/` directory.
- Paper `2026-07-02-authenticated-data-structures`: `PLAN.md`, the
  living plan tracking the extension of the paper to the scope of
  issue dannywillems.github.io#535 (ADS models, sparse Merkle trees,
  accumulators, history trees, Merkle Mountain Ranges, the witness-
  update optimality result of eprint 2025/234, witness maintenance,
  the Zcash shardtree case study, comparison), plus 17 reading-note
  files under `notes/` covering the issue's sources; the note on
  eprint 2025/234 is verified against a first-hand read of the full
  paper.
- Paper `2026-07-02-authenticated-data-structures`: the two remaining
  Phase 0 reads done whole and first-hand from the local PDFs. The
  Dahlberg-Pulls-Peeters sparse-Merkle-tree note (eprint 2016/683) is
  upgraded to verified with the precise definitions, caches, and
  worst-case analysis; the Huffman-Merkle Tree placeholder is replaced
  by a full verified note on eprint 2026/1235, which enters the plan
  as a Section 9 related-work paragraph on workload-adaptive layouts.
  The published venue of eprint 2025/234 (CRYPTO 2025) is recorded in
  the plan's sources.

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
- Dependency updates (Dependabot round of 2026-07-19): GitHub Actions
  `actions/checkout` v4 to v7, `actions/upload-pages-artifact` v3 to
  v5, `actions/deploy-pages` v4 to v5, `astral-sh/setup-uv` v6 to v7,
  `tarides/changelog-check-action` v3 to v4; Python dev tools `ruff`
  to >=0.15.22, `mypy` to >=2.3.0, `pytest` to >=9.1.1; `typescript`
  5.9.3 to 7.0.2 (with the `rootDir` setting TS 7 requires).
