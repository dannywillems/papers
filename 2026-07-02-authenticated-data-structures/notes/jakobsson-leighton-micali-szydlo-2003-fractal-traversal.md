# Jakobsson, Leighton, Micali, Szydlo, "Fractal Merkle Tree Representation and Traversal" (CT-RSA 2003)

- Authors: Markus Jakobsson, Tom Leighton, Silvio Micali, Michael
  Szydlo.
- Reference: Topics in Cryptology - CT-RSA 2003, LNCS 2612,
  pp. 314-326, Springer, 2003. DOI: 10.1007/3-540-36563-X_21.
- Free copy: <http://www.szydlo.com/fractal-jmls.pdf>.
- Accessed: 2026-07-19 (author-page PDF via archive mirror; matches
  the proceedings version).
- Status: digested by a research agent from the full PDF; re-verify
  before citing.

## Core results

- Abstract claim: for one parameter choice and N leaves, worst-case
  2 log N / loglog N hash evaluations per output and total storage
  under 1.5 log^2 N / loglog N hash values; "a simultaneous
  improvement both in space and time complexity over any previously
  published algorithm". (Merkle's original: T_max = 2 log N, space
  about (1/2) log^2 N.)
- General trade-off with stacked subtrees of height h (L = H/h
  levels, H = log N): computation below 2H/h per round; space bounded
  by Space_max <= (2L-1)(2^(h+1) - 2) + L - 2 + h(L-2)(L-1)/2,
  simplified to Space_max < 2 L 2^(h+1) + HL/2 (their eqs. 4-5).
- Low-space choice h = log H = loglog N gives T_max =
  2 log N / loglog N and Space_max <= (5/2) log^2 N / loglog N
  (eqs. 6-7), improved to < 1.5 log^2 N / loglog N by discarding
  pebbles in existing subtrees early plus a TREEHASH tweak
  (Section 6).
- Technique: "fractal" stacked-subtree representation; an Existing
  and a Desired subtree per level; amortized pebbling moves the
  frontier; trade-off parameter is subtree height h.

## Understanding and use in the paper

- Feeds Section 7. Cite for: the first sublinear simultaneous
  space/time improvement for Merkle traversal; origin of the
  fractal/stacked-subtree amortization that Szydlo 2004 and the XMSS
  BDS algorithm build on; the time-space trade-off curve.
- Same model caveat as Szydlo 2004: traversal cost, not witness
  update frequency; verifier oblivious to the traversal technique.
