# Peter Todd, "Merkle Mountain Ranges" (OpenTimestamps)

- Author: Peter Todd (OpenTimestamps project).
- Source: `doc/merkle-mountain-range.md` in
  `opentimestamps/opentimestamps-server`,
  <https://github.com/opentimestamps/opentimestamps-server/blob/master/doc/merkle-mountain-range.md>.
- Accessed: 2026-07-19.
- Status: summarised from the source by a research agent (full page
  fetched); re-verify quoted claims against the page before citing.

## Core content

- An MMR is a collection of perfectly balanced binary trees
  ("mountains"). At size `n` the structure is a list of perfect trees
  whose leaf counts are the powers of two in the binary expansion of
  `n`. A perfect tree over `2^k` leaves has `2^(k+1) - 1` nodes.
- Nodes are stored in a flat, strictly append-only array; heights are
  derivable from positions. Suited to sequential disk storage.
- Append: append the leaf, then, whenever two subtrees of equal height
  become adjacent, append their parent; mountains merge right to left.
- Root digest by "bagging the peaks": collect the peak of each
  mountain and Merkle-hash them together. In OpenTimestamps a notary
  signs the bagged root.
- Key property: interior nodes are immutable once written. Appends
  only extend the array, never rewrite existing entries; the structure
  is deterministic given the base digests and their order.
- Storage: `n - 1` intermediate hashes for `n` leaves. Proof paths
  scale as `log2(n)`, like an ordinary Merkle tree.
- Which roots can vouch for a leaf is determined solely by the MMR's
  total width at the time the leaf was added.

## Understanding and use in the paper

- This is the original MMR description; cite for the definition, the
  append algorithm, immutability of interior nodes, peak bagging, and
  O(log n) proofs over a flat append-only array.
- Feeds Section 5 (MMR construction). The immutability property is the
  bridge to Section 6 (witness-update optimality): witnesses of old
  leaves only ever GROW by new peak-bagging context; the interior path
  never changes.
- The flat position-addressed array is the practical difference from
  the frontier-based Zcash IMT (Section 8): same immutability, other
  layout.
