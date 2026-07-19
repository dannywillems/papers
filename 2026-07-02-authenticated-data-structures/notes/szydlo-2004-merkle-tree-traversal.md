# Szydlo, "Merkle Tree Traversal in Log Space and Time" (Eurocrypt 2004)

- Author: Michael Szydlo.
- Reference: Advances in Cryptology - EUROCRYPT 2004, LNCS 3027,
  pp. 541-554, Springer, 2004. DOI: 10.1007/978-3-540-24676-3_32.
- Free preprint (2003 version, differs somewhat from the proceedings
  version): <http://www.szydlo.com/logspacetime03.pdf>.
- Accessed: 2026-07-19 (preprint, via archive mirror).
- Status: digested by a research agent from the full preprint PDF;
  re-verify the published-version constants before citing.

## Core results

- Problem (Merkle tree traversal): output, for successive leaves (one
  per round), the leaf value plus its authentication path (one sibling
  node value per height).
- Main result: preprint abstract states time Log2(N) and space less
  than 3 Log2(N) (body: Log2(N) elementary operations per round,
  storage 3 Log2(N) - 2 node values). The PUBLISHED Eurocrypt 2004
  version states time 2 log2(N) and space < 3 log2(N); the constant-2
  time bound is the usually cited one. Units: hash evaluations / leaf
  computations for time, stored node values for space.
- Prior work as stated there: Merkle's original traversal, max space
  about (1/2) Log^2(N), max computation 2 Log(N) - 2 hashes per
  round; Jakobsson et al. with space-minimizing parameters, about
  1.5 Log^2(N)/LogLog(N) space and 2 Log(N)/LogLog(N) time per round.
- Lower bound (preprint Theorem 1): if a traversal algorithm uses
  space bounded by alpha log(N), then there is a constant beta such
  that its time is at least beta log(N). Phrased: no algorithm
  consumes both less than O(Log2(N)) space and less than O(Log2(N))
  time. Proof via a pebbling/counting argument over right nodes;
  constants explicitly not quantified.
- Key algorithmic ideas: the TREEHASH stack subroutine plus a new
  scheduling of subtree computations balancing budget across heights.

## Understanding and use in the paper

- Feeds Section 7 (witness maintenance and traversal). This is the
  classical single-tree traversal benchmark and its matching
  Theta(log N) space/time optimality.
- Important framing for our paper: traversal cost (prover-side,
  static tree, all leaves in order) is a DIFFERENT cost model from
  witness-update frequency in a growing accumulator (eprint
  2025/234). The paper should contrast the two explicitly.
- The sparse-witness workload (a few marked leaves, not all) is what
  Zcash faces; these algorithms target the hash-based-signature
  workload (every leaf in order). State the difference.
