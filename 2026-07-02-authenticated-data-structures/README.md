# Authenticated Data Structures

A note formalising an authenticated append-only log built from a binary
Merkle tree, with logarithmic-size membership proofs, paired with a
tested Python reference implementation.

## Contents

- `main.tex`, `references.bib` - the paper source (build with `make build`).
- `code/` - the Python `ads` package implementing the construction, with
  its own `Makefile` and test suite.
- `lean/` - a Lean 4 formalisation proving completeness, soundness, and
  the proof-size bound (no `sorry`), with a runnable demo.

## Build the paper

```bash
make build     # latexmk -> main.pdf
make clean      # remove auxiliary files
```

## Run the code checks

```bash
make -C code check   # Python: format, lint, typecheck, tests
make -C lean check   # Lean: no sorry, build, run demo
```
