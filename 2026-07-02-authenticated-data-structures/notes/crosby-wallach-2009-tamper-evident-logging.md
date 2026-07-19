# Crosby, Wallach, "Efficient Data Structures for Tamper-Evident Logging" (USENIX Security 2009)

- Authors: Scott A. Crosby, Dan S. Wallach.
- Reference: Proceedings of the 18th USENIX Security Symposium,
  pp. 317-334, USENIX Association, 2009.
  <https://www.usenix.org/legacy/event/sec09/tech/full_papers/crosby.pdf>.
- Accessed: 2026-07-19 (full proceedings PDF via archive mirror).
- Status: digested by a research agent from the full PDF; re-verify
  before citing.

## Core results

- Introduces the HISTORY TREE: a versioned append-only Merkle binary
  tree over log events X_0..X_i; each append produces a new signed,
  version-numbered commitment C_i fixing the entire history to date.
- Two proof types, both logarithmic (prior hash-chain schemes needed
  linear scans):
  - membership proofs: event i is fixed by commitment C_j (i <= j);
  - incremental proofs: commitments C_i and C_j make consistent
    claims about the shared past.
  Proofs are pruned trees with at most 2d frozen nodes, d = depth,
  so O(log n).
- Concrete numbers: an 80M-event log needs about a 3 KB proof where a
  hash chain would need an ~800 MB trace; prototype 1,750 events/sec
  with signing on one core, 10,500 events/sec with signatures
  offloaded (~1.1 TB/week).
- Extras: MERKLE AGGREGATION (attributes aggregated up the tree,
  authenticated predicate queries) and SAFE DELETION (provably delete
  only events matching an agreed predicate, no extra trusted party).
- Model: untrusted logger (sole author), trusted-but-forgetful
  clients who insert events and gossip commitments to auditors,
  auditors who challenge with proof requests; goal is tamper
  DETECTION. Formal five-tuple semantics (Section 2.3): H.Add,
  H.Incr.Gen, H.Membership.Gen, P.Incr.Vf, P.Membership.Vf.
- Security property (Historical Consistency, in substance): if a
  valid incremental proof links C_j and C_k (j <= k) and valid
  membership proofs fix X_i' in C_j and X_i'' in C_k (i <= j), then
  X_i' = X_i''.

## Understanding and use in the paper

- Feeds Section 4. This is the direct ancestor of RFC 6962
  consistency proofs; cite for the origin of logarithmic consistency
  ("incremental") proofs, the historical-consistency game, and the
  logger/clients/auditors deployment model with commitment gossip.
- Merkle aggregation and safe deletion are ADS features beyond
  membership worth one sentence each.
