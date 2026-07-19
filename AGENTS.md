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

## Always use existing and standard tools

Prefer an existing, standard, well-maintained tool over anything
hand-rolled, at every layer: build steps, site features, editor
integrations, linters. If a capability exists in a standard tool,
integrate that tool; do not re-implement a subset of it.

Example: Lean sources on the site are displayed and run through
Lean4Web (the official Lean 4 web editor), which brings its own syntax
highlighting; a hand-written highlight.js grammar for Lean was removed
in favour of it. The same reasoning applies to future needs: search
for the standard tool first, and only write custom code when no
suitable tool exists (say so in the commit message).

## Reading notes (mandatory)

Whenever you read a paper, specification, or substantial technical
source while working on a paper, dump the knowledge you extracted into
a dedicated markdown file named after that source, one file per
source, under the paper directory's `notes/` subdirectory (e.g.
`notes/szydlo-2004-merkle-tree-traversal.md`). Include:

- full bibliographic data (authors, title, venue, year, URL/DOI, the
  version actually read, access date);
- the core results with precise statements (theorems, bounds,
  algorithms), not paraphrases;
- your understanding: how the pieces fit, assumptions, limitations;
- everything judged useful for the paper: which sections it feeds,
  what to cite it for, quotable definitions, open questions;
- a status line: whether claims were verified against the source
  itself or only summarised second-hand.

Update the note when the source is re-read or when a claim is
verified. The paper's `PLAN.md` references these notes; keep the two
consistent.

eprint papers: papers on eprint.iacr.org cannot be accessed by AI
agents. When an eprint paper must be read, ask the human to download
it manually and to place it in the paper directory's `eprint/`
subdirectory (e.g. `2026-07-02-authenticated-data-structures/eprint/`),
then read it from there. NEVER commit the `eprint/` directory (it is
gitignored); we respect the eprint distribution rules. Reading notes
about an eprint paper (your own words, under `notes/`) are fine to
commit; the PDF itself is not.

Context integrity while reading: NEVER let the agent context be
compacted while reading a paper. The whole paper must fit in the
context window; if it does not fit, STOP and warn the human instead of
reading it partially or from a summary. Compaction while a source is
in flight is how hallucinated citations happen. More generally, ask
the human before compacting the context at all.

## Per-paper AGENTS.md and human-only sections

A paper directory may contain its own `AGENTS.md` with
paper-specific guidance. Any section marked as human-only (e.g.
"Human section") must NEVER be modified by an agent; it is the
authoritative statement of the paper's motivation and scope. Read it
before working on that paper and keep `PLAN.md` consistent with it.

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
