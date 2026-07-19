# Grin documentation, "Merkle Mountain Ranges"

- Author: Grin developers (mimblewimble/grin project).
- Source: `doc/mmr.md` in `mimblewimble/grin`,
  <https://github.com/mimblewimble/grin/blob/master/doc/mmr.md>.
- Accessed: 2026-07-19.
- Status: summarised from the source by a research agent (full page
  fetched); re-verify quoted claims before citing. NOTE: the page does
  not itself spell out Merkle proof construction; do not cite it for
  proof algorithms.

## Core content

- Describes the MMR as strictly append-only and as "a single binary
  tree that would have been truncated from the top right".
- Position numbering: nodes numbered by post-order insertion position,
  stored flat together with their heights; the whole shape is fully
  described by its size; parent/sibling/height computed by binary
  arithmetic on positions.
- Elements are added left to right, "adding a parent as soon as 2
  children exist"; subtrees are always perfectly balanced, no
  rebalancing ever.
- Hashing is position-salted: leaf = Blake2b(pos || data), parent =
  Blake2b(pos || left || right). The position prefix is domain
  separation ("to avoid collisions").
- No single root by construction. Root = bag the peaks: leftmost peak
  always at a position of the form `2^n - 1`; peaks hashed
  iteratively from the right, using the total MMR size as prefix.
- Pruning: a spent leaf's hash can be removed; removal propagates to a
  parent only when the sibling is also gone. Large fractions of the
  MMR can be dropped while remaining hashes still authenticate the
  rest (PMMR: prunable MMR).

## Understanding and use in the paper

- Cite for: a production MMR deployment (Grin's output/kernel/
  rangeproof sets), position-numbering arithmetic, position-prefixed
  hashing as an alternative domain-separation style to our 0x00/0x01
  tags, the concrete peak-bagging formula, and sibling-driven pruning
  inside an append-only structure.
- Feeds Section 5 (MMR construction; the truncated-tree view
  complements Todd's list-of-mountains view) and Section 9 (pruning
  column in the comparison).
