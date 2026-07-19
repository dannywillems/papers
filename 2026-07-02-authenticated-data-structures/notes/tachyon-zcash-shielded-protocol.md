# Tachyon (Zcash next-gen shielded protocol) and witness maintenance

- Designer: Sean Bowe (co-designer of Zcash's Sapling/Orchard; left
  Electric Coin Co. in 2024). Tachyon is now developed by an
  independent `tachyon-zcash` team and presented as a
  COMMUNITY-PROPOSED Zcash upgrade, NOT an ECC-shipped one. (Earlier
  draft of this note wrongly attributed it to ECC; corrected
  2026-07-19.)
- Primary sources:
  - Sean Bowe, "Tachyon: Scaling Zcash with Oblivious
    Synchronization", seanbowe.com, 2025-04-02,
    <https://seanbowe.com/blog/tachyon-scaling-zcash-oblivious-synchronization/>.
  - Sean Bowe, "Tachyaction at a Distance", seanbowe.com, 2025-05-15,
    <https://seanbowe.com/blog/tachyaction-at-a-distance/>.
  - Sean Bowe, "Ragu for Orchard: Recursion Al Dente", seanbowe.com,
    2025-04-17, <https://seanbowe.com/blog/ragu-for-orchard-part1/>.
  - tachyon.z.cash overview and roadmap
    (<https://tachyon.z.cash/overview/>,
    <https://tachyon.z.cash/roadmap/>);
    "Folding Tachyon with Ragu", tachyon.z.cash blog, 2026-05-07.
  - Ragu source: <https://github.com/tachyon-zcash/ragu>.
  - FORMAL WRITE-UP: IACR eprint 2025/2031, "A Note on Notes: Towards
    Scalable Anonymous Payments via Evolving Nullifiers and Oblivious
    Synchronization", Sean Bowe and Ian Miers, Nov 2025. This is the
    academic paper behind Tachyon's core. READ WHOLE first-hand on
    2026-07-19 from the manually-supplied local PDF; dedicated
    verified note at `notes/bowe-miers-2025-a-note-on-notes.md`. It
    resolves and in two places CORRECTS the blog-based understanding
    (see design items 5-6 and the corrections in that note): the
    note-commitment accumulator is NOT replaced (abstract, Merkle,
    unchanged); the nullifier mechanism is EVOLVING NULLIFIERS plus an
    oblivious-syncing incremental unspent proof, not primarily a new
    accumulator.
- Secondary (corroborating, NOT primary-verified): ZK Podcast ep. 388
  with Bowe (2026-01-21); CoinDesk / Messari coverage; TOKEN2049 2025
  talk.
- Accessed: 2026-07-19.
- Status: VERIFIED against the primary blog posts, the tachyon.z.cash
  site, the Ragu repo (via a deep-research pass, 10 core claims, 0
  refuted, plus three targeted follow-up agents) AND the formal paper
  eprint 2025/2031, read whole first-hand (dedicated note
  `notes/bowe-miers-2025-a-note-on-notes.md`). Verbatim quotes below
  are from the cited primary sources. Tachyon is a DESIGN PROPOSAL in
  active R&D (announced 2025), not deployed; every "does X" means "is
  designed to do X". With the paper read, the accumulator/nullifier
  construction is no longer an open gap; see design items 5-6.

## Why this is directly relevant to the paper

Tachyon's stated motivation IS the witness-update problem this paper
is about. Bowe names the current bottleneck verbatim: "all other
users must account for the newly created note commitments by updating
their set inclusion witnesses for all of their unspent shielded
notes." That is exactly the per-append witness maintenance that
shardtree engineers around and that eprint 2025/234 proves cannot be
driven below omega(n) total for any succinct append-only accumulator.
Tachyon is the design that tries to get the per-wallet cost of that
work to (near) zero, and it is instructive precisely because it does
NOT beat the lower bound: it MOVES the work to another party and
changes the wallet's representation of its own state.

## The design (all verified against the primary posts)

1. Wallet state as proof-carrying data (PCD). "We will also represent
   our wallet's state as proof-carrying data. This means that as the
   wallet state updates to reflect new blocks it will continually
   maintain a proof of its own correctness." Instead of storing and
   re-deriving Merkle witnesses, the wallet carries a recursive proof
   that its current state correctly follows from the chain. (Realized
   via recursive / accumulation-based proving; the specific
   curves/framework are secondary.)
2. Oblivious syncing service. "The user's wallet can outsource the
   process of synchronizing the wallet (and creating the PCD proofs)
   to a third party that I call an oblivious syncing service." It
   "can still make progress synchronizing its state even when the
   user's wallet software is offline", and "only needs to learn the
   nullifier of the note to make synchronization progress ... since
   the wallet can blind or encrypt the rest of the wallet state".
   PCD is chosen over FHE for this ("we already know that this kind
   of approach is possible with expensive cryptography like
   fully-homomorphic encryption ... but by adjusting the protocol
   slightly we can simply use PCD").
3. Reversed nullifier derivation. Nullifiers "are not determined by
   the note commitment but rather the other way around". Purpose:
   "depriving the service of any information about the note being
   spent", so the oblivious syncing service cannot link nullifiers
   back to note positions/identities.
4. Spend model, unchanged in shape. "Shielded transactions
   demonstrate that the note they are spending exists at some
   (usually recent) anchor that validators accept as valid", via "a
   set inclusion witness that demonstrates a commitment exists within
   an accumulator". So Tachyon keeps an append-only accumulator of
   note commitments and keeps recent-anchor verification; what
   changes is who maintains the witness and how. The anchor
   machinery is described exactly as today: "validators continually
   append the new note commitments that appear in shielded
   transactions to a cryptographic accumulator", and "at block
   boundaries, the accumulator is checkpointed and a succinct (hash)
   representation of that checkpoint is stored by validators. We call
   this checkpoint an 'anchor.'"
5. The note-commitment accumulator: UNCHANGED (this is the paper's
   authoritative answer; corrects the blog-based reading). Per eprint
   2025/2031 Section 1: "Canonically in Zerocash, the accumulator is
   a Merkle tree, though we will refer to it abstractly as other
   approaches are possible." The accumulator state (Merkle root) is
   the public ANCHOR; the membership witness (Merkle path) is
   private. The paper does NOT replace or migrate the note-commitment
   structure; its entire contribution is on the nullifier
   (non-membership) side. The blog's "(and potentially also note
   commitments) ... into a new accumulator" was a floated
   possibility, NOT what the formal design does. So: the append-only
   note-commitment membership accumulator stays (still needs
   membership-witness maintenance, which the paper notes is "batchable
   ... saving a constant factor" but is still the omega(n)-bounded
   problem of eprint 2025/234, addressed by shardtree, NOT by this
   paper). Treat the secondary "vector-commitment accumulator with
   constant-size state" claim as unsupported.
6. Nullifiers: EVOLVING NULLIFIERS plus an oblivious-syncing
   incremental unspent proof (the paper's actual, formal mechanism;
   supersedes the blog's "reversed derivation into a new accumulator"
   phrasing). Baseline problem: the nullifier set grows linearly
   forever and "must be stored, queried and updated by all validating
   nodes" (~0.5 GB/day at 100 tps). Mechanism (eprint 2025/2031
   Section 1.3):
   - Evolving nullifier: change `eta <- PRF(k_note, rho)` to
     `eta <- PRF(k_note, rho || e)` where `e` is a monotonic EPOCH
     identifier (per block WLOG), revealed publicly; validators
     enforce the epoch is current. (This is the precise form of the
     blog's "reversed derivation": the nullifier is now a function of
     an epoch counter, so it changes over time and old versions are
     unlinkable to the current one.)
   - Within an epoch: the nullifier is fixed, so the ordinary dedup
     check catches same-epoch double-spends; validators keep only the
     CURRENT epoch's spent-nullifier database.
   - Across epochs: the client must show every PREVIOUS epoch version
     was also unspent, WITHOUT revealing them (which would restore
     the storage problem). This is an INCREMENTAL UNSPENT PROOF: a
     recursive-proof-composed non-membership proof, extended one
     epoch at a time, that "requires no sensitive information from the
     client" and so can be built by a "completely untrusted party",
     the oblivious syncing service. Because old nullifier versions are
     unlinkable, outsourcing leaks nothing.
   - Linkage hazard and fix: correlated proof-update timing across a
     wallet's notes "would be fatal to the entire approach"; the proof
     is RE-RANDOMIZED (as accumulation-scheme PCD permits, ref Bunz et
     al 2020/499) so the service cannot tell which transactions it
     helped with.
   Net effect on validators: they keep only the current epoch's
   nullifiers and verify the incremental unspent proof for the past;
   old-epoch nullifier state is permanently prunable. That is what
   makes nullifier pruning sound.
7. Global pruning. "Almost everything in a block can be permanently
   pruned by validators and ultimately all users of the system as
   well"; Tachyon "allows validators to begin pruning all old
   blockchain state." The PCD proof carries the needed history, so
   the chain need not retain it. This is a stronger pruning claim
   than shardtree's (which prunes wallet-side interior nodes not
   needed for marked witnesses): here the CONSENSUS state itself
   (old note commitments AND the old nullifier set) becomes
   discardable, because correctness is carried by proofs rather than
   by retained data.
8. Out-of-band payments. "Tachyon fully embraces out-of-band payments
   for the first time in a Zcash shielded protocol" and "removes
   in-band secret distribution"; consequently "the on-chain
   ciphertexts can then be removed from the protocol entirely". The
   motivation is scanning cost: "recipients identify incoming
   payments by trial decrypting every transaction ... this simply
   does not scale." A stated side effect ("Tachyaction at a
   Distance"): removing in-band secret distribution also yields full
   post-quantum privacy, since there is no on-chain ciphertext to
   harvest-now-decrypt-later.
9. Acknowledged tradeoff. "The user cannot rely on the blockchain as
   a storage mechanism for recovering their funds from a seed phrase
   or sharing transaction histories with view keys", so Tachyon
   "will need additional infrastructure for our wallets to store and
   distribute payment information privately."

## The proving system (Ragu) and status (verified)

- Ragu (`github.com/tachyon-zcash/ragu`) is Tachyon's proof-carrying
  data layer: "a Rust-language proof-carrying data (PCD) framework
  that implements a modified version of the ECDLP-based recursive
  SNARK construction from Halo [BGH19] ... Ragu does not require a
  trusted setup." It "aims to be a production-grade realization of
  the original Halo paper", over "the Pasta elliptic curve cycle",
  with "the original Poseidon algebraic hash function" and
  "univariate polynomial multi-commitment schemes using inner product
  arguments"; it uses an R1CS-like arithmetization with lookup
  escape hatches, split accumulation/folding, and largely avoids
  FFTs. So it is Halo-lineage (recursive Bulletproofs / BCCGP16),
  NOT PLONK/KZG, and trusted-setup-free. Underlying construction:
  Halo (Bowe, Grigg, Hopwood, IACR eprint 2019/1021). Ragu status:
  public but "under heavy development and has not undergone
  auditing. Do not use this software in production" (repo), MIT/
  Apache-2.0 dual-licensed.
- Specification / ZIP: none yet. The NU7 candidate-ZIP set (ZIP 218,
  230, 231, 233/234/235, 2002, 2003) does NOT include Tachyon, and
  tachyon.z.cash/roadmap says the shielded protocol is still being
  designed, "deployed on testnet after review", with a ZIP not yet
  written. eprint 2025/2031 is the nearest thing to a spec.
- Network-upgrade targeting: UNCONFIRMED. Primary sources
  (tachyon.z.cash, z.cash/upgrade/nu7) do NOT pin Tachyon to NU7;
  z.cash/upgrade/nu7 does not mention Tachyon at all. Secondary
  outlets (zcashtracker, crypto.news, CoinDesk) assert NU7 inclusion,
  conflating the NU7 timeframe with Tachyon; treat "Tachyon is in
  NU7" as unconfirmed. Best current read: a POST-NU7 upgrade,
  community approval pending. Bowe's Apr-2025 aspiration was "many of
  the major scalability improvements should be able to hit mainnet
  within a year" (not met as a single upgrade).
- Prototype code: Ragu (the proving layer) is the one active public
  repo; the shielded-protocol / payment-protocol code is NOT public
  and remains design-stage. No Tachyon branch was found in
  zcash/librustzcash or zcash/orchard.
- Roadmap workstreams (tachyon.z.cash/roadmap), all in progress:
  (1) Ragu (PCD scheme), in optimization + auditing; (2) payment
  protocol (two candidate approaches: PIR + post-quantum key exchange
  for privacy, vs more-scalable infrastructure-based designs);
  (3) shielded protocol (simplified key structure enabling oblivious
  sync + shielded aggregation), to testnet after review.
- Stated open problems (Bowe, Apr 2025): wallet migration from legacy
  payment protocols; network-privacy countermeasures (mixnets) so
  oblivious-sync servers cannot correlate evolving nullifiers;
  building the oblivious-syncing-service infrastructure; PCD-toolkit
  performance benchmarks (proving Ragu is fast enough); removing
  in-band secret distribution.

## Relation to the canonical property set

The paper's ten properties, and where Tachyon puts each. "Kept",
"sidestepped", or "moved to another party".

Framing correction after reading eprint 2025/2031: Tachyon touches
TWO distinct authenticated structures, and our property set is about
the first. (i) The note-commitment tree: an append-only MEMBERSHIP
accumulator, our paper's core; Tachyon leaves it UNCHANGED (abstract,
Merkle), and its membership-witness maintenance is the omega(n)
problem of eprint 2025/234 that shardtree engineers within, NOT what
Tachyon solves. (ii) The nullifier set: a NON-membership / revocation
structure (the dual problem), where Tachyon's evolving-nullifier +
oblivious-synchronization design lives. The per-property mapping below
is about structure (i) unless noted; structure (ii) is the additional
axis in items 3, 7, and 10.

1. append: KEPT. Validators still "continually append the new note
   commitments ... to a cryptographic accumulator" and checkpoint it
   to anchors at block boundaries. Append is unchanged at consensus.
2. sparse witnesses: KEPT in spirit, MOVED in practice. A wallet
   still spends its own notes via inclusion witnesses against an
   anchor, but the witness is maintained by the oblivious syncing
   service and folded into the wallet-state PCD, not stored/updated
   leaf-by-leaf by the wallet. The "marked subset" is still the
   wallet's own notes; the maintenance of their witnesses is what
   moves off-wallet.
3. pruning: STRENGTHENED to GLOBAL CONSENSUS pruning. Not just
   wallet-side pruning of interior nodes unneeded for marked
   witnesses (shardtree), but validators and ultimately all users
   pruning ALL old blockchain state, INCLUDING the historical
   nullifier set, because the PCD proof carries the history the
   pruned data used to authenticate. This is a categorically stronger
   pruning than the property-3 wallet-side pruning in our set: it
   discards CONSENSUS state, not just local bookkeeping.
4. out-of-order insertion: not discussed in the primary sources;
   OPEN. Tachyon's writing does not speak to the insertion order of
   the underlying accumulator. (Likely irrelevant at consensus, where
   commitments append in block order; it was shardtree's concern
   because wallets sync ranges non-sequentially, and under oblivious
   sync that concern moves to the syncing service. Inference, not
   stated.)
5. bounded checkpoints: PARTIALLY ADDRESSED. Recent-anchor spending
   plus the "check only the most recent block(s)" nullifier rule both
   imply a bounded recent window at consensus, which is the
   checkpoint-bound idea in a different guise; but Tachyon's posts do
   not frame it as a fixed checkpoint count, and the window size is
   unspecified. Call it "implied, not quantified".
6. proof update when new elements are added: SPLIT by membership vs
   non-membership. For the note-commitment MEMBERSHIP witness
   (structure i): the paper says updates are "batchable, saving a
   constant factor" and the broader Tachyon vision moves them to the
   oblivious syncing service / wallet-state PCD; the omega(n) total
   (eprint 2025/234) still binds and is not what this paper attacks.
   For the nullifier NON-membership proof (structure ii): the hard
   case, since "clients cannot compute the initial non-membership
   proof without access to the full nullifier history" and known
   lower bounds ([10] Christ-Bonneau 2022/1478) make it hard to
   eliminate. Tachyon's escape is the evolving-nullifier + incremental
   unspent proof: the update is (a) moved onto the untrusted oblivious
   syncing service (which advances the proof from purely public info
   while the wallet is offline), and (b) re-expressed as a
   recursively-composed, re-randomized non-membership proof rather
   than a maintained accumulator witness. The work does not vanish;
   the wallet stops doing it and the representation changes from a
   maintained witness to a proof.
7. bounded memory footprint: ACHIEVED for the wallet in a strong
   form, and additionally for CONSENSUS. The wallet keeps a
   constant-size PCD proof of its state instead of witnesses whose
   upkeep scales with chain growth; validators shed the growing
   note-commitment history AND the growing nullifier set via global
   pruning (the nullifier set was previously unbounded: "validators
   currently remember all of the nullifiers seen before"). The
   storage burden moves to the oblivious syncing service and to the
   new out-of-band wallet infrastructure. So Tachyon targets bounded
   memory at BOTH the wallet and the validator, at the cost of new
   off-chain infrastructure.
8. rewind: not discussed; OPEN. (Reorg handling under PCD wallet
   state is not covered by the sources; presumably the PCD is
   re-derived to a recent anchor, but this is not stated.)
9. verification against recent anchors: KEPT verbatim. Spends prove
   membership "at some (usually recent) anchor that validators
   accept as valid"; the nullifier freshness check is likewise
   reduced to "the most recent block(s)".
10. witness-update-frequency metric: the lens that makes Tachyon
    legible. Tachyon does NOT lower the omega(n) TOTAL witness-update
    count that eprint 2025/234 forces on the accumulator; it changes
    WHO PAYS it (oblivious syncing services, learning only a blinded
    nullifier) and the REPRESENTATION (a recursive PCD proof vs a
    stored/edited path). The lower bound is precisely why Tachyon
    must RELOCATE the cost rather than remove it: no succinct
    append-only accumulator can escape omega(n) total updates, so the
    only degrees of freedom are which party performs them and in what
    form. This is the paper's cleanest real-world illustration of the
    lower bound as an engineering boundary. Bonus: Tachyon ALSO
    attacks a second growing-state cost the paper does not center on,
    the nullifier set, by moving from "remember every nullifier" to a
    PCD-checked non-membership accumulator; that is the same
    "prove-instead-of-retain" move applied to a non-membership
    structure rather than a membership one. Sharpened by eprint
    2025/2031: MEMBERSHIP updates (note commitments) are the
    easier, batchable case bounded by 2025/234; NON-membership
    updates (nullifiers) are the harder case bounded by Christ-Bonneau
    2022/1478, and are exactly where the evolving-nullifier trick is
    needed. Same witness-update tyranny, two dual structures, two
    different escapes.

## Open / unconfirmed (status after the follow-up research pass)

Resolved by the follow-up pass (2026-07-19):

- Nullifier / double-spend handling: ANSWERED at the design level
  (reversed derivation + new non-membership accumulator + PCD
  discharges history + validators check only recent blocks; see
  design item 6). Concrete construction still only "sketched" in the
  blogs.
- Academic write-up: FOUND. eprint 2025/2031, Bowe & Miers, "A Note
  on Notes". Central; must be supplied manually per the eprint rule.
- ZIP / NU7 / code / proving system: ANSWERED (no ZIP yet; NU7
  inclusion unconfirmed and likely post-NU7; Ragu is the one public
  repo, un-audited; proving system is Halo/Pasta/Poseidon,
  trusted-setup-free). See the status section.

Resolved by reading eprint 2025/2031 (2026-07-19):

- Note-commitment accumulator: UNCHANGED (abstract, canonically a
  Merkle tree, with an anchor as public input). NOT replaced, note
  commitments do NOT migrate. The blog's "potentially also note
  commitments" is not the formal design.
- Nullifier construction: evolving nullifiers (epoch-keyed PRF) +
  incremental unspent proof via recursive proof composition,
  outsourced to an oblivious syncing service and re-randomized. This
  is the concrete mechanism, not a single named accumulator.

Still genuinely open:

- The unpruned recent nullifier window: the paper says the epoch
  counter is "per block WLOG (in practice ... less frequently)" but
  does not fix the epoch length; it explicitly ties the need for a
  data-availability layer to epoch length (long epochs organic,
  single-block epochs force centralized nullifier storage).
- Reorg/rewind semantics under evolving nullifiers / PCD wallet
  state: not covered.
- The concrete proof system + accumulator co-design for batched
  non-membership: flagged as future possibility ([7;16]), not
  specified.
- A firm network-upgrade target and mainnet date: none stated;
  Tachyon is not in the NU7 candidate-ZIP set.

## Sources now fully read

eprint 2025/2031 has been supplied manually and read whole; see the
dedicated verified note `notes/bowe-miers-2025-a-note-on-notes.md`.
The only optional remaining background is Halo (eprint 2019/1021) for
the Ragu proving system, which is well-known and non-central; fetch
only if the paper's proof-system section is written in detail.

## Use in the paper

- Section 8 (Zcash case study): add Tachyon as the forward-looking
  counterpart to shardtree. Framing: shardtree engineers WITHIN the
  witness-update lower bound (lazy fast-forward against shard roots);
  Tachyon's design question is whether the wallet can stop carrying
  that cost at all, answered by moving synchronization + witness
  maintenance to an oblivious syncing service and representing wallet
  state as recursive PCD. Neither beats eprint 2025/234; both
  relocate its cost. Add the second axis Tachyon opens: the nullifier
  set (a growing NON-membership structure) gets the same
  prove-instead-of-retain treatment, letting validators prune it.
- Section 3/9 (accumulators, comparison): Tachyon's new PCD-friendly
  (non-)membership accumulator is a concrete modern data point for
  the accumulator comparison, ONCE eprint 2025/2031 is read and the
  construction is known; until then present it as "a
  proof-carried non-membership accumulator, construction in
  eprint 2025/2031".
- Section 6/10: Tachyon is the concrete motivation for stating the
  witness-update lower bound as an ENGINEERING boundary, and for the
  "which party pays, and in what representation" framing in the
  conclusion (data vs proof; wallet vs syncing service vs validator).
- Citations: cite the Bowe blog posts and eprint 2025/2031 (Bowe &
  Miers) as primary; the Ragu proving system via the repo, the
  tachyon.z.cash Ragu post, and Halo (eprint 2019/1021). Keep
  NU7-targeting OUT (unconfirmed). Add to references.bib once the
  eprint is read: 2025/2031, and Halo 2019/1021 if the proving
  system is discussed.
- Correctness note for the paper's prose: attribute Tachyon to Sean
  Bowe and the tachyon-zcash project (community-proposed), NOT to
  Electric Coin Co.; Bowe left ECC in 2024.
