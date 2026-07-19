# Tamassia, "Authenticated Data Structures" (ESA 2003)

- Author: Roberto Tamassia.
- Reference: Algorithms - ESA 2003, LNCS 2832, pp. 2-5, Springer,
  2003. DOI: 10.1007/978-3-540-39658-1_2. Free copy:
  <https://cs.brown.edu/research/pubs/pdfs/2003/Tamassia-2003-ADS.pdf>.
- Accessed: 2026-07-19 (full 4-page PDF via archive mirror).
- Status: digested by a research agent from the full PDF; re-verify
  before citing. Already in references.bib.

## Core content

- Invited-talk survey fixing the standard THREE-PARTY ADS MODEL:
  source, responder, user, over a structured collection S with query
  and optional update operations.
  - Source holds the original S; each update produces signed,
    time-stamped "structure authentication information" about the
    current version.
  - Responder maintains a copy, receives updates plus structure
    authentication information, answers queries with "answer
    authentication information" = the latest structure authentication
    information plus a proof of the answer.
  - User queries the responder but trusts only the source; verifies
    with the answer authentication information.
  - Responders need no physical security; replicating them gives
    scalability and DoS resilience.
- Survey bounds: Merkle hash trees give a static authenticated
  dictionary with linear space, O(log n) proof size, query and
  verification time; dynamic hash-tree dictionaries reach O(log n)
  update (Naor-Nissim); skip lists with commutative hashing reach
  O(log n) across proof/query/update/verify (Goodrich-Tamassia); the
  RSA-accumulator approach (Goodrich-Tamassia-Hasic) gives constant
  proof size and verification with a query/update trade-off, e.g.
  O(sqrt(n)) query and update. Cites Tamassia-Triandopoulos for cost
  measures and lower bounds; mentions persistent authenticated
  dictionaries, range queries, fractional cascading.

## Understanding and use in the paper

- Feeds Section 2: the canonical three-party model statement and the
  standard cost measures (space, update, query, verification, proof
  size). Our current paper's client/server setting is the two-party
  case; the accumulator setting of eprint 2025/234 is the two-party
  degenerate case; one contrast sentence is worthwhile.
- Also a compact map of early constructions for related work.
