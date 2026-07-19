# Dahlberg, Pulls, Peeters, "Efficient Sparse Merkle Trees" (NordSec 2016)

- Authors: Rasmus Dahlberg, Tobias Pulls, Roel Peeters.
- Reference: Secure IT Systems, NordSec 2016, LNCS 10014,
  pp. 199-215, Springer, 2016. DOI: 10.1007/978-3-319-47560-8_13.
  Preprint: Cryptology ePrint Archive 2016/683,
  <https://eprint.iacr.org/2016/683>.
- Accessed: 2026-07-19. Local copy: `eprint/2016-683.pdf` (provided
  manually per the eprint rule).
- Status: digested by a research agent; the local PDF is available
  for first-hand verification and should be read whole before the
  sparse-Merkle-tree section is written.

## Core results

- Contributions (as stated): first complete, succinct, recursive
  definitions of a sparse Merkle tree (SMT) and its operations;
  caching strategies enabling space-time trade-offs; verifiable audit
  paths proving (non-)membership in practically constant time
  (< 4 ms with SHA-512/256) with a cache smaller than the underlying
  ADS; full concrete security in the multi-instance setting.
- SMT: an ADS based on a perfect Merkle tree of intractable size (one
  leaf per possible hash output, 2^N leaves for an N-bit hash),
  simulatable because almost all leaves are empty; default digests
  per level are precomputable. Definition 1 composes a data structure
  answering "is leaf k non-empty" with recursive root/audit-path
  computation over cached ("relative") digests.
- Non-membership proof = ordinary audit path showing the default
  (empty) digest at the key's position. History independence: the
  root depends only on the set, not insertion order.
- Caching strategies around BRANCHES (interior nodes both of whose
  children derive non-default digests): B cache stores every branch
  digest (exactly n - 1 digests for n non-empty leaves); B- cache
  probabilistically discards branches (capture probability p); B+
  cache stores branches plus children (bounded by 2n digests) so a
  discarded branch recomputes in O(1).
- Adversarial keys can force a near-perfect "branch spine", defeating
  naive dense-top-layer caching; branch-based caches bound recursive
  traversals by a constant. Experimental trade-off curves; no
  asymptotic lower bounds claimed.

## Understanding and use in the paper

- Feeds Section 3 (sparse/pruned Merkle trees) and Section 9 (the
  non-membership column: SMTs give non-membership proofs, MMRs do
  not).
- The key-value / revocation-style ADS alternative to append-only
  logs; history independence contrasts with the strictly ordered MMR.
