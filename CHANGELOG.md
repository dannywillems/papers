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

### Infrastructure

- CI: sequential paper build, Python checks (ruff, mypy, pytest), Lean
  build and demo run, changelog hygiene, PR hygiene, and shellcheck.
