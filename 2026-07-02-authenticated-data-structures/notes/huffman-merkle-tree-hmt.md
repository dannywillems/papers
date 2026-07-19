# Shangguan, Yaish, Malkhi, "Authenticated Data Structures for Dynamic Workloads" (the Huffman-Merkle Tree)

- Authors: Ziheng (Tom) Shangguan (UCSB), Aviv Yaish (Yale University,
  IC3, Complexity Science Hub Vienna), Dahlia Malkhi (UCSB).
- Reference: Cryptology ePrint Archive 2026/1235,
  <https://eprint.iacr.org/2026/1235>. 34 pages (20 main text +
  references + appendices A-C).
- Accessed: 2026-07-19. Local copy: `eprint/2026-1235.pdf` (provided
  manually per the eprint rule).
- Status: VERIFIED. Read whole first-hand from the local PDF on
  2026-07-19 (main text, references, and appendices); the claims below
  are checked against the full text. This resolves the "Huffman-Merkle
  Tree (HMT)" term from the issue comment.

## Problem

- In a balanced binary Merkle tree (MT) with N leaves, inclusion
  proofs contain log N hashes regardless of how often an element is
  accessed; the same frequency-independence holds for Ethereum's
  Merkle Patricia Trie (MPT). Real workloads are skewed (Zipfian) and
  the access distribution CHANGES over time.
- The paper's metric is therefore AVERAGE-CASE cost: each element's
  proof and update cost weighted by its access frequency, in concrete
  units (hash-compression invocations / hashed input bytes and
  membership-proof bytes).
- Static case is solved: with known frequencies, the optimal static
  tree is a Huffman code. Prior dynamic work rebuilds the whole
  structure when the distribution changes (Mizrahi, Koren,
  Rottenstreich, Cassuto, "Traffic-Aware Merkle Trees", IEEE/ACM ToN
  2024); the restructuring cost was not accounted for in the same
  concrete units. Research question: an ADS that adapts to evolving
  access frequencies while explicitly accounting for restructuring
  cost.

## Definitions

- Definition 2.1 (ADS interface) over a dataset D of key-value pairs:
  Put(D, k, v) -> D'; Delete(D, k) -> D'; Commit(D) -> c;
  Get(D, k) -> {v, bottom}; GetProof(D, k) -> {pi, bottom};
  Verify(c, k, v, pi) -> {0, 1}, with Verify(c, k, v, pi) = 1 iff
  (k, v) in D when pi and c are honestly produced.
- HuffMHT (from Munoz, Forne, Esparza, Rey, TrustBus 2005): a Huffman
  tree built over element access weights, elements at leaves,
  child-hash commitments at internal nodes, root as commitment. Proof
  depth for x equals its Huffman code length L(x), so the Huffman
  objective sum_x p(x) L(x) IS the access-weighted expected proof
  depth. The basic HuffMHT layout is static; the paper is explicit
  that HMT's novelty is not the Huffman-shaped tree itself but the
  dynamic authenticated-map design around it.
- Baselines: Ethereum MPT (hexary nibble paths; proofs contain whole
  encoded trie nodes, not one sibling hash per level, hence large
  witnesses; cited as a DoS vector) and UBT (EIP-7864 Unified Binary
  Tree: one 32-byte key-value space, 256-value stems, binary internal
  nodes; proof follows the binary path of the first 248 bits of the
  31-byte stem, then authenticates within the stem subtree).

## The HMT construction

Two-tier architecture plus an overflow tree:

- Cold tier: a balanced binary MT storing infrequent AND newly
  inserted elements (logarithmic update paths in the cold-tier size).
- Hot tier: selected high-frequency elements in a HuffMHT (short
  access-weighted proofs and less path rehashing).
- Why the cold tier is a plain MT: a single HuffMHT gives short paths
  to hot items by giving LONG paths to cold ones; the deepest HuffMHT
  leaf can have depth N - 1 versus ceil(log2 N) balanced, a worst-case
  depth ratio of N / log2 N (their Figure 6). Cold and new elements
  are kept out of the Huffman tail on purpose.
- Periodic-rebuild HuffMHT (the hot tier): a base HuffMHT for elements
  already absorbed into the optimized layout, plus an overflow MT for
  newly promoted / not-yet-absorbed elements; base and overflow are
  key-disjoint. Value updates only mark the ancestor path dirty
  (reflected at the next root computation); layout changes are
  deferred to rebuild boundaries. Exported root: H(base-overflow ||
  r_base || r_overflow) when the overflow tree is non-empty, else
  H(base-only || r_base); proofs carry a component tag. At a rebuild
  boundary the base is rebuilt from the latest frequency counts and
  the overflow tree is cleared. So the hot HuffMHT is never
  restructured per access.
- Global commitment over T tier roots:
  Root_global = H(Root_0 || Root_1 || ... || Root_{T-1}).

## Incremental layout maintenance (Section 3)

- Complete rebuild: linear in the number of elements per change.
- Incremental (pair-swap) strategy: if only relative frequency RANKS
  change, the Huffman code is fixed by swapping the positions of the
  affected pair; for an accessed subset S, |S| pair-swaps transform
  the old frequency order f into the new order f'. For a promoted
  e_i, the swap partner is
  e_j = arg min_e { f(e) | f(e) > f(e_i), f'(e) < f'(e_i) }.
  A swap costs hashing proportional to the distance between the two
  nodes; batching several swaps avoids redundant rehashing of shared
  ancestors.
- Adaptive Huffman coding (Knuth 1985, Vitter 1987) is rejected for
  the ADS setting: every structural change requires hash maintenance
  before the next root can be committed (measured 3 orders of
  magnitude slower; see microbenchmarks below).

## Soundness (Section 4.1)

Assumptions: H collision resistant; all hashed inputs prefix-free and
domain separated (leaf encodings, internal nodes, empty roots,
tier-root tuples, global-root tuples); committed state key-disjoint
across tiers (each live key in exactly one tier).

- Proposition 4.1 (multi-tier membership soundness): key-disjoint tier
  datasets D_0, ..., D_{T-1}, each tier a membership-sound ADS with
  root r_i, global commitment the domain-separated hash of the ordered
  root tuple: the resulting ADS is membership sound. Proof: a false
  proof either yields two distinct domain-separated inputs with the
  same hash (collision) or verifies against an honest tier root for a
  non-member (breaking that tier's soundness).
- Proposition 4.2 (HuffMHT membership soundness): a HuffMHT with
  key-value leaves and ordered-child internal hashes is membership
  sound when H is collision resistant; the argument is independent of
  balance because the Huffman layout changes only path lengths, not
  the bottom-up authentication recurrence.
- Proposition 4.3 (HMT membership soundness): HMT is membership sound
  when its constituent tier ADSs are membership sound and H is
  collision resistant. The CMS, promotion cache, and migration policy
  only determine which tier stores each key BEFORE the next root is
  committed; they do not change verification once tier roots are
  fixed (frequency-estimation error can hurt layout quality, never
  proof soundness).

## Policy machinery

- Count-Min Sketch (Cormode-Muthukrishnan) for frequency estimates: a
  d x w counter array, w = ceil(e / eps), d = ceil(ln(1 / delta));
  per-key guarantee f(x) <= fhat(x) <= f(x) + eps * T with probability
  >= 1 - delta (T = total observed accesses). Example: eps = delta =
  10^-6 with 32-bit counters is about 152 MB, versus >= 360 MB for
  exact counters over 10^7 distinct 32-byte keys; memory is fixed, not
  proportional to the number of elements. Row indices derived from one
  BLAKE3 computation (deterministic so replicas agree), conservative
  update to reduce overestimation; O(d) per update/query.
- Promotion Cache: in-memory policy metadata, NOT authenticated state.
  Hot-tier caches mirror tier membership exactly (capacity C_i);
  cold-tier cache tracks only promotion candidates. Implemented as
  bucketed LFU: keys batched into frequency ranges of width R, LRU
  replacement within a bucket, O(1) eviction from the
  minimum-frequency bucket. Total space O(wd + sum_i (N_i + K_i)).
- Migration policies (Section 5), decisions batched at period
  boundaries (in the blockchain evaluation, at the end of block
  building), deterministic across replicas given the same access
  stream:
  - Absolute Threshold: promote when cumulative CMS estimate
    fhat(x) > theta_i; drawback: counts never decay, so early-hot
    elements stay favored.
  - Ratio-Based: lifetime access rate s_B(x) = fhat(x) / B over B
    elapsed periods, promote when s_B(x) > theta_i; ranks identically
    to Absolute Threshold (same denominator), stable but stale-friendly.
  - Sliding-Window: a ring of recent period histograms with aggregate
    H_W over W periods; window rate s_W(x) = H_W(x) / W; promote when
    s_W(x) >= theta_i; demotion is LAZY (a per-edge demotion wheel
    rechecks after a delay; demote only if still below threshold),
    reducing churn for boundary-oscillating items while staying
    responsive to shifts.
  - Dynamic-Control: feedback loops adjust the promotion threshold
    theta_i (every M periods, from occupancy rho_i = n_i / C_i and
    rejection ratio q_i, clamped to [theta_min, theta_max] with
    theta_max derived from the least-frequent element already in the
    hotter tier) and the hot-tier capacity C_i (every K control
    windows, only after threshold adjustment is exhausted).

## Evaluation (verified numbers)

- Microbenchmark, pre-inserted keys (N = 100,000 keys, then 5,000,000
  get/update ops, Zipf with a = 4, b = 1, 500,000-op milestones):
  batched pair-swaps average 47.1 ms per milestone vs 100.3 ms for
  full rebuilds over milestones 2-10, a 2.13x reduction.
- Microbenchmark, continuous insertion (100,000 keys inserted over
  5,000,000 ops): periodic-rebuild HuffMHT spends about 180 ms at the
  final milestone vs about 136 SECONDS for an adaptive Huffman tree
  (per-operation restructuring plus hash maintenance).
- Ethereum replay: a go-ethereum StateDB trace recorded during block
  execution, replayed deterministically from block 17,000,000 for one
  million blocks at ACCOUNT granularity (storage attributed to the
  owning contract account; snapshot/revert markers honored; accounts
  materialized on first access with deterministic placeholders).
  Compared ADSs: MPT, UBT, and three two-tier HMT configurations
  (Ratio-Based, threshold 0.05, promotion-cache capacities
  8,000/16,000; Sliding-Window, 1,000-block window, threshold 0.05,
  100-block lazy demotion; Dynamic-Control with M = 2,500-block
  windows, K = 3, occupancy band [0.75, 0.95], q_high = 0.3, U = 3).
  Every HMT rebuilds its HuffMHT every 500 blocks. Metrics: per-block
  hashed input bytes at commit, and inclusion-proof size weighted by
  per-block access counts. Hardware: Dell PowerEdge R7715, 16-core
  AMD EPYC 9135, 32 GB, Go 1.25.4.
- Results: Sliding-Window is the best policy. Headline numbers
  (abstract and conclusion): about 2.4x less average hash operations
  than MPT and 0.34x less than UBT; access-weighted proofs "shorter by
  0.18x than MPT and 0.55x than UBT". CAUTION on the multiplier
  phrasing, which mixes conventions; the plots (Figure 9, Appendix C)
  disambiguate: per-block hashed input is roughly 5.5-6 x 10^5 bytes
  for MPT, 3.3-3.5 x 10^5 for UBT, and 2-2.5 x 10^5 for the HMTs
  (so about 2.4x below MPT and about 34% below UBT); weighted average
  proof size is about 3 KB for MPT, about 1.1 KB for UBT, and in the
  hundreds of bytes (about 0.5 KB) for all HMT variants (so about
  0.18x of MPT and about 45% of UBT, i.e. a 55% reduction). Read- and
  write-weighted refinements (Appendix C) show the same ordering, so
  the reduction is not an artifact of the trace's read/write mix.
  Ratio-Based is slightly less responsive but stable; Dynamic-Control
  stays competitive in proof size but costs more hash input, and the
  authors treat it as exploratory. Appendix B: two more fixed
  policies (Absolute Threshold, cumulative estimate > 50,000; Periodic
  Evaluation, rate 0.05 every 500 blocks) preserve the trend.

## Related work recorded by the paper

- Authenticated state commitments: authenticated dictionaries / hash
  tables / generic ADS frameworks; locality-optimized memory checking
  (Wang, Lu, Papamanthou, Zhang, CCS 2023); Ethereum directions
  (UBT/EIP-7864, Verkle migration EIP-7748); accumulator / key-value /
  vector commitments (Boneh-Bunz-Fisch, KVaC, Tas-Boneh); storage-
  oriented systems (mLSM, RainBlock/DSM-Tree, Jellyfish Merkle Tree,
  LVMT, QMDB, AlDBaran) which target I/O and storage locality rather
  than the authenticated layout. HMT changes neither the commitment
  primitive nor the backing store; it adapts the authenticated path
  lengths to the observed workload.
- Frequency-aware trees: skewed/unbalanced authenticated trees applied
  to certificate revocation (QuasiModo, Elwailly-Gentry-Ramzan, PKC
  2004), skew Merkle tree traversal (Karpinski-Nekrich 2004), and
  hardware memory-integrity checking (Szefer-Biedermann, HASP 2014);
  HuffMHT (TrustBus 2005) as the direct static precursor. Huffman
  optimality holds only for static i.i.d. accesses; dynamic
  distributions were flagged as future work by Szefer-Biedermann.
- Online-algorithms framing: the theoretic literature evaluates
  dynamic data structures by competitive ratio against an offline
  optimum (list update, paging); this paper deliberately optimizes
  real-world average-case performance instead. No competitive-ratio or
  optimality theorem is claimed for HMT; the guarantees proved are the
  soundness propositions, and the performance claims are empirical.

## Side-find for our bibliography

Their reference [7] gives the published venue of our central source
eprint 2025/234: Bonneau, Chen, Christ, Karantaidou, "Merkle Mountain
Ranges are Optimal: On Witness Update Frequency for Cryptographic
Accumulators", CRYPTO 2025, Springer, pp. 170-202, ISBN
978-3-032-01878-6, DOI 10.1007/978-3-032-01878-6_6. Also potentially
relevant: [25] Mendonca, Shi, Huynh, Pryvalov, Herzberg, "Efficient
Merkle-Tree Consistent Accumulator", eprint 2026/673 (not read).

## Understanding and use in the paper

- The metric HMT optimizes is ACCESS-WEIGHTED expected cost (proof
  length and update hashing) under a skewed, drifting access
  distribution. This is orthogonal to the witness-update-frequency
  metric of Bonneau-Chen-Christ-Karantaidou: 2025/234 counts how often
  OTHER parties' witnesses are invalidated by appends in an
  append-only accumulator, while HMT tunes the per-access cost of the
  party querying a mutable key-value map. Neither subsumes the other:
  HMT is a dictionary ADS (updates in place, no append-only history,
  no consistency proofs), and its layout freedom (Huffman shape) is
  exactly what append-only structures like MMRs give up in exchange
  for immutable interior nodes and rare witness updates.
- Placement: one related-work paragraph in the comparison section
  (Section 9 of the target structure), presenting workload-adaptive
  layouts as a second optimality axis next to witness-update
  frequency; cite 2026/1235 for HMT and TrustBus 2005 (HuffMHT) as the
  static precursor. Not a candidate for a full section: it addresses
  dynamic dictionaries, not the append-only log/MMR problem set that
  drives the paper.
- Quotable precise items: Definition 2.1 (ADS interface),
  Propositions 4.1-4.3 with their assumptions, the pair-swap rule and
  its |S|-swaps claim, the N - 1 vs ceil(log2 N) worst-case depth
  argument for why cold items need a balanced tree, and the verified
  evaluation numbers above.
- Caveats for citation: an eprint (2026/1235) with no peer-reviewed
  venue listed as of the version read; all performance claims are
  empirical (one Ethereum trace, one hardware setup); the headline
  "0.34x / 0.18x / 0.55x" multipliers mix conventions and should be
  restated from the plot-level numbers if quoted.
