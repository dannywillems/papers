# The color model: reformulating the Zcash wallet problem

- Status: SYNTHESIS / modeling note (own work, not a source reading).
  It reformulates the Zcash/Tachyon wallet problem and the canonical
  property set using a "colored set" analogy, to serve as a candidate
  unifying framing for the paper's introduction and model section.
- Author's framing (verbatim): "one color = one user"; "A wallet must
  track all the elements of the set that haven't been used in another
  set (used nullifiers)"; a new wallet "MUST scan the whole set to
  fetch their colors ... only the user can see its own color in the
  set. For any other party, they're all the same." The last clause is
  the color-hiding (privacy) assumption used throughout: to anyone but
  the owner, every element looks the same, so no third party can tell
  which elements share a color or who owns them.
- Date: 2026-07-19. Related: `notes/bowe-miers-2025-a-note-on-notes.md`
  (evolving nullifiers, oblivious synchronization),
  `notes/tachyon-zcash-shielded-protocol.md`,
  `notes/zcash-protocol-spec-note-commitment-trees.md`, and the
  canonical property set in `PLAN.md`.

## 1. The model

There is one global, append-only SET of elements. Each element has
exactly one COLOR, and one color belongs to one user (a color IS a
user identity). Concretely, an element is a note commitment and its
color is its owner; the set is the note-commitment accumulator.

Two structures, not one:

- S, the COLORED SET (membership side). Elements e_1, e_2, ... are
  APPENDED to S and never removed. Each e_i carries a color c_i in a
  HIDDEN form: e_i is a commitment that hides its color.
- U, the USED SET (non-membership side). When an element is USED
  (spent), a MARKER for it is revealed and added to U. The marker is
  the nullifier.

Three cryptographic properties tie the model to reality:

1. Color-hiding (privacy). Given an element e_i, no party without the
   COLOR KEY of color k can decide whether c_i = k. Every element
   looks like a uniformly-random-colored one to outsiders; nobody can
   tell which elements share a color, nor who owns any of them. This
   is the author's clause: "only the user can see its own color in the
   set. For any other party, they're all the same."
2. Owner-only detection. The owner of color k holds a detection key
   dk_k with which they can TEST an element: t(dk_k, e_i) in
   {yes, no}, "yes" iff c_i = k. Testing is per-element (in today's
   Zcash it is trial decryption of the element's ciphertext). No
   cheaper detector exists for someone who does not hold dk_k, by
   property 1.
3. Marker unlinkability. The used-marker mu_k(e_i) reveals nothing
   about e_i: given a marker in U, no party (without dk_k and the
   element's secret) can find which element it marks, nor link two
   markers as sharing a color. With EVOLVING markers (Tachyon), the
   marker also carries an epoch t, and mu^(t) and mu^(t') for t != t'
   are mutually unlinkable, so old markers leak nothing about the
   current one.

## 2. The wallet's task

A wallet for color k must track its LIVE set: the elements of its own
color that have not yet been used.

  L_k(A) = { e_i in S_A : t(dk_k, e_i) = yes  AND  mu_k(e_i) not in U_A }

evaluated against an ANCHOR A, a recent snapshot (checkpoint) of S and
U that validators accept. To USE an element e in L_k, the wallet must
produce, against a recent anchor A:

- a MEMBERSHIP proof that e is in S_A (the element genuinely exists),
  i.e. an inclusion witness against the anchor; and
- a NON-MEMBERSHIP proof that mu_k(e) is not in U_A (the element is
  unused), i.e. the marker has not been seen.

Both proofs rest on WITNESSES that must be kept current as S and U
grow. This is the whole game: maintain, privately, the set of
own-color unused elements and the two witnesses needed to spend each.

## 3. The three problems, in color terms

The color model makes three distinct costs visible; the paper's
canonical property set addresses the second and touches the third,
but the FIRST is a prior problem the model surfaces cleanly.

### P1. Detection / scanning (finding your own color)

To even learn L_k, a wallet must find which elements of S have its
color. By owner-only detection (property 2) the only way is to TEST
elements one by one, and by color-hiding (property 1) NO other party
can do it for you without being handed dk_k, which would hand them
your color and destroy your privacy. So:

- A brand-new wallet (or one restoring from a seed) must scan the
  WHOLE set S, testing every element for its own color: O(|S|) work,
  and |S| grows forever.
- You cannot outsource the naive scan, because recognizing your color
  IS the private operation. "Only the user can see its own color; for
  any other party, an element's color is opaque."

This is the SCANNING problem, and it is one of the things Tachyon
targets. It is NOT a witness-maintenance problem; it is a
detection/private-information-retrieval problem, prior to any witness.

### P2. Membership-witness maintenance (keeping your elements provable)

For each element in L_k, the inclusion witness in S must be updated as
new (other-colored) elements are appended, because appending changes
the accumulator. Maintaining a witness per own-color element is the
SPARSE-WITNESS workload. Its unavoidable total cost is the
witness-update lower bound: omega(n) total updates over n appends for
any succinct append-only accumulator (eprint 2025/234). This is the
membership side, and it is what shardtree engineers within.

### P3. Used-set growth and non-membership (proving unused)

U grows forever and every validator must retain it to reject a
repeated marker (double-spend). Worse, proving mu_k(e) not in U is a
NON-membership statement that, naively, needs the full history of U;
initial non-membership witnesses cannot be formed without it, and
known lower bounds make this hard to eliminate (Christ-Bonneau,
eprint 2022/1478). This is the used-set (nullifier) side.

### The duality the colors expose

S (colored elements) is a MEMBERSHIP structure; U (used markers) is a
NON-MEMBERSHIP structure. A live coin is exactly
(in S with my color) AND (not in U). The same "witness must be
maintained as the set grows" tyranny hits both, with two different
lower bounds (2025/234 for membership, 2022/1478 for non-membership)
and two different escapes. The color model is the cleanest way to
state this duality: one predicate over two sets.

## 4. The canonical properties, reformulated in color terms

The ten properties (PLAN.md), each restated over the colored set S and
the used set U. Unless noted, "witness" means the own-color elements'
membership witnesses in S.

1. append: elements are only ever ADDED to S (and markers to U); no
   element is removed or recolored.
2. sparse witnesses: a wallet maintains witnesses only for elements
   of ITS color, a sparse and hidden subset of S, never for all of S.
3. pruning: discard the parts of S's (and U's) authentication
   structure not needed for the own-color unused elements and the
   retained anchors.
4. out-of-order insertion: own-color elements are scattered through S
   in append order set by everyone else; a wallet must incorporate
   them, and synced summaries of other-colored ranges, in any order.
5. bounded checkpoints: keep a bounded number of recent anchors
   (snapshots of S and U) to prove against.
6. proof update on append: as new (mostly other-colored) elements are
   appended to S, the own-color elements' membership witnesses must be
   updated; symmetrically, as markers are added to U, the unused
   (non-membership) proofs must be advanced.
7. bounded memory footprint: wallet state is bounded by the number of
   own-color UNUSED elements, the number of retained anchors, and the
   set depth, NOT by |S| or |U|. The wallet's memory scales with how
   much of ITS OWN color is live, not with the whole colored world.
8. rewind: restore to a past anchor (chain reorg) and recolor-forward
   correctly.
9. verification against recent anchors: prove own-color membership in
   S and marker-non-membership in U against a RECENT anchor, not only
   the latest snapshot.
10. metrics: the total membership-witness-update count over the life
    of S (the 2025/234 quantity), AND its non-membership dual over U
    (the 2022/1478 quantity), plus the per-use cost of a single
    fast-forward on each side.

The color model also surfaces an ELEVENTH concern the current set does
not name: DETECTABILITY / scanning cost (P1). The ten properties are
about maintaining witnesses for elements a wallet ALREADY KNOWS are
its own; detection is the prior step of learning which elements are
its own at all. Worth deciding explicitly whether the paper takes
detection as (a) an additional property, (b) an out-of-scope
assumption ("the wallet is given its own-color set"), or (c) a
separately treated problem. Recommendation: name it, then scope it,
so the paper does not silently conflate "maintain my witnesses" with
"find my coins".

## 5. Tachyon in color terms

Tachyon's three moves map cleanly onto the color model, and none of
them beats the two lower bounds; each RELOCATES the work.

- Out-of-band color transmission (attacks P1, scanning). Instead of
  embedding a color-bearing ciphertext in every element so recipients
  DETECT by scanning-and-testing, the color assignment is delivered
  to the recipient off-chain. A new wallet is then TOLD which elements
  are its color rather than discovering them by scanning S; the
  on-chain element need carry no color-bearing ciphertext at all.
  Cost: an out-of-band channel and wallet infrastructure, and the
  loss of "recover all my coins from the seed alone", since the chain
  no longer stores the color hints.
- Oblivious synchronization (attacks P3, and the maintenance in P2/6).
  An UNTRUSTED service maintains, for a wallet, the proofs that its
  elements are unused, and advances its witnesses, WITHOUT learning
  the wallet's color. It works on evolving markers, which are
  unlinkable (property 3), so it sees markers but cannot link them to
  elements, to each other, or to a user. This is the crucial point:
  the maintenance work of P2/P3 moves to a third party, yet
  color-hiding (property 1) is preserved because the service never
  sees a color. Timing-correlation leakage is closed by
  re-randomizing the proof.
- Evolving markers (enables the above and prunes U). Because
  mu_k^(t)(e) changes each epoch t and old versions are unlinkable,
  validators can keep only the CURRENT epoch's markers and prune all
  older ones; the historical "is it unused" check is discharged by an
  incremental, recursively-composed non-membership proof carried in
  the transaction. This makes P3's used-set boundedly small at
  consensus.

So, in one sentence: Tachyon keeps the colored set S and the used set
U and their two lower bounds, but (i) moves color-DETECTION off-chain
so new wallets need not scan, and (ii) moves witness/unused-proof
MAINTENANCE onto an untrusted service that never learns a color, using
evolving markers so the used set can be pruned and the service stays
oblivious.

## 6. Why this framing helps the paper

- It unifies the paper's two authenticated structures (append-only
  membership accumulator and non-membership revocation set) under one
  intuitive predicate: a live coin is a same-color, not-yet-used
  element. Readers get the duality for free.
- It makes the SCANNING/detection problem first-class, which the
  witness-centric property set otherwise hides. Tachyon's out-of-band
  move only makes sense once detection is named.
- It is privacy-first by construction: color-hiding is stated up
  front, so every later property is read through the constraint that
  no third party may learn a color, which is exactly what forces the
  hard design choices (why you cannot just outsource the scan, why
  witness outsourcing needs unlinkable markers).
- Candidate placement: introduce the color model in the Introduction
  or as the opening of the Model section (Section 2), then instantiate
  it: S is the note-commitment tree / MMR / sparse Merkle tree; U is
  the nullifier set; detection is trial decryption; anchors are the
  checkpointed roots. The Zcash case study (Section 8) and Tachyon
  then read as engineering answers to P1-P3 stated in Section 2.

## 7. Caveats

- This is a MODEL, chosen for pedagogy; it abstracts away details
  (value/amounts, balance integrity, key hierarchy, the fact that a
  "note" carries an amount and metadata beyond its color). Those are
  orthogonal to the ADS problem and can be mentioned once and set
  aside.
- "One color = one user" is a simplification: a user may hold many
  colors/keys, and diversified addresses complicate the one-to-one
  map. For the ADS problem this does not matter (treat each detection
  key as a color); note it once so the analogy is not over-read.
