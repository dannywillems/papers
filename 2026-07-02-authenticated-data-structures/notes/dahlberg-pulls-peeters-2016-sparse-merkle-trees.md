# Dahlberg, Pulls, Peeters, "Efficient Sparse Merkle Trees" (NordSec 2016)

- Authors: Rasmus Dahlberg, Tobias Pulls (Karlstad University), Roel
  Peeters (KU Leuven, ESAT/COSIC & iMinds).
- Full title: "Efficient Sparse Merkle Trees: Caching Strategies and
  Secure (Non-)Membership Proofs".
- Reference: Secure IT Systems, NordSec 2016, LNCS 10014,
  pp. 199-215, Springer, 2016. DOI: 10.1007/978-3-319-47560-8_13.
  Preprint: Cryptology ePrint Archive 2016/683,
  <https://eprint.iacr.org/2016/683>.
- Accessed: 2026-07-19. Local copy: `eprint/2016-683.pdf` (provided
  manually per the eprint rule); 16 pages.
- Status: VERIFIED. Read whole first-hand from the local PDF on
  2026-07-19; every claim below checked against the full text.

## Problem and context

- Motivation: Certificate Transparency (RFC 6962) gives verifiable
  append-only logs (membership + consistency proofs) but cannot prove
  absence: "the log is both chronological and append-only, effected
  certificates can neither be removed nor can the absence of a
  revocation certificate be proven efficiently". Revocation
  Transparency (Laurie-Kasper 2012) needs an ADS with efficient
  non-membership proofs; the SMT is their generalisation of the
  Laurie-Kasper proposal, which they judge "incomplete" (it re-derives
  subtree digests over and over; solved here by relative information).
- Two known routes to non-membership proofs: (i) lexicographically
  sorted Merkle trees (binary search + audit path; requires balancing
  rules, and history independence is NOT guaranteed, e.g. a red-black
  tree); (ii) the SMT route taken here.

## The SMT

- A perfect Merkle tree of intractable size: one distinct leaf for
  every possible output of a cryptographic hash function H with
  digests of N := 2*lambda bits, hence 2^N leaves at all times. The
  hash of a key k determines its leaf ell = H(k); the leaf's attribute
  is a_1 if k is a member and the shared default attribute a_0
  otherwise. (Non-)membership of k is proven by an ordinary audit path
  for leaf H(k).
- Tractability comes from sparseness: almost all leaves are empty, and
  every empty subtree rooted at height h derives the same
  precomputable default digest (d*_0 = H(a_0), d*_h =
  H(d*_{h-1} || d*_{h-1})). Only nodes whose digest depends on
  existing keys need processing.
- History independence (citing Naor-Teague): a set of keys produces a
  deterministic root digest regardless of insertion/removal order.
- Earlier proposals: Bauer's explicitly pruned tree (non-empty
  attributes elevated through ancestors; needs per-subtree index
  bookkeeping, memory-heavy unless keys are evenly spread);
  Laurie-Kasper's simulation over a key collection (adopted and
  completed here).

## Definitions (verbatim)

- Definition 1: "A simulated SMT is the composition of (i) a data
  structure D containing unique keys k, and (ii) a collection of
  cached digests, referred to as the relative information delta. Both
  structures define operations for insertion, removal, and look-up;
  D also supports splitting, i.e., dividing it in two based on a key."
  There is no explicit tree: every key in D maps to its associated
  subtrees recursively. A traversal tracks a base (left-most leaf of
  the current subtree, all-zeros initially, updated by setting bit
  j = N - h on right traversals) and a split index s (left-most leaf
  of the right subtree; an upper-exclusive / lower-inclusive bound for
  the keys of the left / right subtree, used to split D).
- Definition 2: "A branch is an interior node in a Merkle tree, for
  which both of the two children derive non-default digests."

## Recurrences (Figure 5)

Complete recursive definitions parameterised by height h and base b:

- (1) xi: default digests (leaf hash LH of a_0 at h = 0, interior
  hash IH of two copies one level down otherwise).
- (2) R: root digest of a subtree; base cases are cached relative
  information delta^h_b, a default digest when D is empty, and a leaf
  hash when |D| = 1 at h = 0; otherwise recurse on D split at s.
- (3) A: audit path for key k: at each level, collect the sibling's
  digest via R on the half not containing k, recurse into the half
  containing k (list concatenation).
- (4) B: reconstruct the root digest from an audit path P, key k, and
  attribute a in {a_0, a_1}.
- (5) U: batch update of a key subset K (all set to a; covers insert
  and remove), recomputing digests bottom-up and invoking the cache
  routine C at every interior node so delta stays current.

An audit path always has exactly N sibling digests (size fixed by the
tree height, independent of n); discarding default digests plus an
N-bitmap yields a "sparse audit path".

## Caching strategies (the B / B- / B+ caches)

The naive strategy "cache the top ceil(log n) + 1 layers" captures the
dense part in the average case (H is uniform, so non-empty leaves
spread evenly) but is defeated by an adversary who selects keys that
clump below the dense threshold; the paper therefore caches around
branches (Definition 2):

- B cache: capture every branch digest. Invariant: exactly n - 1
  digests for n non-empty leaves (all but the first insertion yield a
  single new branch).
- B- cache: discard f(n) branches from B, trading memory for
  recomputation. Examined instance: keep a branch with probability p
  (f(n) roughly n(1 - p)); other variants mentioned: skip every other
  layer, cap the number ignored. For worst-case protection f(n) must
  be constant or unpredictable to the adversary.
- B+ cache: capture branches AND their children (covers the entire
  dense part, since the dense region also spans layer ceil(log n)+1);
  memory bounded by 2n by discarding branches, whose digests re-derive
  in constant time from the cached children.
- Cache routine C: on computing an interior digest, if both children
  are non-default, cache the new branch and delete the previous one if
  applicable; extends from B to B- and B+, and the strategies can be
  mixed over a tree's lifetime (start B+, degrade to B, then B- as
  memory tightens). In principle B- is a subset of B is a subset of
  B+.

## Adversarial worst-case analysis (Section 5.3)

- With merely N keys an adversary can force an almost perfect "branch
  spine" (Figure 7): membership proofs for the spine leaves must
  recompute most non-default digests, since the siblings hang off the
  spine and are not branches.
- The bound: when a sibling's digest is requested it is either default
  (constant time) or derived by one traversal down to the nearest
  branch or leaf; hence, regardless of how the adversary selects keys,
  AT MOST N traversals are needed per audit path (one per layer) for
  B, and similarly for B+ (children of branches are cached). For B-
  the number of traversals is bounded by f(n). Worst-case efficiency
  actually improves as the tree grows (new insertions yield additional
  branches to stop at). The same analysis covers updates, since (3)
  and (5) invoke (2) once per layer.
- The paper claims no asymptotic lower bounds; the aim is that audit
  path generation and single-key updates reduce to the cost of the
  underlying split operation, with the number of extra traversals
  bounded as above.

## Security (Section 5)

- Lemma 1: "The security of an audit path reduces to the collision
  resistance of the underlying hash function H." (Stated for a single
  SMT with a fixed hash function, where audit-path size is fixed by N
  so leaves and interior nodes are distinguishable; proof "follows
  directly" from Merkle and Blum et al.)
- Multi-instance setting (inspired by Katz's analysis of hash-based
  signatures and by CONIKS): many SMTs attacked at once; the goal is
  full lambda-bit security per instance with N = 2*lambda-bit digests.
- CONIKS Merkle prefix tree encodings compared (their Eqs. 6-8):
  constants C_empty and C_leaf separate node types, a tree-wide
  constant C_tw separates trees, and unique location encodings (index,
  depth) separate positions; but full lambda-bit security across
  versions of one MPT requires a fresh C_tw per update, i.e.
  recomputing the whole tree from scratch.
- Their secure SMT encoding (Eqs. 9-10): LH*_b(a) := H(C_tw) if
  a = a_0, else H(C_tw || b); IH^h_b(d_l, d_r) := H(d_l || d_r) if
  both children default, else H(d_l || d_r || b || h). Unique
  identifiers (base b, height h) only in NON-EMPTY subtrees; putting
  them in empty subtrees would destroy the default digests and thus
  sparseness. The empty-node encoding moves into the non-empty parent;
  height is needed because the base alone is ambiguous on left
  traversals. Like CONIKS, C_tw is reused across versions, so
  cross-version attacks on one tree are out of scope.

## Performance (Section 6)

- Proof-of-concept in Go (github.com/pylls/gosmt, Apache 2.0),
  SHA-512/256 (so 2^256 leaves), D with logarithmic split, delta as a
  hash table; Intel i7-4790 3.60 GHz, 2x8 GB DDR4.
- Size at 2^20 keys: hash treap 960 MiB, B+ 512 MiB, B 256 MiB,
  B-(p=0.5) 128 MiB; a hash treap is roughly 8x a B-(0.5) cache.
- Audit-path generation: hash treap 0.003 ms (explicit structure);
  B and B+ consistently < 1 ms regardless of size; B- with p > 0.6
  expected < 4 ms, p = 0.5 erratic (this is the abstract's
  "practically constant time (< 4 ms)" claim).
- Updates scale O(m log n) for m keys among n; B+ needs < 20 ms to
  update 256 keys at n = 2^20 vs 9.5 ms for the hash treap, at half
  the treap's memory.

## Related work recorded by the paper

- Google's three transparency ADS categories: verifiable logs (CT),
  verifiable maps (SMT-based, proposed in RT), and verifiable
  log-backed maps (combination; full audits can ensure complete
  correct behavior).
- PADs (persistent authenticated dictionaries) support queries to
  past versions too; an SMT plus persistency (path copying,
  Sarnak-Tarjan versioned nodes) yields a PAD.
- CONIKS (MPT + verifiable unpredictable function for indices);
  Balloon (append-only, combines a history tree and a hash treap);
  hash treaps store attributes in every node and leak via audit
  paths, need exactly n nodes and probabilistic balance; certificate
  revocation trees and 2-3 tree successors (full recompute problem).
  An SMT is NOT for Bitcoin-style block Merkle trees (no
  non-membership needed there).
- The work extends Dahlberg's bachelor's thesis (Karlstad, 2016)
  with batch-update/reconstruction recursions, branch caching, the
  multi-instance security evaluation, and the Go implementation.

## Understanding and use in the paper

- Feeds Section 3 (sparse/pruned Merkle trees) and Section 9 (the
  non-membership column: SMTs give non-membership proofs, MMRs do
  not).
- The key-value / revocation-style ADS alternative to append-only
  logs; history independence contrasts with the strictly ordered MMR.
- Quotable precise items: Definitions 1-2 (verbatim above), Lemma 1,
  the B / B- / B+ definitions with their exact memory invariants
  (n - 1, roughly n*p, at most 2n), the branch-spine worst case with
  its at-most-N-traversals bound, and the secure encoding Eqs. 9-10.
- Caveats for citation: "practically constant time < 4 ms" is an
  empirical claim about B- caches at p > 0.6 on their hardware, not
  an asymptotic bound; the multi-instance encoding does not protect
  across versions of a single tree (C_tw reused); no lower bounds are
  claimed anywhere.
