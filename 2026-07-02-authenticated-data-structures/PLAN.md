# Paper plan: Authenticated data structures, MMRs, and witness-update optimality

Living document guiding the redaction of this paper. It tracks the
target structure, the TODOs, and every source found, with notes on what
to cite each source for. Update it as the paper progresses; keep the
log at the bottom.

Driving issue:
<https://github.com/dannywillems/dannywillems.github.io/issues/535>.
The issue's 3000-4000-word constraint applies to the blog article, not
to this paper; the paper takes the full treatment.

## Goal

An engineering-and-theory treatment of authenticated data structures
(ADS): definitions and models, the Merkle/accumulator design space,
append-only logs, Merkle Mountain Ranges (MMRs) as the running example,
the witness-update optimality result (eprint 2025/234), witness
maintenance algorithms, and a production case study (Zcash note
commitment trees / shardtree). Audience: engineers, protocol designers,
cryptography researchers. Explicit complexity bounds and optimality
results throughout; every non-trivial claim proved, cited, or
implemented.

The authoritative motivation is the human-only section of this
directory's `AGENTS.md`: provide FORMAL DEFINITIONS of ADS, their
properties, and multiple instances satisfying them, with Python
implementations and Lean code; structure the definitions and the Lean
development as LIBRARIES reusable by other authors and agents. The
paper grew out of asking, while reading zcash/incrementalmerkletree,
which structures in the literature solve exactly the problems that
repository addresses.

## Canonical property set (agreed 2026-07-19)

The properties the formal ADS definitions, the Python library, and
the Lean library are built against. Source: issue comment
<https://github.com/dannywillems/dannywillems.github.io/issues/535#issuecomment-5016934670>
(core properties 1-6), plus bounded memory footprint (added by the
author in session) and three explicit companions agreed in session.
This is the interface the incremental-Merkle-tree problem class
requires:

1. append (append-only insertion of new elements);
2. sparse witnesses (maintain witnesses only for a marked subset of
   elements, not all of them);
3. pruning (discard interior data not needed for the marked witnesses
   and retained checkpoints);
4. out-of-order insertion (leaves and subtree roots inserted in
   arbitrary order around a tracked frontier);
5. bounded checkpoints (at most a fixed number of retained states);
6. proof update when new elements are added (incremental /
   fast-forwardable witnesses);
7. bounded memory footprint: the persistent state is bounded by a
   function of the number of marked witnesses, the number of retained
   checkpoints, and the tree depth (so O((m + c) log n) hashes for m
   marked leaves and c checkpoints in a depth-log n tree), NOT by the
   total number n of appended elements. This is the guarantee that
   pruning (property 3) must deliver, stated as a bound so instances
   can be proved to meet or fail it; the frontier alone is the
   O(log n) floor (appending needs nothing else), and policy-side
   state can be bounded separately (cf. the Count-Min Sketch in the
   HMT paper: fixed-size frequency state independent of the number of
   elements).

Explicit companions:

8. rewind (restore the structure to any retained checkpoint; the
   operation over property 5);
9. verification against recent anchors (proofs verify against any
   checkpointed root in a bounded history, not only the latest
   digest);
10. metrics attached to property 6, so optimality can be stated:
    total witness-update count (eprint 2025/234, Definition 8) and
    the cost of a single witness fast-forward.

Deliberately out of this set: consistency proofs between digests
(RFC 6962); the Zcash workload gets digest consistency from
consensus. The paper covers them in the append-only-logs section as
an extension, not as a required property.

## Current state (2026-07-19)

The paper is a compact note covering the base construction only:

- ADS definition, two-party model, memory-checking lineage
  (Sections 1-3 of the paper).
- Balanced binary Merkle-tree log with domain separation, membership
  proofs, completeness/soundness/proof-size propositions (Sections 4-5).
- Python reference implementation (`code/`, `ads.merkle`) and Lean 4
  formalisation (`lean/`, completeness, soundness, proof length, no
  `sorry`).

Everything past the base construction is missing: sparse Merkle trees,
accumulators, history trees and consistency proofs, MMRs, the
optimality result, witness maintenance, the Zcash case study, the
comparison table.

## Target structure

Mapped from the issue outline, adapted to the paper format:

1. Introduction: what an ADS is, deployment contexts (CT, light
   clients, rollups, timestamping, privacy-preserving payments), and
   the recurring problem set (append, prove membership, maintain a
   witness, prune, roll back). Contribution list.
2. Models and definitions: two-party (Merkle) vs three-party
   (Tamassia) ADS; static vs dynamic vs append-only; membership and
   non-membership proofs; digest, prover, verifier; completeness and
   soundness (already present, to be generalised beyond the log).
3. Base primitives: Merkle trees (present); sparse and pruned Merkle
   trees (Laurie-Kasper caching, Dahlberg-Pulls-Peeters efficient
   representation); cryptographic accumulators (RSA vs Merkle,
   trapdoor vs trapdoor-less, witness model).
4. Append-only logs and history trees: Crosby-Wallach tamper-evident
   logging; RFC 6962 audit proofs and consistency proofs (with the
   consistency-proof algorithm and bounds).
5. Merkle Mountain Ranges: structure (list of perfect binary trees /
   truncated tree), position numbering, O(log n) append, peak bagging,
   proofs, and the key property that interior nodes are immutable once
   written. Todd (OpenTimestamps) and Grin as primary descriptions.
6. Witness-update optimality: eprint 2025/234. State the lower bound
   (total witness updates over n sequential insertions for any
   accumulator with succinct commitment), the model, and how an MMR
   variant matches it. Consequences for light clients.
7. Witness maintenance and traversal: the classic problem; fractal
   traversal (JLMS, CT-RSA 2003); Szydlo Eurocrypt 2004 (2 log N
   hashes, < 3 log N storage, matching lower bound); how the
   sparse-witness workload differs from the hash-based-signature
   workload.
8. Case study, Zcash: note commitment trees; why wallets need
   fast-forwardable witnesses; the real-world combination (append +
   sparse witnesses + pruning + out-of-order insertion + bounded
   checkpoints + DB-backed sharding); the clean core vs the
   bookkeeping; incrementalmerkletree / shardtree design. Then
   Tachyon (Sean Bowe, 2025) as the forward-looking counterpart:
   shardtree engineers WITHIN the witness-update lower bound;
   Tachyon moves the cost off the wallet entirely via wallet-state
   proof-carrying data plus an oblivious syncing service, and prunes
   all old chain state. Neither beats eprint 2025/234; both relocate
   its cost. See `notes/tachyon-zcash-shielded-protocol.md`.
9. Comparison and trade-offs: MMR vs sparse Merkle tree vs RSA
   accumulator on append cost, proof size, witness update frequency,
   non-membership support, trusted setup. When each is right.
10. Conclusion and open directions.

## Artifacts plan

The repository convention pairs each paper with runnable code and
machine-checked proofs. Planned extensions:

Both artifacts are LIBRARIES, per the human-only motivation: reusable
definitions and properties first, instances second.

- Python (`code/`): structure `ads` as a library of interfaces
  (digest/prove/verify, append, witness maintenance) with the Merkle
  log as one instance; add an MMR instance (append, peaks, bagging,
  membership proofs, consistency between digests) and a
  witness-maintenance simulator counting witness updates per append
  (to illustrate the eprint 2025/234 bound empirically), tests for
  everything.
- Lean (`lean/`): a reusable library layer of ADS definitions and
  properties (completeness, soundness, proof-size, witness-update
  counting), with the existing Merkle-log proofs refactored as the
  first instance and MMR as the second (key property: append never
  mutates an existing node position; proof-size bound). The
  optimality lower bound itself is likely out of reach for a first
  pass; state as future work.

## TODOs

Phase 0, context (this file):

- [x] Read issue 535 and extract the outline and sources.
- [x] Gap analysis against the current paper.
- [x] Digest the theory sources (agent pass done 2026-07-19, notes
      under `notes/`; eprint 2025/234 additionally READ WHOLE
      first-hand from the local PDF and its note is verified).
- [x] Digest the practice sources (agent pass done 2026-07-19, notes
      written under `notes/`; claims still to re-verify before
      citing).
- [x] Resolve "Huffman-Merkle Tree (HMT)": identified as eprint
      2026/1235 (Shangguan, Yaish, Malkhi, "Authenticated Data
      Structures for Dynamic Workloads"); local PDF provided.
- [x] Read `eprint/2016-683.pdf` (Dahlberg et al.) whole and upgrade
      its note to verified (done 2026-07-19; note now records the
      full definitions, the B/B-/B+ caches, and the adversarial
      branch-spine analysis).
- [x] Read `eprint/2026-1235.pdf` (HMT) whole and write its full
      note; decide its place in related work (done 2026-07-19;
      decision: one related-work paragraph in Section 9 presenting
      workload-adaptive layouts as an orthogonal optimality axis, see
      the source entry below).
- [x] Research Tachyon and its relation to the property set (done
      2026-07-19; note verified against primary sources; see the
      Tachyon source entry and the log).
- [ ] Manually download eprint 2025/2031 (Bowe & Miers, "A Note on
      Notes") into `eprint/`, read it whole, and upgrade the Tachyon
      note's accumulator/nullifier construction from "sketched" to
      verified. This is the one remaining Tachyon gap.

Phase 1, structure:

- [ ] Restructure `main.tex` into the target structure (section
      skeletons with scope notes, keeping the existing material as
      Sections 2-3 content).
- [ ] Extend `references.bib` with all sources below (verified
      metadata, DOIs).

Phase 2, theory sections:

- [ ] Write Section 2 (models and formal definitions) against the
      canonical property set above; the definitions double as the
      interfaces of the Python and Lean libraries.
- [ ] Write Section 3 (sparse Merkle trees, accumulators).
- [ ] Write Section 4 (history trees, RFC 6962 proofs, with the
      consistency-proof algorithm).
- [ ] Write Section 5 (MMR construction, formally stated: positions,
      append, bagging, proofs; state the immutability property as a
      proposition).
- [ ] Write Section 6 (the optimality result: restate the bound and
      the matching construction faithfully from eprint 2025/234).
- [ ] Write Section 7 (traversal/witness maintenance: JLMS, Szydlo,
      sparse-witness workload).

Phase 3, practice sections:

- [ ] Write Section 8 (Zcash case study: protocol grounding,
      incrementalmerkletree/shardtree design, what makes it hard).
- [ ] Write Section 9 (comparison table plus prose).

Phase 4, artifacts:

- [ ] Python MMR implementation plus tests.
- [ ] Witness-update counting simulation plus a small table/figure in
      the paper.
- [ ] Lean: MMR append immutability plus proof-size bound.

Phase 5, polish:

- [ ] Introduction and conclusion rewritten against the final content.
- [ ] Abstract rewritten.
- [ ] Bibliography pass (every claim cited, DOIs checked).
- [ ] Full build (PDF + HTML), site check, CHANGELOG entries.

## Sources

Annotated bibliography. Status: "verified" means the claims cited in
the paper were checked against the source itself, not a summary.

Per the repository convention (AGENTS.md, "Reading notes"), every
source that gets read produces a knowledge-dump file under `notes/`,
one markdown file named after the source. The list below tracks WHAT
to read and WHY; the notes hold the extracted content.

### From the issue (primary)

- Tamassia, "Authenticated Data Structures", ESA 2003.
  For: the three-party ADS model framing. In references.bib already.
  Status: cited in current paper, claims to re-verify when Section 2
  is written.
- Merkle, "A Digital Signature Based on a Conventional Encryption
  Function", CRYPTO 1987. For: Merkle trees. In references.bib.
- Blum, Evans, Gemmell, Kannan, Naor, "Checking the Correctness of
  Memories", Algorithmica 1994. For: memory-checking lineage. In
  references.bib.
- Laurie, Langley, Kasper, RFC 6962, "Certificate Transparency", IETF
  2013. For: audit proofs, consistency proofs, production append-only
  logs. In references.bib.
- Crosby, Wallach, "Efficient Data Structures for Tamper-Evident
  Logging", USENIX Security 2009. For: history trees, membership and
  incremental (consistency) proofs in a versioned append-only tree.
  TODO add to references.bib.
- Dahlberg, Pulls, Peeters, "Efficient Sparse Merkle Trees" (NordSec
  2016; eprint 2016/683). For: sparse Merkle trees, caching strategies,
  non-membership proofs. Status: VERIFIED, read whole from the local
  PDF 2026-07-19; note upgraded with Definitions 1-2, the B/B-/B+
  caches, the secure encodings, and the branch-spine worst case
  (at most N traversals, one per layer; the note records the
  citation caveats). Notes:
  `notes/dahlberg-pulls-peeters-2016-sparse-merkle-trees.md`.
  TODO add to references.bib.
- Jakobsson, Leighton, Micali, Szydlo, "Fractal Merkle Tree
  Representation and Traversal", CT-RSA 2003. For: first sublinear
  traversal algorithm. TODO add.
- Szydlo, "Merkle Tree Traversal in Log Space and Time", Eurocrypt
  2004. For: 2 log N time / < 3 log N space traversal and the matching
  lower bound. TODO add.
- Bonneau, Chen, Christ, Karantaidou, "Merkle Mountain Ranges are
  Optimal: On Witness Update Frequency for Cryptographic
  Accumulators", eprint 2025/234. For: the central lower bound and the
  matching MMR variant. Read whole and verified (see the log).
  Published venue (found via 2026/1235's bibliography, reference [7]):
  CRYPTO 2025, Springer, pp. 170-202, ISBN 978-3-032-01878-6,
  DOI 10.1007/978-3-032-01878-6_6; cite the proceedings version.
  TODO add to references.bib. eprint cannot be fetched by agents: the
  human downloads the PDF into `eprint/` (gitignored, see AGENTS.md),
  and it is read from there.
- Peter Todd, "Merkle Mountain Ranges", OpenTimestamps documentation.
  For: the original MMR description. Notes:
  `notes/todd-merkle-mountain-ranges.md`. TODO add to references.bib
  (online reference with access date).
- Grin project, MMR documentation (mimblewimble/grin). For: production
  MMR usage, position-prefixed hashing, PMMR pruning. Does NOT
  describe proof construction; do not cite it for that. Notes:
  `notes/grin-mmr-documentation.md`. TODO add.
- zcash/incrementalmerkletree (README, docs.rs). For: frontier,
  incremental/fast-forwarding witnesses, checkpoint/rewind. Notes:
  `notes/zcash-incrementalmerkletree.md`. TODO add.
- shardtree crate (lib.rs / docs.rs). For: shard/cap split, retention
  flags, pruning, out-of-order insertion, witness fast-forward via
  shard roots. Notes: `notes/shardtree-crate.md`. TODO add.
- The Orchard Book, commitment tree design section. For: the explicit
  witness-update workload statement and the
  keep-structure/fix-implementation decision. Notes:
  `notes/orchard-book-commitment-tree.md`. TODO add.
- zcash/zcash issue #4713. CAUTION: only specifies per-layer domain
  separation for MerkleCRH^Orchard, nothing about witnesses; cite
  narrowly. Notes: `notes/zcash-issue-4713-orchard-merkle-design.md`.
  TODO add.
- Zcash protocol specification, sections 3.8 and 5.3. For: protocol
  grounding (append-only, fixed depths 29/32/32, anchors, Merkle path
  validity in spend circuits). Notes:
  `notes/zcash-protocol-spec-note-commitment-trees.md`. TODO add.
- Certificate Transparency project, "How CT Works". For: one-paragraph
  production grounding of Section 4. Notes:
  `notes/certificate-transparency-production.md`. TODO add.
- Working synthesis (not citable):
  `notes/synthesis-witness-maintenance.md`.
- Tachyon (Sean Bowe + the tachyon-zcash community project; NOT ECC).
  For: Section 8, the forward-looking counterpart to shardtree, and
  the conclusion's "the lower bound is unbeatable, so the engineering
  relocates the work" framing. Full note (verified against primary
  sources) at `notes/tachyon-zcash-shielded-protocol.md`. Primary:
  Bowe's blog posts (tachyon oblivious-sync 2025-04-02, tachyaction
  2025-05-15, ragu-for-orchard 2025-04-17), tachyon.z.cash
  overview/roadmap and the Ragu post, and the Ragu repo
  (github.com/tachyon-zcash/ragu). FORMAL WRITE-UP:
  eprint 2025/2031, Bowe & Miers, "A Note on Notes: Towards Scalable
  Anonymous Payments via Evolving Nullifiers and Oblivious
  Synchronization" (Nov 2025); central for the concrete accumulator/
  nullifier construction; MUST be downloaded manually into `eprint/`
  per the eprint rule, still unread first-hand. Proving-system
  background: Halo (Bowe, Grigg, Hopwood, eprint 2019/1021). TODO add
  2025/2031 (and Halo 2019/1021 if the proving system is discussed)
  to references.bib once the eprint is read. Keep NU7 targeting OUT
  (unconfirmed by primary sources).
- Shangguan, Yaish, Malkhi, "Authenticated Data Structures for
  Dynamic Workloads" (the Huffman-Merkle Tree, HMT), eprint 2026/1235.
  Resolves the "Huffman-Merkle Tree (HMT)" issue comment. Status:
  VERIFIED, read whole from the local PDF 2026-07-19; full note at
  `notes/huffman-merkle-tree-hmt.md`. Decision: one related-work
  paragraph in Section 9, presenting workload-adaptive layouts
  (access-weighted expected proof/update cost under skewed, drifting
  workloads; tiered hot HuffMHT + cold Merkle tree) as an optimality
  axis ORTHOGONAL to the witness-update frequency of 2025/234; cite
  2026/1235 with HuffMHT (TrustBus 2005) as the static precursor. Not
  a full section: it is a dynamic dictionary ADS, not the append-only
  problem set driving this paper. TODO add both to references.bib
  when Section 9 is written (note the citation caveats recorded in
  the note: eprint only, empirical claims, ambiguous headline
  multipliers).

### Found during research

Secondary sources surfaced by the digests (metadata from eprint
2025/234's bibliography, verified there; fetch before citing):

- Reyzin, Yakoubov, "Efficient Asynchronous Accumulators for
  Distributed PKI", SCN 2016. Rediscovered the MMR; their Theorem 2
  is the k = 2 witness-update upper bound.
- Camacho, Hevia, "On the impossibility of batch update for
  cryptographic accumulators", Latincrypt 2010. Deletion-based lower
  bound predecessor.
- Christ, Bonneau, "Limits on revocable proof systems, with
  applications to stateless blockchains", Financial Crypto 2022.
  Omega(n/log n) change-once bound for dynamic/universal
  accumulators.
- Bunz, Kiffer, Luu, Zamani, "FlyClient: Super-light clients for
  cryptocurrencies", IEEE S&P 2020. MMR-based light clients; adopted
  by Grin, Minima, Nervos, Neptune, Zcash.
- Benaloh, de Mare, "One-Way Accumulators", Eurocrypt 1993.
- Camenisch, Lysyanskaya, "Dynamic Accumulators and Application to
  Efficient Revocation of Anonymous Credentials", CRYPTO 2002.
- Nguyen, "Accumulators from Bilinear Pairings and Applications",
  CT-RSA 2005; Li, Li, Xue, "Universal Accumulators with Efficient
  Nonmembership Proofs", ACNS 2007; Damgard, Triandopoulos,
  "Supporting Non-membership Proofs with Bilinear-map Accumulators",
  eprint 2008/538.
- Boneh, Bunz, Fisch, "Batching Techniques for Accumulators...",
  CRYPTO 2019 (batching does not reduce update frequency).
- Miller, Hicks, Katz, Shi, "Authenticated data structures,
  generically", POPL 2014.
- Papamanthou, Tamassia, Triandopoulos, "Authenticated hash tables
  based on cryptographic accumulators", Algorithmica 74, 2016.
- Google Transparency project, "Compact Ranges" (online, 2022+): the
  MMR-adjacent concept in the CT tooling.
- Crosby-Wallach history trees described by 2025/234 as the MMR
  precursor "with all sub-trees included as nodes of a larger tree".
- Szydlo preprint vs proceedings caveat: the free 2003 preprint
  differs from the Eurocrypt 2004 version; cite the published
  constants (2 log N time, < 3 log N space).
- HMT lineage: Munoz, Forne, Esparza, Rey, "HuffMHT", TrustBus 2005
  (Huffman-shaped Merkle tree precursor). Full metadata verified in
  2026/1235's bibliography: LNCS 3592, pp. 119-127,
  DOI 10.1007/11537878_13.
- Mendonca, Shi, Huynh, Pryvalov, Herzberg, "Efficient Merkle-Tree
  Consistent Accumulator", eprint 2026/673 (surfaced by 2026/1235's
  bibliography; not read; possibly relevant to Sections 4-6).

## Log

- 2026-07-19: File created. Issue 535 read; gap analysis done; source
  digests in progress (two research passes: theory and practice).
- 2026-07-19 (later): Both digests done; 17 notes files written under
  `notes/`. eprint 2025/234 read whole first-hand from the local PDF
  (25 pages) and its note verified: Theorem 1 (omega(n) updates for
  succinct accumulators), Corollary 2 (Omega(n log n / log log n) in
  the superpolynomial regime), Theorem 2 + Corollary 3 (k-ary MMR
  upper bound, optimal at k = polylog n). HMT identified as eprint
  2026/1235. Remaining reads: 2016/683 and 2026/1235 local PDFs
  (fresh session, per the no-compaction rule).
- 2026-07-19 (later still): The two remaining reads done, whole and
  first-hand, in one fresh session. 2016/683 (16 pages): note
  verified and extended with Definitions 1-2, the recurrences, the
  B/B-/B+ caches, the secure encodings, and the branch-spine
  worst case (two prior paraphrases corrected: Definition 1's shape,
  and the traversal bound, which is at most N per audit path, not
  constant). 2026/1235 (34 pages): full note written, replacing the
  placeholder; placement decided (related-work paragraph in
  Section 9). Side-find: the published venue of 2025/234 is CRYPTO
  2025 (DOI 10.1007/978-3-032-01878-6_6). Phase 0 is complete.
- 2026-07-19 (later still): Property 7, bounded memory footprint,
  added to the canonical property set at the author's request: state
  bounded by marked witnesses + checkpoints + depth, never by the
  total number of appended elements; companions renumbered 8-10.
- 2026-07-19 (Tachyon): deep-research pass on Tachyon (Sean Bowe's
  next-gen Zcash shielded protocol). 10 claims verified against his
  two primary blog posts (0 refuted); pass stopped before full
  synthesis, note written from the verified core
  (notes/tachyon-zcash-shielded-protocol.md) with a per-property
  mapping. Key finding: Tachyon's stated bottleneck IS the
  witness-update problem; it does not beat the omega(n) lower bound
  but moves the cost off the wallet (PCD wallet state + oblivious
  syncing service) and prunes all old chain state.
- 2026-07-19 (Tachyon follow-up): three targeted agents closed the
  open items. (a) Accumulator: role unchanged (append + anchor +
  set-inclusion) but the CONCRETE structure is deliberately unnamed
  in the blogs; Tachyon introduces a new PCD-friendly
  (non-)membership accumulator into which nullifiers "and potentially
  also note commitments" are batch-inserted, scheme only "sketched".
  (b) Nullifiers: reversed derivation; the historical freshness check
  moves into PCD so validators check only "the most recent
  block(s)", which is what makes global pruning of the nullifier set
  sound. (c) FORMAL WRITE-UP FOUND: eprint 2025/2031, Bowe & Miers,
  "A Note on Notes: Towards Scalable Anonymous Payments via Evolving
  Nullifiers and Oblivious Synchronization" (Nov 2025); central,
  needs manual download per the eprint rule. (d) Proving system Ragu
  confirmed: github.com/tachyon-zcash/ragu, Rust PCD, modified Halo
  (eprint 2019/1021) over Pasta + Poseidon, trusted-setup-free,
  un-audited. (e) Status: no Tachyon ZIP; NU7 inclusion UNCONFIRMED
  (primary sources do not pin it to NU7; likely post-NU7);
  attribution corrected to Sean Bowe + the independent tachyon-zcash
  community project, NOT ECC (Bowe left ECC in 2024). Note fully
  updated; the only remaining gap is the concrete accumulator
  construction, expected in eprint 2025/2031.
