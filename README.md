# Papers

Research papers in mathematics and computer science, with accompanying
code and, where relevant, machine-checked proofs. Everything is written
in English.

## Layout

Each paper lives in its own directory whose name starts with the date it
was created, `YYYY-MM-DD-<slug>`. Several papers may be in progress at
once. A paper directory contains at least a LaTeX project (`main.tex`,
`references.bib`, a `Makefile`), and optionally a `code/` subdirectory
(implementation) and a `lean/` subdirectory (formal proofs).

Current papers:

- [`2026-07-02-authenticated-data-structures`](2026-07-02-authenticated-data-structures/)
  - Authenticated append-only Merkle log: paper, Python reference
    implementation, and a Lean 4 formalisation of its properties.

## Building

The root `Makefile` builds every paper listed in its `PAPERS` variable,
one after another:

```bash
make build      # build every paper's PDF, sequentially
make clean      # clean every paper's auxiliary files
```

To build a single paper, use its own `Makefile`:

```bash
make -C 2026-07-02-authenticated-data-structures build
```

## Continuous integration

Workflows live in `.github/workflows/`:

- `build.yaml` - builds each paper directory in turn (listed explicitly,
  one step per paper).
- `python.yaml` - runs the Python checks (ruff, mypy, pytest) for code
  subdirectories.
- `lean.yaml` - builds the Lean proofs (rejecting `sorry`) and runs the
  demo executable.
- `changelog.yaml`, `pr-hygiene.yaml`, `shellcheck.yaml` - repository
  hygiene.

Every CI step invokes a `make` target, so local and CI runs match.

## Adding a new paper

1. Create a directory `YYYY-MM-DD-<slug>/` with `main.tex`,
   `references.bib`, and a `Makefile` (copy an existing paper's
   `Makefile`).
2. Add the directory to `PAPERS` in the root `Makefile`.
3. Add a build step for it in `.github/workflows/build.yaml`.
4. If it has code or proofs, add the relevant CI steps.
5. Record the addition in `CHANGELOG.md` (in its own commit).
