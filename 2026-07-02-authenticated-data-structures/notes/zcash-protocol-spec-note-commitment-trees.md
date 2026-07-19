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

## Nullifiers and double-spend detection (the used-set side)

The note-commitment tree is only the MEMBERSHIP half of Zcash's state.
Double-spend prevention runs on the dual NON-membership structure, the
nullifier set. Mechanism (grounded in the spec's spend description and
verified against Bowe-Miers eprint 2025/2031, which quotes the current
behaviour directly):

- Every note has a unique NULLIFIER, computed deterministically from
  the note and a spender-only secret (a keyed pseudo-random function;
  in Sapling/Orchard the nullifier deriving key is part of the
  spending key material). It reveals nothing about which note it
  belongs to.
- A shielded SPEND publicly REVEALS its note's nullifier. The
  zero-knowledge proof enforces two things at once: the spent note's
  commitment EXISTS in the tree (a valid Merkle path to a recent
  anchor) AND the revealed nullifier was correctly derived for that
  note, all without revealing the note or its position.
- Validators MAINTAIN THE NULLIFIER SET as consensus state: the set of
  all nullifiers ever revealed. A transaction is rejected as a
  double-spend if any nullifier it reveals is already in the set (or
  is duplicated within the same block/transaction, catching
  concurrent double-spends). Verified quote (Bowe-Miers): validators
  "remember all of the nullifiers seen before and reject payments as
  invalid if they reveal a previously-seen nullifier." An accepted
  spend's nullifier is then ADDED to the set.
- Determinism is what makes it work: spending the same note twice
  yields the same nullifier, so the duplicate is caught; the keyed
  PRF keeps the nullifier unlinkable to the note, so privacy holds.
- Cost consequence: the nullifier set must be kept ONLINE and
  complete (unlike ordinary transaction history, which can be
  archived), and it grows linearly with all spends ever. This is the
  used-set growth problem (P3 in
  `notes/color-model-reformulation.md`) and the motivation for
  evolving nullifiers + oblivious synchronization
  (`notes/bowe-miers-2025-a-note-on-notes.md`).

## Understanding and use in the paper

- The protocol grounding for Section 8, in one sentence: each shielded
  spend requires a depth-32 Merkle path to a recent anchor, so wallets
  must keep membership witnesses for their own notes current as the
  global tree grows.
- Cite for the append-only framing at consensus level and the fixed
  depth that pins the implementation space (no MMR digest possible at
  consensus without a circuit change).
- Use the nullifier-set mechanism above as the concrete instance of
  the paper's non-membership / used-set side: membership (note
  commitments, proven by inclusion) vs non-membership (nullifiers,
  checked by brute retention), the duality the color model unifies.
