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
   bookkeeping; incrementalmerkletree / shardtree design.
9. Comparison and trade-offs: MMR vs sparse Merkle tree vs RSA
   accumulator on append cost, proof size, witness update frequency,
   non-membership support, trusted setup. When each is right.
10. Conclusion and open directions.

## Artifacts plan

The repository convention pairs each paper with runnable code and
machine-checked proofs. Planned extensions:

- Python (`code/`): an MMR implementation next to `ads.merkle` (append,
  peaks, bagging, membership proofs, consistency between digests), a
  witness-maintenance simulator counting witness updates per append
  (to illustrate the eprint 2025/234 bound empirically), tests for
  both.
- Lean (`lean/`): formalise the MMR key property (append never mutates
  an existing node position) and the proof-size bound; keep the
  existing Merkle-log proofs as the base layer. The optimality lower
  bound itself is likely out of reach for a first pass; state as
  future work.

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
- [ ] Read `eprint/2016-683.pdf` (Dahlberg et al.) whole and upgrade
      its note to verified.
- [ ] Read `eprint/2026-1235.pdf` (HMT) whole and write its full
      note; decide its place in related work.

Phase 1, structure:

- [ ] Restructure `main.tex` into the target structure (section
      skeletons with scope notes, keeping the existing material as
      Sections 2-3 content).
- [ ] Extend `references.bib` with all sources below (verified
      metadata, DOIs).

Phase 2, theory sections:

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
  non-membership proofs. TODO add.
- Jakobsson, Leighton, Micali, Szydlo, "Fractal Merkle Tree
  Representation and Traversal", CT-RSA 2003. For: first sublinear
  traversal algorithm. TODO add.
- Szydlo, "Merkle Tree Traversal in Log Space and Time", Eurocrypt
  2004. For: 2 log N time / < 3 log N space traversal and the matching
  lower bound. TODO add.
- "Merkle Mountain Ranges are Optimal: On Witness Update Frequency for
  Cryptographic Accumulators", eprint 2025/234. For: the central lower
  bound and the matching MMR variant. TODO add; verify authors and the
  exact theorem statement from the PDF. eprint cannot be fetched by
  agents: the human downloads the PDF into `eprint/` (gitignored, see
  AGENTS.md), and it is read from there. Same applies to
  Dahlberg-Pulls-Peeters if the NordSec version is not accessible
  elsewhere (their eprint is 2016/683).
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
- "Huffman-Merkle Tree (HMT)": mentioned in an issue comment without a
  reference. TODO identify the intended source before deciding
  whether it enters the paper.

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
  (Huffman-shaped Merkle tree precursor).

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
