# Agent guidelines

Instructions for AI coding agents (Claude Code, Copilot, Codex, ...)
working in this repository. Human contributors may ignore this file.

## Attribution (mandatory)

Any commit whose content (code, prose, or both) was generated or
substantially co-written by an AI agent MUST end its commit message
body with an attribution line naming the model or agent used:

```
With the assistance of Claude Fable 5.
```

Use the actual model or agent name; one line per agent involved. This
applies to every commit an agent creates, including changelog and
documentation commits.

The same transparency applies to generated text outside commits: when
an agent writes a substantial part of a paper, its README, or other
prose, say so with the same phrasing (for papers, an acknowledgement
note "Written with the assistance of <model>"; for documentation, the
commit attribution line is enough).

## Repository layout

- One directory per paper, named `YYYY-MM-DD-<slug>`, containing
  `main.tex`, `references.bib`, a `Makefile`, and optionally `code/`
  (Python, uv) and `lean/` (Lean 4, Lake).
- `tools/build_site.py` assembles the GitHub Pages site; it is generic
  and driven by conventions (`code/`, `lean/`, file extensions). Never
  add per-paper logic to it.
- `tools/site_assets/` holds the site's runner scripts: strict
  TypeScript in `src/`, compiled to `dist/` by `make site-assets`.

## Build and checks

Run the checks that cover what you touched before committing:

- LaTeX: `make -C <paper> build` (PDF), `make -C <paper> html`.
- Python: `make -C <paper>/code check` (ruff format, ruff, mypy
  strict, pytest).
- Lean: `lake build` inside `<paper>/lean`; no `sorry` may remain.
- Site assets: `make site-assets` (strict tsc; compiling is the type
  check).
- Site: `make site`, or `make assemble-site` if the HTML is already
  built.

## Conventions

- Changelog: every change is documented in `CHANGELOG.md`, and
  changelog edits go in their own dedicated commit
  (`CHANGELOG: <description>`).
- Keep the root `Makefile`'s `PAPERS` list and the CI workflows in
  sync when adding a paper.
- Wrap prose and commit messages at 80 characters. No emojis in
  commits.
- New dependencies (Python, npm, Lean) require explicit approval from
  the repository owner before being added.
