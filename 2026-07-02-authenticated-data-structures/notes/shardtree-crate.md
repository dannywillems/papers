# shardtree (Rust crate)

- Author: Kris Nuttycombe, Jack Grigg, Sean Bowe et al. (zcash).
- Source: <https://docs.rs/shardtree/> and
  `shardtree/src/lib.rs` in
  <https://github.com/zcash/incrementalmerkletree>.
- Accessed: 2026-07-19.
- Status: summarised from the source by a research agent (docs and
  lib.rs fetched); re-verify before citing.

## Core content

- Tagline: "A space-efficient Merkle tree with witnessing of marked
  leaves, checkpointing & state restoration."
- Structure: a fixed-depth tree of depth `DEPTH` split horizontally at
  level `SHARD_HEIGHT` into:
  - shards: ordered fixed-height subtrees spanning levels
    `0..SHARD_HEIGHT`, each a `LocatedPrunableTree`, the unit of
    persistence;
  - the cap: a single `PrunableTree` over levels
    `SHARD_HEIGHT..DEPTH` whose leaves are the shard roots, caching
    upper-level hashes.
- Nodes may carry cached hash annotations; leaves carry
  `RetentionFlags` controlling pruning. `Retention` variants:
  - `Ephemeral`: pruned whenever its sibling is also an ephemeral
    leaf (merged away as soon as the sibling hash exists);
  - `Checkpoint`: the position is retained but the value may be
    pruned; has an id and a marking field for what survives if the
    checkpoint is dropped;
  - `Marked`: retained during pruning, only explicitly removable (the
    wallet's own notes whose witnesses must stay maintainable);
  - `Reference`: retained until overwritten by a node with one of the
    other retentions.
- Checkpoints bounded by `max_checkpoints`; older ones pruned
  automatically unless explicitly retained.
- Storage via the `ShardStore` trait; `MemoryShardStore` and
  `CachingShardStore` provided; DB-backed stores (SQLite in
  `zcash_client_sqlite`) implement the trait, one shard per row.
- Out-of-order insertion: leaves and nodes may be inserted in
  arbitrary order; the tree tracks the rightmost filled position as
  the frontier (unfilled positions left of it are missing, right of
  it are empty). Witness advancement inserts only the roots of the
  complete shards between the marked leaf and the frontier, not every
  intermediate leaf.
- Pruning keeps only hashes needed for Marked-leaf witnesses and
  checkpointed states; rewind restores any retained checkpoint.

## Understanding and use in the paper

- This is the production answer to the sparse-witness workload:
  append + sparse witnesses + pruning + out-of-order insertion +
  bounded checkpoints + DB-backed sharding, all at once.
- Cite for Section 8: retention-flag-driven pruning, the shard/cap
  split, shard-root-based witness fast-forwarding (the concrete
  mechanism that avoids per-leaf witness replay).
- Comparison hook for Section 9: witness update cost paid lazily at
  fast-forward time against shard roots, vs the eager per-append
  updates of the naive IMT.
