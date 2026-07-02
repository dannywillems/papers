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

## Reading online

Every paper is published as HTML at
<https://dannywillems.github.io/papers>. The LaTeX is converted with
`make4ht`, mathematics is rendered with MathJax, and each paper's source
code (Python and Lean) is embedded on its page in collapsible blocks.
Build the site locally with:

```bash
make site      # LaTeX -> HTML for every paper, then assemble site/
```

Open `site/index.html` in a browser. The site is deployed to GitHub
Pages by `.github/workflows/pages.yaml` on every push to `main`.

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
- `pages.yaml` - builds the HTML site and deploys it to GitHub Pages.
- `python.yaml` - runs the Python checks (ruff, mypy, pytest) for code
  subdirectories.
- `lean.yaml` - builds the Lean proofs (rejecting `sorry`) and runs the
  demo executable.
- `changelog.yaml`, `pr-hygiene.yaml`, `shellcheck.yaml` - repository
  hygiene.

Every CI step invokes a `make` target, so local and CI runs match. LaTeX
runs in a TeX Live container via `docker run` (the image ships no Node.js,
so it cannot be a job `container:`). Dependency updates are managed by
Dependabot (`.github/dependabot.yml`) for GitHub Actions and the Python
code.

## Adding a new paper

1. Create a directory `YYYY-MM-DD-<slug>/` with `main.tex`,
   `references.bib`, and a `Makefile` (copy an existing paper's
   `Makefile`).
2. Add the directory to `PAPERS` in the root `Makefile` (used by both the
   `build` and `site` targets).
3. Add a build step for it in `.github/workflows/build.yaml`.
4. If it has code or proofs, add the relevant CI steps and a Dependabot
   entry in `.github/dependabot.yml`.
5. Record the addition in `CHANGELOG.md` (in its own commit).
