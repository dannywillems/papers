# RFC 6962, "Certificate Transparency" (Merkle proof definitions)

- Authors: Ben Laurie, Adam Langley, Emilia Kasper.
- Reference: RFC 6962, IETF, June 2013. DOI: 10.17487/RFC6962.
  <https://www.rfc-editor.org/rfc/rfc6962>. Successor: RFC 9162
  (CT v2) restates the definitions; cite 6962 as the original.
- Accessed: 2026-07-19 (rfc-editor.org directly).
- Status: digested by a research agent from the RFC text (Section
  2.1); re-verify before citing. Already in references.bib.

## Core definitions (Section 2.1)

- Merkle Tree Hash over an ordered list D[n], SHA-256, with domain
  separation:
  - MTH({}) = SHA-256().
  - MTH({d(0)}) = SHA-256(0x00 || d(0)).
  - n > 1: k = largest power of two smaller than n;
    MTH(D[n]) = SHA-256(0x01 || MTH(D[0:k]) || MTH(D[k:n])).
  The 0x00/0x01 prefixes block the leaf-vs-node second-preimage
  confusion (same tags our paper already uses). The split rule makes
  the tree left-balanced, the same shape family as history trees.
- Merkle audit path (2.1.1): for the (m+1)st input d(m), the shortest
  list of additional nodes required to compute MTH from d(m); root
  match proves inclusion. Length <= ceil(log2(n)).
- Merkle consistency proof (2.1.2): given MTH(D[0:m]) and MTH(D[n])
  (m <= n), a set of intermediate nodes sufficient to verify both
  roots (recursive SUBPROOF definition); proves the append-only
  property (D[0:m] is a prefix of D[n]). Size <= ceil(log2(n)) + 1
  nodes.
- Section 2.1.3 has the worked 7-leaf example (audit path for d0 is
  [b, h, l], etc.).

## Understanding and use in the paper

- Feeds Section 4: the de facto standard concrete definitions of
  inclusion and consistency proofs for append-only logs, with exact
  construction and size bounds. Our Section 4 should present the
  consistency-proof algorithm and cite this for the normative form.
- Note our current paper's Construction 1 differs from MTH in the odd
  case: we promote the last node unchanged; RFC 6962 splits at the
  largest power of two below n. Both are left-balanced families but
  they are NOT the same tree for all n; the paper should either align
  or note the difference explicitly when introducing consistency
  proofs.
