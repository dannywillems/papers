# Zcash Protocol Specification, note commitment trees

- Authors: Daira-Emma Hopwood, Sean Bowe, Taylor Hornby, Nathan
  Wilcox.
- Source: "Zcash Protocol Specification", version v2026.7.0 [NU6.2],
  sections 3.8 (Note Commitment Trees) and 5.3 (Constants),
  <https://zips.z.cash/protocol/protocol.pdf>.
- Accessed: 2026-07-19.
- Status: agent-verified against the spec text (version above);
  re-verify section numbers when citing.

## Core content

- Section 3.8: "A note commitment tree is an incremental Merkle tree,
  of fixed depth defined by each shielded protocol, used to store
  note commitments that JoinSplit transfers or Spend transfers or
  Action transfers produce. ... unlike the UTXO set, it is not the job
  of this tree to protect against double-spending, as it is
  append-only."
- Constants (5.3): MerkleDepth Sprout = 29, Sapling = 32,
  Orchard = 32.
- A root ("anchor") is associated with each treestate; consensus
  forbids exceeding the 2^MerkleDepth leaf capacity.
- Spend circuits enforce Merkle path validity: for Orchard,
  "(path, pos) is a valid Merkle path of depth MerkleDepth^Orchard"
  from the note commitment to the anchor rt; anchors must refer to
  some earlier block's final treestate.

## Understanding and use in the paper

- The protocol grounding for Section 8, in one sentence: each shielded
  spend requires a depth-32 Merkle path to a recent anchor, so wallets
  must keep membership witnesses for their own notes current as the
  global tree grows.
- Cite for the append-only framing at consensus level and the fixed
  depth that pins the implementation space (no MMR digest possible at
  consensus without a circuit change).
