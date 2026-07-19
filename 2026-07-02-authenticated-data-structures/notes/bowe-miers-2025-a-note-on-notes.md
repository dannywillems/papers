# Bowe, Miers, "A Note on Notes: Towards Scalable Anonymous Payments via Evolving Nullifiers and Oblivious Synchronization" (eprint 2025/2031)

- Authors: Sean Bowe (Zcash; ewillbefull@gmail.com), Ian Miers
  (University of Maryland; imiers@umd.edu).
- Reference: IACR Cryptology ePrint Archive 2025/2031, November 2025
  (short note, 8 pages incl. references; no peer-reviewed venue
  recorded). <https://eprint.iacr.org/2025/2031>.
- Version read: local PDF
  `eprint/A Note on Notes_ ... - 2025-2031.pdf`, supplied manually
  per the eprint rule.
- Status: VERIFIED. Read WHOLE first-hand (all 8 pages, no
  compaction) on 2026-07-19. Quotes below are faithful to the PDF.
  This is the FORMAL write-up behind Tachyon's nullifier design; it
  refines and in one place corrects the blog-based understanding (see
  "Corrections" at the end).

## Scope and thesis

This is a focused note on ONE of the two growing-state problems of
Zerocash-style anonymous payments: the perpetually growing NULLIFIER
set. It is NOT about the note-commitment tree (the append-only
membership accumulator this paper's project centers on); that is
treated abstractly and left unchanged. The contribution is a general
model, "oblivious synchronization", plus a specific enabling
mechanism, "evolving nullifiers".

Abstract, verbatim highlights: Zerocash-derived protocols "require
every consensus participant to maintain a perpetually growing set of
nullifiers -- unlinkable revocation tokens used to detect
double-spending -- which must be stored, queried and updated by all
validating nodes. This set grows linearly in the number of historic
transactions and cannot be discarded without the undesirable effect
of destroying unspent funds." They introduce "continual, permanent
pruning of nullifiers by validators, without imposing significant
computation, bandwidth or latency overhead for users, and without
compromising privacy", via "oblivious synchronization whereby users
ask untrusted remote services (which ingest and process the public
ledger) to create succinct proofs that coins are unspent and
otherwise valid. ... these services are fully oblivious to their
clients' transaction details and cannot link their clients to any
transactions that ultimately appear on the public ledger. Moreover,
these services only keep ephemeral state per client and users can
freely switch between services without incurring redundant
computational effort."

## Zerocash background as the paper frames it (Section 1)

- Notes encapsulate spendable value (amount, owner identity,
  metadata). A transaction consumes existing notes and creates new
  ones; it publishes commitments to the new notes, a zero-knowledge
  proof of correctness, and a NULLIFIER per spent note to prevent
  double-spending. Validators verify the proof and check the
  nullifier is unique.
- "Valid transactions have their note commitments inserted into an
  accumulator. Canonically in Zerocash, the accumulator is a Merkle
  tree, though we will refer to it abstractly as other approaches are
  possible." KEY: the note-commitment accumulator is abstract and
  UNCHANGED; the accumulator state (e.g. the Merkle root) is the
  public input called the ANCHOR; the membership witness (e.g. the
  Merkle path) is private.
- The ZK proof is a program checking: Existence (spent notes are
  well-formed and their commitments exist in the global accumulator
  at the anchor); Authorization (spender knows the keys); Balance
  Integrity (value conservation, no counterfeiting); Nullifier
  Correctness (nullifiers computed deterministically from the spent
  notes; "ideally, a nullifier is an output of a pseudo-random
  function applied to the note and keyed on a secret known to the
  spender").
- Framing used throughout: transaction validation is two programs,
  the client's local checks (proven in ZK) and the validators'
  global checks; "accumulators and nullifiers are a crucial
  communication boundary between those two programs, through which
  the validators learn that the note being spent exists and was not
  already spent, but do not learn the note's (and hence the
  sender's) identity." The same structure applies to
  privacy-preserving smart contracts (Zexe, Aleo, Aztec, Miden),
  with balance integrity generalised to an execution kernel.

## The two scaling costs (Section 1.1)

1. Proof verification: more expensive than an ECDSA check, but
   "amortized away as individual transaction proofs can be aggregated
   into a single batch proof (e.g., via recursive proofs). In the
   limit, the validation cost for an entire block could be reduced to
   verifying just one proof."
2. Nullifier tracking (the significant one): "validators must still
   track nullifiers. The perpetually growing nullifier set ... grows
   linearly with the number of transactions that have ever occurred."
   Concrete: a transaction consuming two notes reveals two 32-byte
   nullifiers; "at 100 transactions per second, the nullifier set
   would grow by half a GB each day", far more at Visa scale (Visa
   ~322 billion tx/year, ~10,000 tps, 65,000 tps capacity per their
   footnote). Nullifier data "must be stored online and readily
   accessible to allow double-spend checks", unlike ordinary tx
   history which can be offloaded to an archival node. This is a
   scaling limitation UNIQUE to anonymous payments.

Prior pruning approaches the paper surveys:
- (a) Expire notes and nullifiers once old: users must move funds
  into a new note once per window or lose them; at scale this might
  be weekly or daily.
- (b) "More promising": modify the ZK proof to check the note is not
  already spent, providing an ACCUMULATOR for nullifiers and having
  the proof compute the nullifier and check NON-membership. Block
  boundaries give a clear cutoff for past transactions; the nullifier
  must still be revealed to catch CONCURRENT double-spends in the
  same block (validators still dedup within the block); "we may make
  unspent proofs relative to an older block to increase stability".
  The most promising known techniques "center around the idea of
  periodically freezing the active nullifier set for an 'epoch',
  collecting it into an accumulator, and requiring users provide
  non-membership proofs for prior epochs when spending their notes."
  This runs into the accumulator update problem (Section 1.2).

## The tyranny of accumulator updates (Section 1.2)

- To prove (non-)membership you need a witness w (e.g. Merkle
  siblings), and "this witness must be updated as notes or nullifiers
  are added ... naively, each client must process every block in
  order to update their witnesses. At any reasonable scale, this is
  cost prohibitive." (This IS the witness-update problem of eprint
  2025/234.)
- Membership vs non-membership asymmetry, stated explicitly: "For
  membership proofs, once a client has an initial witness to their
  note's existence, updates to membership proofs can be batched,
  saving the client a constant factor. However, for non-membership
  proofs, e.g., to prove that a nullifier is not already spent, we
  run into an additional problem: clients cannot compute the initial
  non-membership proof without access to the full nullifier history.
  There are a variety of tricks to reduce this problem, but known
  lower bounds for accumulators that make it difficult to eliminate
  [10]." Reference [10] is Christ, Bonneau, "Limits on revocable
  proof systems" (eprint 2022/1478), the SAME authors/lineage as the
  2025/234 MMR-optimal lower bound. So the paper anchors the
  non-membership difficulty in the accumulator lower-bound
  literature.
- Why not just outsource witness computation? Privacy: "computing an
  accumulator witness (for membership of a note or non-membership of
  a nullifier) leaks exactly the element the proof is for. In
  particular, a client outsourcing such operations for multiple
  notes/nullifiers would link those notes together and reveal they
  are owned by the same user. This is a fundamental privacy
  violation", worsened because such nodes are often part of the
  network (Sybil/surveillance risk).

## Evolving nullifiers (Section 1.3, the core mechanism)

The dilemma: (a) clients download/store the entire ever-growing spent
nullifier set to prove their own is unspent, or (b) lose privacy by
outsourcing. "Our approach resolves this conflict not by trying to
fix the accumulator, but by making the nullifier itself evolve over
time, allowing old versions to be safely revealed."

Construction, verbatim: modify the nullifier from
`eta <- PRF(k_note, rho)` to `eta <- PRF(k_note, rho || e)`, where
`k_note` is a key bound to the note, `rho` is a nonce, and `e` is "a
monotonic counter known as an epoch identifier", incremented per
block WLOG (in practice less frequently). "`e` is revealed publicly
in spends and validators enforce the epoch is current in addition to
the existing double-spend check."

- Within one epoch: the same nullifier is deterministically generated
  for all spends of a note, so the existing dedup check suffices;
  "validators maintain a database of that epoch's spent nullifiers."
- Across epochs: the nullifier changes, so dedup cannot catch it.
  "Instead, we must ensure that every previous version of the
  nullifier is also unspent." Revealing previous versions would put
  validators back to storing all history; instead "we outsource this
  check to an untrusted third party oblivious syncing service who
  produces an incremental unspent proof that clients incorporate into
  their transactions. Because nullifiers evolve and different
  versions are unlinkable, these old nullifiers can safely be
  outsourced while the client maintains the latest nullifier(s)."

The incremental unspent proof, two key properties (verbatim):
1. "it can be computed incrementally. Given a proof that previous
   nullifier versions up to epoch i-2 were unspent and a proof that
   the nullifier version for i-1 is well-formed, we can create a new
   proof (via recursive proof composition) that the nullifier for
   epoch i-1 was also unspent."
2. "this proof requires no sensitive information from the client; its
   components are only what the client would have revealed if they
   had spent in epoch e_{i-1}. So each incremental update to this
   proof can be computed by a completely untrusted party."

Timing/linkage hazard and its fix (verbatim): wallets hold multiple
notes and "may update their unspent proofs at the same (or
correlated) time, such as when first turned on after a period of
inactivity, or charging on WiFi at home. Transactions spending these
notes to different parties could still be linked together by their
use of incremental unspent proofs that were computed at correlated
times. This is not a small problem; in fact, it would be fatal to the
entire approach." Fix: "it is essential that the syncing service is
incapable of distinguishing transactions they assisted with and ones
they did not. This problem can be generally addressed by
re-randomizing the proof, as many recursive proof systems permit,
such as those involving accumulation schemes [9]." Reference [9] =
Bunz, Chiesa, Mishra, Spooner, "Proof-carrying data from accumulation
schemes" (eprint 2020/499), i.e. the PCD-from-accumulation basis
(the Ragu/Halo lineage).

## Batching and a data-availability layer (Section 1.4)

- Batching: "the synchronization service can compute one proof for a
  batch of disparate transactions from different clients. Various
  efficient batched non-membership proofs exist [7;16]" ([7] =
  Boneh-Bunz-Fisch batching for accumulators, CRYPTO 2019; [16] =
  Ozdemir, Wahby, Whitehat, Boneh, "Scaling verifiable computation
  using efficient set accumulators", USENIX Security 2020), "and
  there is the possibility of co-designing a specific proof system
  and accumulator to improve performance."
- Data-availability layer: instead of ad-hoc oblivious syncing
  services, build a DA layer [2] (Al-Bassam, Lazyledger) that stores
  old nullifiers so the network need not depend on volunteers'
  goodwill and the main chain need not store them forever. This
  splits the system into a TRANSACTION LAYER (validates proofs incl.
  the incremental unspent proofs, checks double-spends for the
  current epoch) and a DA LAYER (stores the past-epoch nullifier
  database, runs oblivious syncing services). The DA layer "could
  readily be set up as a Proof-of-Stake (PoS) network independent of
  the consensus mechanism for the underlying transaction layer
  (which, e.g., in Zcash is Proof-of-Work)."
- Epoch-length tradeoff (the paper's closing caution): the need for a
  DA layer is "a direct function of epoch length." Long epochs
  (years) can be supported organically by exchanges/wallet providers/
  hobbyists; but "to achieve a scale approaching that of traditional
  payment providers, epochs must become much shorter -- perhaps even
  as short as a single block", and then "the historical nullifier
  database grows so large that it can only be stored by a few highly
  centralized providers ... This could introduce a critical point of
  failure, where the sudden shutdown of these services could render
  the funds of all their dependent users unspendable, potentially
  permanently."

## Corrections to the earlier blog-based Tachyon note

Reading the paper corrects two things in
`notes/tachyon-zcash-shielded-protocol.md` that were taken from the
blog and were fuzzier there:

1. The NOTE-COMMITMENT accumulator is NOT replaced. The paper keeps
   it abstract ("canonically a Merkle tree"), unchanged, with an
   anchor as public input and a membership witness as the private
   part. The blog's "potentially also note commitments [into a new
   accumulator]" is a mentioned possibility, NOT what the paper does.
   Tachyon's innovation here is entirely on the NULLIFIER
   (non-membership) side. Correct the note's "concrete structure ...
   possibly replaced" wording: the note-commitment membership
   accumulator stays; only the nullifier handling changes.
2. The nullifier mechanism is not primarily "a new PCD-friendly
   non-membership accumulator" (blog phrasing). The paper's actual
   mechanism is EVOLVING NULLIFIERS (epoch-keyed PRF) plus an
   INCREMENTAL UNSPENT PROOF built by recursive proof composition and
   computed by an untrusted oblivious syncing service, RE-RANDOMIZED
   to avoid timing linkage. The accumulator-of-nullifiers with
   non-membership proofs is described as the prior "more promising"
   approach that hits the update problem; evolving nullifiers is what
   lets the check be safely outsourced instead.

## Use in the paper

- Section 8 (Zcash case study) / the Tachyon subsection: use this
  paper as the primary, formal source. The clean story for our paper
  is the MEMBERSHIP vs NON-MEMBERSHIP asymmetry stated in Section
  1.2: for the append-only note-commitment tree (our paper's core),
  membership-witness updates are "batchable, saving a constant
  factor" but still bounded below by omega(n) total (eprint 2025/234)
  and shardtree engineers within that; for the nullifier set (the
  DUAL, non-membership problem), initial non-membership proofs need
  the full history and are hard to eliminate by known lower bounds
  ([10] Christ-Bonneau), and Tachyon's evolving-nullifier +
  oblivious-synchronization design is the escape hatch, moving the
  cost to an untrusted service that learns nothing.
- This gives the paper a clean two-column framing: MEMBERSHIP
  (note commitments, append-only, MMR/shardtree, 2025/234 bound) vs
  NON-MEMBERSHIP (nullifiers, revocation, evolving nullifiers +
  oblivious sync, 2022/1478 bound). Same witness-update tyranny,
  dual structures, different escapes.
- The re-randomization-via-accumulation-PCD point ([9] Bunz et al
  2020/499) connects to Ragu/Halo and to our proof-system remarks.
- references.bib to add: this paper (2025/2031, Bowe & Miers);
  supporting refs it leans on that our paper may also cite:
  Christ-Bonneau 2022/1478, Bunz et al PCD-from-accumulation
  2020/499, Boneh-Bunz-Fisch batching (CRYPTO 2019), Ozdemir et al
  set accumulators (USENIX Sec 2020), Zerocash (S&P 2014), Zexe
  (S&P 2020), Al-Bassam Lazyledger DA.
