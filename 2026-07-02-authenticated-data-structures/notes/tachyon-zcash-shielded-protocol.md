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
    academic paper behind Tachyon's core. eprint CANNOT be fetched by
    agents; number/title/authors reported from DBLP, tachyon.z.cash,
    and ZK news, NOT read. It must be supplied manually into
    `eprint/` per the eprint rule, then read whole; the concrete
    accumulator/nullifier construction that the blog posts only
    "sketch" is expected to live here.
- Secondary (corroborating, NOT primary-verified): ZK Podcast ep. 388
  with Bowe (2026-01-21); CoinDesk / Messari coverage; TOKEN2049 2025
  talk.
- Accessed: 2026-07-19.
- Status: VERIFIED against the primary blog posts, the tachyon.z.cash
  site, and the Ragu repo via a deep-research pass (3-vote
  adversarial verification, 10 core claims, 0 refuted) plus three
  targeted follow-up agents on the open items. Verbatim quotes below
  are from the cited primary sources. Tachyon is a DESIGN PROPOSAL in
  active R&D (announced 2025), not deployed; every "does X" means "is
  designed to do X". The one construction still unread first-hand is
  eprint 2025/2031 (see above).

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
5. The note-commitment accumulator: role unchanged, concrete
   structure NOT specified, possibly replaced. This is the most
   paper-relevant open point. The primary posts NEVER name the
   note-commitment structure: no "depth-32 incremental Merkle tree",
   no "Merkle Mountain Range", no "Verkle/RSA/vector commitment". The
   only statement about changing it is that Tachyon introduces a NEW
   accumulator for nullifiers and MAY move note commitments into it
   too: "Nullifiers (and potentially also note commitments) must be
   batch inserted into a new accumulator that supports efficient set
   (non-)membership testing in PCD. I've already sketched a very
   simple and efficient accumulation scheme for this." So per primary
   sources: the note-commitment accumulator keeps its role
   (append + checkpoint-to-anchor + set-inclusion witness), but
   whether the fixed depth-32 Orchard tree is retained, changed, or
   replaced by the new PCD-friendly accumulator is UNSPECIFIED in the
   blog posts; the new scheme is only "sketched", not given. A
   secondary explainer calls the new nullifier accumulator a
   "vector-commitment accumulator" with "constant-size state"; that
   phrasing is NOT in Bowe's posts and must be treated as secondary.
   The concrete construction is the thing eprint 2025/2031 is
   expected to pin down.
6. Nullifiers: reversed derivation, a new non-membership accumulator,
   and where the double-spend check goes. Today's baseline, stated by
   Bowe: "the nullifier ... serves as an indelible mark on the chain
   state that prohibits double-spends. Validators currently remember
   all of the nullifiers seen before and reject payments as invalid
   if they reveal a previously-seen nullifier." That ever-growing
   nullifier set is a target. Tachyon (a) reverses derivation
   (nullifiers "are not determined by the note commitment but rather
   the other way around", so the oblivious syncing service is
   deprived "of any information about the note being spent"); (b)
   batch-inserts nullifiers into the new accumulator "that supports
   efficient set (non-)membership testing in PCD"; and (c) discharges
   the FULL-HISTORY freshness check inside the wallet's PCD, so
   validators shrink to a recent window: "validators are now only
   responsible for ensuring that the transaction is correct in the
   presence of the additional transactions that appeared in the
   intervening time, which just involves checking that the most
   recent block(s) do not contain the revealed nullifier." This
   recent-window reduction is EXACTLY what makes global pruning
   sound: the historical non-membership is proven, not re-checked
   against retained state. Caveat: no single sentence says verbatim
   "the transaction carries a nullifier non-membership proof"; the
   design intent is strongly implied by (a)-(c) read together, not
   word-for-word asserted. How many "recent block(s)" the unpruned
   nullifier window spans is not specified.
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
6. proof update when new elements are added: MOVED and TRANSFORMED.
   The core move, and the single most paper-relevant point. The
   per-append witness update is NOT eliminated globally (the eprint
   2025/234 lower bound still binds any succinct append-only
   accumulator); it is (a) moved off the wallet onto the oblivious
   syncing service, which can advance the proof while the wallet is
   offline and learns only a (blinded) nullifier, and (b)
   re-expressed as advancing a recursive PCD proof of wallet-state
   correctness rather than editing a Merkle authentication path. The
   work does not vanish; the WALLET stops doing it, and its
   representation changes from data (a path) to a proof.
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
    structure rather than a membership one.

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

Still genuinely open:

- The CONCRETE note-commitment and nullifier accumulator
  construction. The blogs deliberately do not name it (no depth-32,
  no MMR) and only "sketch" the new PCD-friendly (non-)membership
  accumulator. This is the single most paper-relevant gap and is
  expected to be pinned down in eprint 2025/2031 (needs manual
  download). Until read, do NOT assert Tachyon uses/keeps/drops any
  specific structure.
- Whether note commitments actually migrate into the new accumulator
  ("potentially", per Bowe) or the Orchard tree is retained for
  commitments while only nullifiers move.
- The size of the unpruned recent nullifier window (how many blocks).
- Reorg/rewind semantics under PCD wallet state.
- A firm network-upgrade target and mainnet date (none stated).

## Action required (eprint rule)

To finish this note to "verified" on the accumulator/nullifier
construction, the human should download
<https://eprint.iacr.org/2025/2031.pdf> ("A Note on Notes", Bowe &
Miers) into `2026-07-02-authenticated-data-structures/eprint/`
(gitignored), after which it can be read whole and a verified note
written. Optionally also Halo (eprint 2019/1021) for the Ragu
proving-system background, though that is well-known and non-central.

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
