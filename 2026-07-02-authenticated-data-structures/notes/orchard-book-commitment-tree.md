# The Orchard Book, "Commitment tree" (design chapter)

- Author: Zcash / Orchard developers.
- Source: <https://zcash.github.io/orchard/design/commitment-tree.html>.
- Accessed: 2026-07-19.
- Status: summarised from the source by a research agent (page
  fetched); re-verify before citing.

## Core content

- Orchard keeps Sapling's structure: a single global commitment tree
  of fixed depth 32. Note commitments are appended in-order from each
  block; valid anchors are the roots at block boundaries.
- The Merkle hash `MerkleCRH^Orchard` is instantiated with Sinsemilla
  (Sapling used the Bowe-Hopwood Pedersen hash).
- The uncommitted (empty) leaf value is 2, chosen because Orchard note
  commitments are x-coordinates of Pallas points and `2^3 + 5` is not
  a square in either Fp or Fq, so 2 can never be a real commitment.
- Witness-cost statement (explicit in the book): since commitments are
  appended in-order, a wallet that receives a note must afterwards
  update its incremental witness with every subsequent commitment, in
  order, in that block and every later block. Per tracked note this is
  O(1) amortized hash work per append, but it requires touching every
  appended commitment.
- Design rationale: hierarchical bundle/block/global trees were
  considered and rejected as too large a change from Sapling; the
  judgement was that the incremental Merkle tree implementation could
  be improved instead. That path was later realized by shardtree: keep
  the consensus structure, fix the implementation layer.

## Understanding and use in the paper

- Feeds Section 8. Two key citations: the explicit witness-update
  workload statement (the wallet-side cost the optimality result
  speaks to), and the keep-structure/fix-implementation design
  decision.
- Also worth noting in the paper: Zcash cannot adopt an MMR digest
  directly because circuit-verified anchors fix a constant-depth-32
  path; the improvement must happen in the implementation layer. (Own
  synthesis, consistent with this source; do not attribute to the
  book.)
