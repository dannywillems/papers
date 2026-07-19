# zcash/incrementalmerkletree (Rust workspace)

- Author: Zcash developers (Electric Coin Co. / zcash).
- Source: repository README and docs.rs,
  <https://github.com/zcash/incrementalmerkletree>.
- Accessed: 2026-07-19.
- Status: summarised from the source by a research agent (README and
  docs fetched); re-verify before citing.

## Core content

- Workspace tagline: "an append-only merkle tree implementation that
  remains constantly pruned, with incremental and fast-forwarding
  witnesses".
- Crates:
  - `incrementalmerkletree`: core types (`Position`, `Level`,
    `Retention`, the `frontier` module).
  - `shardtree`: the sharded prunable tree (see
    `shardtree-crate.md`).
  - `bridgetree`: an earlier compact representation based on
    "bridges" between witnessed positions.
  - `incrementalmerkletree-testing`.
- Frontier: the minimal data needed to keep appending to an
  append-only Merkle tree; the rightmost-path summary (left-sibling
  "ommer" hashes plus the rightmost leaf). Appending updates only the
  frontier, O(log n) amortized, never touching interior history (the
  same immutability property MMRs exploit).
- Witnesses are incremental (updated as leaves arrive) and
  fast-forwarding (advanced to the current tree state without
  replaying every intermediate leaf). Checkpoints allow rewinding the
  tree to an earlier block boundary (reorg support).

## Understanding and use in the paper

- Cite for: the maintained Rust implementation used by Zcash wallets;
  the frontier abstraction; incremental / fast-forwarding witness
  terminology; checkpoint-and-rewind as a first-class API requirement
  driven by chain reorgs.
- Feeds Section 8 (case study). The frontier is the fixed-depth
  analogue of the MMR peak set; making that correspondence explicit in
  the paper is worthwhile.
- bridgetree vs shardtree is a nice evolution story: bridges between
  witnessed leaves, replaced by shard/cap decomposition.
