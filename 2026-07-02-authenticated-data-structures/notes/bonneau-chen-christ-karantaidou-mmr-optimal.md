# Bonneau, Chen, Christ, Karantaidou, "Merkle Mountain Ranges Are Optimal" (eprint 2025/234, CRYPTO 2025)

- Authors: Joseph Bonneau (NYU, a16z crypto), Jessica Chen (NYU),
  Miranda Christ (Columbia), Ioanna Karantaidou (NYU; CNRS, IRIF,
  Universite Paris Cite).
- Title: "Merkle Mountain Ranges Are Optimal: On Witness Update
  Frequency for Cryptographic Accumulators".
- Reference: Advances in Cryptology - CRYPTO 2025, Springer LNCS.
  DOI: 10.1007/978-3-032-01878-6_6. Preprint: Cryptology ePrint
  Archive 2025/234, <https://eprint.iacr.org/2025/234>.
- Version read: the eprint PDF, read WHOLE first-hand (25 pages) from
  the local copy `eprint/Merkle Mountain Ranges are optimal -
  2025-234.pdf` on 2026-07-19.
- Status: VERIFIED first-hand against the full text. Quotes below are
  faithful to the PDF.

## Problem and headline results

Append-only set commitments with succinct digests and O(log n)
inclusion proofs ("witnesses"). The studied metric: how often existing
elements' witnesses must CHANGE as new elements are appended.

- Lower bound (abstract): "to accumulate a set of n items, any
  construction with a succinct accumulator value (O(lambda polylog n)
  storage) must induce at least omega(n) total witness updates as n
  items are sequentially added."
- Stronger regime: for accumulators accommodating superpolynomial-size
  sets, Omega(n log n / log log n) total updates.
- Bounds hold "not just in the worst case, but with overwhelming
  probability over a random choice of the accumulated set".
- Matching upper bound: k-ary MMRs; with k = log^c n they achieve
  O(n log n / (c log log n)) total updates, so (log n)-ary MMRs are
  essentially optimal.
- Motivation stated: for Merkle trees, RSA accumulators, and bilinear
  accumulators, "adding a single new element to the set requires
  (except with negligible probability) changing every existing
  element's witness". Also: their bound shows most witnesses "never
  stop changing" (stronger than change-at-least-once bounds), which
  matters for offline clients.

## Definitions (Section 4)

- Definition 1 (append-only accumulator, after Benaloh-de Mare):
  Pi = (Setup, Acc, Verify), data universe U.
  Setup(1^lambda, ord) -> pp, where ord is an ORDERING FUNCTION
  mapping a set to a sequence of its elements. Acc(pp, S) -> A,
  (pi_1..pi_|S|). Verify(pp, A, u, pi) -> {true, false}. Add is
  implicit (re-run Acc on S union {s'}). Remark 2: passing ord to
  Setup STRENGTHENS the lower bound (the scheme may exploit knowledge
  of past and future insertion order).
- Definition 2 (soundness): computational; negligible probability of
  a verifying membership proof for u not in S.
- Definition 3 (correctness): up-to-date proofs verify with
  probability 1.
- Definitions 4-5 (size, succinctness): Size(Pi, lambda, n) = max |A|
  over pp, |S| = n. Succinct if Size(Pi, lambda, n) <= p(lambda)
  q(log n) for polynomials p, q.
- Definitions 6-7 (superpolynomial-size sets): accommodates sets of
  size f(lambda) if Setup, Verify run in poly(lambda), Acc in
  poly(lambda, f(lambda)); correctness up to |S| <= f(lambda);
  soundness against poly(lambda, f(lambda)) adversaries with success
  negligible in lambda + f(lambda).
- Definition 8 (one-shot witness updates): S has k one-shot updates
  under pp if for at least k indices i,
  Verify(pp, A_n, s_i, pi_i^(i)) = false, where pi_i^(i) is the
  witness issued when s_i was added and A_n is the final accumulator.
- Witness-change counting (Section 3.1): the number of changes for
  x_j is the number of indices j <= i <= n-1 with pi_j^(i) != bot and
  pi_j^(i) != pi_j^(i+1); the initial assignment is not counted.
  Trivial max: n(n-1)/2 = O(n^2) total, O(n) per element.

## Main theorems (verified statements)

- Lemma 1 (one-shot witness changes): Pi succinct, ord arbitrary,
  U any subset of size n = Omega(poly(lambda)), S <= U random. For
  any constant c in (0,1): Pr[S has fewer than c|S| one-shot witness
  updates given pp] <= negl(lambda). Proof: compression/encoding.
  Alice sends the final accumulator A_k^S plus a bit vector v (one
  bit per universe element consulted); Bob replays additions with
  shared randomness, testing each u_i's fresh witness against A_k^S;
  soundness ensures verification only for members. If few witnesses
  changed, the message is n - Omega(n) + polylog(lambda) bits,
  contradicting Shannon's coding theorem for a random element of a
  2^n/(2p(lambda))-sized set.
- Lemma 2 (multi-shot): X random polynomial-sized subset, split after
  a starting index m0 into d consecutive segments of size m; the
  considered witnesses are those of each segment relative to the
  accumulator at that segment's completion. If
  d = omega(Size(Pi, lambda, m0 + dm)), then for any positive
  constant c < 1, with overwhelming probability at least a fraction c
  of these witnesses no longer verify against A_{m0+dm} (at least
  cdm values of j).
- Theorem 1: "Let Pi = (Setup, Acc, Verify) be a succinct accumulator
  for a data universe U. Let ord be an arbitrary ordering function.
  For any constant alpha >= 0, for sufficiently large n,
  Pr[there are at least alpha n witness updates given pp]
  >= 1 - negl(lambda)", probability over random X with |X| = n and
  pp <- Setup(1^lambda, ord). Since alpha is an arbitrary constant,
  total updates are omega(n). Proof parameters: d >= lambda^2,
  h = alpha/0.99, n = d^h; hierarchy of h levels of segments of sizes
  d^i; Lemma 2 with c = 0.99 per level gives >= 0.99 n changes per
  level, summed over h levels, with care not to double-count
  (disjoint counting windows per level).
- Corollary 1: Lemma 2 for superpolynomial-set accumulators, with
  error negl(lambda + f(lambda)).
- Corollary 2: "Let Pi be a succinct accumulator for sets of
  superpolynomial size n (Definition 6). ... There exists some
  constant alpha such that for any constant c in (0,1), for
  sufficiently large n, Pr[there are at least
  (c beta n log n)/(alpha log log n) witness updates given pp]
  >= 1 - negl(lambda)." Proof: rerun Theorem 1 with
  d = (p(lambda) q(log n))^2 and h = log n / log d; soundness
  negligible in f(lambda) allows a union bound over poly(n) events;
  log d <= (alpha/beta) log log n for n <= 2^(lambda^beta).
- Theorem 2 (upper bound): "A k-ary Merkle Mountain Range is succinct
  and requires O(n log_k n) witness updates when accumulating n
  elements." Accumulator size O(k log_k n): at most ceil(log_k n)
  distinct tree sizes, at most k-1 trees per size; maximum hit at
  n = k^m - 1. An element's proof changes only when its tree is
  merged; at most floor(log_k n) merges per element. Reyzin-Yakoubov
  proved the k = 2 case (their [42], SCN 2016, Theorem 2).
- Corollary 3: k-ary MMR with k = log^c n: O(log^(c+1) n) storage and
  O(n log n / (c log log n)) witness updates.
- Remark 3: such MMRs are sound in the random-oracle model for sets
  of size 2^(lambda^beta), beta < 1 (collision probability
  poly(2^(lambda^beta)) * 2^-lambda).

## The k-ary MMR (Section 6.1, verified)

A list of complete k-ary Merkle trees storing disjoint subsequences;
the number of trees of each size equals the corresponding digit of
the base-k representation of n. Accumulator = list of the roots in
decreasing tree-size order. Witness = sibling nodes along the path to
its Merkle root; verification checks the proof against ANY root in
the list. Add: create a singleton tree; while k same-size trees
exist, merge them into one (adding the new sibling nodes to the
member witnesses). Binary MMR: Theta(lambda log n) commitment,
Theta(n log n) total witness changes; "witness updates are ...
concretely efficient, consisting of appending just one new
neighbor-node value to the existing witness".

## Comparison of constructions (Table 1, Section 3.2, verified)

Accumulator size / total witness updates (lambda factors omitted):
- Simple database: Theta(n) / 0.
- Classical accumulator (Merkle root, RSA, bilinear): Theta(1) /
  O(n^2).
- k-buffering + accumulator: Theta(k) / O(n^2/k).
- k-bucketed accumulators: Theta(n/k) / O(kn).
- k-buffering + k-bucketed: Theta(n/k + k) / O(n) (k = sqrt(n) gives
  Theta(sqrt n) storage).
- k-ary Mountain Range: O(k log_k n) / Theta(n log_k n).
- (log n)-ary Mountain Range: O(log^2 n) / O(n log n / log log n).

## Related-work map (verified against their Sections 2 and refs)

- Prior lower bounds use DELETION: Camacho-Hevia (Latincrypt 2010,
  batch update impossibility; information linear in number of deleted
  elements) and Christ-Bonneau (Financial Crypto 2022, "Limits on
  revocable proof systems": Omega(n/log n) proofs change, applies to
  dynamic or universal accumulators). Neither applies to plain
  append-only accumulators; that is the gap this paper fills.
- Memory checkers (Blum et al.; Dwork-Naor-Rothblum-Vaikuntanathan
  TCC 2009; Boyle-Komargodski-Vafa ACM TOC 2024; Wang-Lu-
  Papamanthou-Zhang CCS 2023 locality): incomparable model; their
  lower bounds do not imply accumulator bounds (Section 2 discusses
  in depth).
- Registration-based encryption faces an analogous update problem;
  the RBE lower bound of Mahmoody-Qi-Rahimi (TCC 2022) extends to
  accumulators but only restricted ones (update times known in
  advance); this paper's bound has no such restriction.
- Trusted-manager settings evade the bound (Baldimtsi et al.;
  Karantaidou-Baldimtsi; Tas-Boneh vector commitments with efficient
  updates), at the cost of a manager who can violate soundness.
  Batching (Boneh-Bunz-Fisch CRYPTO 2019; Srinivasan et al.
  Hyperproofs) does not make witnesses update LESS FREQUENTLY.
- MMR history: Todd proposed and named MMRs in 2013 (OpenTimestamps);
  Reyzin-Yakoubov (SCN 2016) rediscovered the construction for
  distributed PKI; Garg-Hajiabadi-Mahmoody-Rahimi (TCC 2018)
  rediscovered it for RBE; Crosby-Wallach 2009 history trees are "a
  similar notion but with all sub-trees included as nodes of a larger
  tree"; Google's Transparency team proposed "compact ranges" (2022).
- Applications listed: OpenTimestamps; Todd's delayed TXO
  commitments; FlyClient (Bunz-Kiffer-Luu-Zamani, IEEE S&P 2020)
  adopted by Grin, Minima, Nervos, Neptune, and Zcash; Axiom,
  Herodotus, Picasso; DataTrails, Witness. Liang et al. (2024)
  studied k-ary MMRs for IoT.

## Use in our paper

- Section 6 (optimality): state Definition 8, Lemma 1 (with the
  compression-argument sketch), Theorem 1, Corollary 2, Theorem 2,
  Corollary 3 faithfully; explain the buffering/bucketing trade-off
  ladder (Table 1) as the pedagogical run-up to the MMR.
- Section 5 (MMR): their Section 6.1 gives the clean k-ary
  formalisation to align our notation with; note the verify-against-
  any-root convention vs peak bagging (Todd/Grin bag peaks into one
  root; the paper keeps the root list; equivalent up to an O(k log_k
  n)-vs-O(lambda) commitment and one extra path segment).
- Section 8 (Zcash): the lower bound speaks to TOTAL witness changes;
  shardtree's lazy fast-forward changes the SCHEDULE of updates, not
  the total count (consistent with the bound; state this and check
  against Definition 8's counting).
- Section 2: their accumulator definitions (1-8) are a good basis for
  our formal model section; our existing Merkle-log definitions are
  the two-party specialisation.
- References to add to references.bib: this paper (CRYPTO 2025 +
  eprint), Reyzin-Yakoubov SCN 2016, Camacho-Hevia Latincrypt 2010,
  Christ-Bonneau FC 2022, Bunz et al. FlyClient S&P 2020, Benaloh-de
  Mare Eurocrypt 1993, Camenisch-Lysyanskaya CRYPTO 2002, Nguyen
  CT-RSA 2005, Li-Li-Xue ACNS 2007, Damgard-Triandopoulos eprint
  2008/538, Boneh-Bunz-Fisch CRYPTO 2019, Miller-Hicks-Katz-Shi POPL
  2014 (generic ADS), Papamanthou-Tamassia-Triandopoulos
  Algorithmica 2016 (authenticated hash tables), Google compact
  ranges (online).
