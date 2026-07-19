# Tachyon (Zcash next-gen shielded protocol) and witness maintenance

- Designer: Sean Bowe (Electric Coin Co.), with the ECC team.
- Primary sources:
  - Sean Bowe, "Tachyon: Scaling Zcash with Oblivious
    Synchronization", seanbowe.com, 2025-04-02,
    <https://seanbowe.com/blog/tachyon-scaling-zcash-oblivious-synchronization/>.
  - Sean Bowe, "Tachyaction at a Distance", seanbowe.com,
    2025-05-15.
- Secondary (corroborating, NOT primary-verified): tachyon.z.cash
  overview; ZK Podcast ep. 388 with Bowe; CoinDesk / Messari
  coverage; TOKEN2049 2025 talk; the "Ragu" recursive-proof / PCD
  framework (Halo, Pasta curves). Treat NU7 targeting, curve choices,
  and the Ragu name as secondary until confirmed against a primary
  source.
- Accessed: 2026-07-19.
- Status: VERIFIED against the two primary blog posts via a
  deep-research pass with 3-vote adversarial verification; 10 claims
  survived, 0 refuted, each supported by verbatim quotes from Bowe's
  posts (evidence retained in the workflow journal for run
  wf_c6c903e3-fc8). The research pass was STOPPED before full
  synthesis; this note is written from the verified claims, which
  cover the load-bearing design. Tachyon is a DESIGN PROPOSAL in
  progress (announced 2025), not deployed; every "does X" below means
  "is designed to do X".

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
   changes is who maintains the witness and how.
5. Global pruning. "Almost everything in a block can be permanently
   pruned by validators and ultimately all users of the system as
   well"; Tachyon "allows validators to begin pruning all old
   blockchain state." The PCD proof carries the needed history, so
   the chain need not retain it.
6. Out-of-band payments. "Tachyon fully embraces out-of-band payments
   for the first time in a Zcash shielded protocol" and "removes
   in-band secret distribution"; consequently "the on-chain
   ciphertexts can then be removed from the protocol entirely". The
   motivation is scanning cost: "recipients identify incoming
   payments by trial decrypting every transaction ... this simply
   does not scale."
7. Acknowledged tradeoff. "The user cannot rely on the blockchain as
   a storage mechanism for recovering their funds from a seed phrase
   or sharing transaction histories with view keys", so Tachyon
   "will need additional infrastructure for our wallets to store and
   distribute payment information privately."

## Relation to the canonical property set

The paper's ten properties, and where Tachyon puts each. "Kept",
"sidestepped", or "moved to another party".

1. append: KEPT. Still an append-only accumulator of note
   commitments at consensus.
2. sparse witnesses: KEPT in spirit, MOVED in practice. A wallet
   still spends its own notes via inclusion witnesses, but the
   witness is maintained by the oblivious syncing service and folded
   into PCD, not stored/updated leaf-by-leaf by the wallet.
3. pruning: STRENGTHENED and GLOBAL. Not just wallet-side pruning of
   unneeded interior nodes (shardtree), but validators and all users
   pruning ALL old blockchain state, because the PCD proof carries
   the history the pruned data used to authenticate.
4. out-of-order insertion: not addressed by the primary sources;
   OPEN. (shardtree's concern; Tachyon's writing does not speak to
   the insertion order of the underlying accumulator.)
5. bounded checkpoints: not addressed directly; OPEN. Recent-anchor
   spending still implies a bounded root history at consensus, but
   Tachyon's posts do not discuss a checkpoint bound as such.
6. proof update when new elements are added: MOVED / TRANSFORMED.
   This is the core move. The per-append witness update is not
   eliminated globally (the eprint 2025/234 bound still applies to
   the accumulator); it is (a) moved off the wallet onto the
   oblivious syncing service, and (b) re-expressed as advancing a PCD
   proof of wallet-state correctness rather than editing a Merkle
   path. The work does not vanish; the WALLET stops doing it.
7. bounded memory footprint: ACHIEVED for the wallet, in a strong
   form. The wallet keeps a constant-size PCD proof of its state
   instead of witnesses whose upkeep scales with chain growth; the
   chain itself shrinks via global pruning. The storage burden moves
   to the syncing service and to out-of-band wallet infrastructure.
8. rewind: not addressed; OPEN.
9. verification against recent anchors: KEPT verbatim. Spends prove
   membership "at some (usually recent) anchor that validators
   accept as valid".
10. witness-update-frequency metric: this is the lens that makes
    Tachyon legible. Tachyon does not lower the omega(n) TOTAL
    witness-update count that eprint 2025/234 forces on the
    accumulator; it changes WHO PAYS it (oblivious syncing services,
    once per note-relevant event, learning only a nullifier) and the
    REPRESENTATION (PCD proof vs stored path). The lower bound is the
    reason Tachyon must move the cost rather than remove it; this is
    the paper's cleanest illustration of "the bound is unbeatable, so
    the engineering is about relocating the work".

## Open / unconfirmed (need primary sources or manual eprint)

- The exact accumulator structure Tachyon uses (still the depth-32
  Orchard note-commitment tree? a different append-only accumulator?
  the posts say "an accumulator" generically).
- Nullifier-set membership / double-spend handling under the reversed
  derivation (how validators check nullifier freshness).
- Whether any part of Tachyon's construction is written up in an
  eprint paper (if so, it must be supplied manually per the eprint
  rule; the primary sources here are blog posts, not eprint).
- ZIP number(s), NU7 targeting, prototype code locations
  (librustzcash / seanbowe repos), and the Ragu framework details:
  all secondary; confirm before citing.

## Use in the paper

- Section 8 (Zcash case study): add Tachyon as the forward-looking
  counterpart to shardtree. Framing: shardtree engineers WITHIN the
  witness-update lower bound (lazy fast-forward against shard roots);
  Tachyon's design question is whether the wallet can stop carrying
  that cost at all, answered by moving synchronization + witness
  maintenance to an oblivious syncing service and representing wallet
  state as PCD. Neither beats eprint 2025/234; both relocate its
  cost.
- Section 6/10: Tachyon is the concrete motivation for stating the
  witness-update lower bound as an ENGINEERING boundary, and for the
  "which party pays" framing in the conclusion.
- Cite the two Bowe posts as primary; keep secondary claims
  (curves, NU7, Ragu) out until primary-verified.
