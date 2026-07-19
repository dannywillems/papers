# Synthesis: witness maintenance cost across the sources

- Author: own synthesis over the practice sources (see the sibling
  notes); not a citable source, a working note.
- Date: 2026-07-19.

## The through-line

- Baseline (Sapling-era, protocol-level): witness updates require
  processing every appended commitment. The Orchard Book states a
  receiver must update its witness with every subsequent commitment in
  order. Per-note cost is O(1) amortized hashes per append, but total
  wallet work is O(appends x tracked notes) unless witnesses share
  structure.
- bridgetree reduced sharing overhead via bridges between witnessed
  leaves; shardtree replaces it with the shard/cap decomposition:
  fast-forwarding a marked leaf's witness to a recent checkpoint
  inserts only complete shard roots between the marked leaf and the
  frontier, and out-of-order insertion lets synced subtree roots
  substitute for leaf-by-leaf replay.
- The MMR line (Todd, Grin) achieves the same key property (immutable
  interior nodes under append, O(log n) proofs) with a flat
  position-addressed array and peak bagging instead of a fixed-depth
  frontier; Grin adds position-prefixed hashing and sibling-driven
  pruning.
- Zcash cannot adopt an MMR root directly: circuit-verified anchors
  fix a constant-depth-32 path, so the fix landed in the
  implementation layer (per the Orchard Book rationale), not the
  consensus structure.

## Open questions for the paper

- Make precise the correspondence frontier <-> peak set (fixed-depth
  IMT vs MMR): same information, different addressing. Candidate for
  a formal remark in Section 5/8.
- How the eprint 2025/234 lower bound (theory digest pending) reads
  against the shardtree lazy fast-forward: does deferring witness
  updates to spend time change the total-update count, or only its
  schedule? Likely only the schedule; check against the bound's model.
