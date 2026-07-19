# Accumulators background (Benaloh-de Mare, Camenisch-Lysyanskaya, comparison facts)

- Status: digested by a research agent from the standard sources,
  cross-checked against the related-work section of eprint 2025/234;
  the Nguyen / Li-Li-Xue / Damgard-Triandopoulos attributions are
  standard literature not independently re-fetched. Verify page
  numbers before final citation.

## Benaloh-de Mare (one-way accumulators)

- Reference: Josh Benaloh, Michael de Mare, "One-Way Accumulators: A
  Decentralized Alternative to Digital Signatures", EUROCRYPT '93,
  LNCS 765, pp. 274-285, Springer, 1994. DOI: 10.1007/3-540-48285-7_24.
- Accumulators via a quasi-commutative one-way hash; RSA
  instantiation z = x^(y_1 ... y_n) mod N.
- Constant-size accumulator value and witnesses (one group element);
  witness for y_i is the accumulation of all other elements;
  verification one exponentiation.
- Append: O(1) exponentiation for the accumulator value, but EVERY
  existing witness must be updated (one exponentiation each): one
  append touches all n witnesses.
- No non-membership proofs. Trusted setup: RSA modulus with unknown
  factorization (dealer or MPC; class groups the known workaround).

## Camenisch-Lysyanskaya (dynamic accumulators)

- Reference: Jan Camenisch, Anna Lysyanskaya, "Dynamic Accumulators
  and Application to Efficient Revocation of Anonymous Credentials",
  CRYPTO 2002, LNCS 2442, pp. 61-76, Springer, 2002.
  DOI: 10.1007/3-540-45708-9_5.
- Adds efficient DELETION and witness updates to the RSA accumulator
  (anonymous credential revocation). Elements are primes;
  v = u^(prod x_i) mod n, safe RSA modulus.
- Add x': v' = v^(x'); witness w for x updates w' = w^(x').
- Delete x' (manager, using the factorization trapdoor):
  v' = v^(x'^-1 mod phi(n)); a user updates its witness WITHOUT the
  trapdoor via Bezout a, b with a*x + b*x' = 1: w' = w^b * v'^a.
- O(1) exponentiations per witness per epoch, but every held witness
  refreshes on every add/delete: Theta(n) total work per operation
  across witness holders. Constant proof size; trusted setup.

## Prior lower bounds (as cited by eprint 2025/234)

- Camacho-Hevia: batch witness updates after deletions need
  information linear in the number of deleted elements.
- Christ-Bonneau: Omega(n / log n) witnesses must change when
  deleting n elements from a succinct DYNAMIC or UNIVERSAL
  accumulator. Neither applies to plain append-only accumulators,
  which is the gap 2025/234 fills.

## Comparison-table facts (per-append unless stated)

- Merkle tree (single, append/rebuild): append O(log n) hashes; proof
  O(log n); every append changes the root and with high probability
  every element's witness; non-membership only if sorted (then
  inserts shift shape) or via SMT; no trusted setup.
- Binary MMR: commitment Theta(lambda log n) as peak list (O(lambda)
  if peaks bagged); append O(1) amortized hashes; proof O(log n);
  TOTAL witness updates over n appends Theta(n log n) (an element's
  witness changes only at merges, <= floor(log2 n) times). k-ary MMR
  with k = log^c n: O(log^(c+1) n) commitment and
  O(n log n / (c log log n)) total updates (optimal per eprint
  2025/234). Non-membership: no. No trusted setup.
- RSA accumulator (BdM; CL02 dynamic): commitment O(1); append O(1)
  exponentiation for the value but all n witnesses refresh per append
  (Theta(n) total); proof O(1); deletion O(1) with trapdoor (CL02);
  non-membership not in the base scheme (universal RSA accumulators:
  Li-Li-Xue 2007); trusted setup required (avoidable with class
  groups).
- Bilinear/pairing accumulator (Nguyen 2005): commitment O(1); proof
  O(1); every append changes all witnesses; non-membership in the
  universal extension (Damgard-Triandopoulos 2008); trusted setup:
  q-SDH powers-of-tau CRS with an upper bound on set size.
- The "every witness changes per append" fact for Merkle trees, RSA,
  and bilinear accumulators is stated in eprint 2025/234, Section 1.

## Use in the paper

- Feeds Section 3 (accumulator background) and Section 9 (the
  comparison table rows). The BdM/CL02 references belong in
  references.bib; add Nguyen 2005, Li-Li-Xue 2007,
  Damgard-Triandopoulos 2008, Camacho-Hevia, Christ-Bonneau once
  their exact metadata is verified.
