# Certificate Transparency: how it works, as a cryptographer

- Sources: RFC 6962 (Laurie, Langley, Kasper, IETF, June 2013,
  DOI 10.17487/RFC6962, <https://www.rfc-editor.org/rfc/rfc6962>);
  Certificate Transparency project, "How CT Works",
  <https://certificate.transparency.dev/howctworks/>. Successor spec:
  RFC 9162 (CT v2) restates the structures; cite 6962 as the
  original.
- Accessed: 2026-07-19.
- Status: the RFC 6962 definitions, recursions, base cases, size
  bound, and worked example below were VERIFIED verbatim against
  rfc-editor.org (targeted fetches). The ecosystem/production
  paragraphs come from the CT project page (agent-digested). The
  "reading it as a cryptographer" sections are own synthesis and must
  not be attributed to a source.

## The problem and the trust model

The web PKI lets hundreds of certificate authorities issue a
certificate for any domain. A misissued certificate is invisible to
the domain owner: the CA and the attacker know it exists, nobody else
does. CT's goal is not to PREVENT misissuance but to make issuance
PUBLICLY UNDENIABLE: every certificate a browser will accept must
appear in public, append-only logs, so a domain owner monitoring the
logs discovers every certificate naming it, legitimate or not.

Party roles, in ADS terms (compare Crosby-Wallach's logger /
clients / auditors and Tamassia's three-party model):

- The LOG is an untrusted prover maintaining an append-only Merkle
  tree over submitted certificates. It is trusted for nothing: every
  claim it makes is either signed (so misbehaviour is attributable)
  or provable (so misbehaviour is detectable).
- CAs / servers are submitters; browsers are verifiers with O(1)
  state (log public keys plus recent signed roots).
- MONITORS replay whole logs watching for certificates of interest;
  AUDITORS spot-check proofs. Between them they enforce that the
  signed commitments and the actual tree agree.

The security goal, informally: if a log ever presents two
inconsistent views (drops, rewrites, or reorders an entry, or shows
different trees to different parties), then some pair of signed
statements it produced is cryptographically irreconcilable, and any
party holding both can prove the log misbehaved.

## The commitment: Merkle Tree Hash (RFC 6962, Section 2.1)

The log's state is committed by the Merkle Tree Hash over the ordered
list D[n] of n entries, with SHA-256:

- MTH({}) = SHA-256() (the hash of the empty string);
- MTH({d(0)}) = SHA-256(0x00 || d(0));
- for n > 1, with k the largest power of two smaller than n:
  MTH(D[n]) = SHA-256(0x01 || MTH(D[0:k]) || MTH(D[k:n])).

Two things a cryptographer should notice:

- Domain separation. The RFC states: "the hash calculations for
  leaves and nodes differ. This domain separation is required to give
  second preimage resistance." Without the 0x00/0x01 prefixes, an
  internal node's input (a 64-byte concatenation of two digests)
  could be reinterpreted as a leaf, yielding the classic
  leaf/interior confusion second-preimage attack. (Our paper's
  Construction 1 uses the same tags; Grin instead salts with node
  positions; Orchard with per-layer prefixes. Three styles, one
  purpose.)
- The split rule fixes the tree SHAPE as a function of n alone
  (largest power of two strictly below n on the left). The tree is
  left-balanced, every left subtree is perfect, and the tree for size
  m is a "prefix" of the tree for size n > m in the sense that makes
  consistency proofs possible. This is the same shape family as
  Crosby-Wallach's history trees, and the left-perfect prefix
  property is exactly what an MMR exposes directly as its list of
  peaks: the CT tree at size n is the MMR's mountains bagged
  right-to-left. NOTE: it differs from our paper's Construction 1
  (promote-last-node-unchanged) for some n; the paper must align or
  flag this.

## Inclusion: the Merkle audit path (Section 2.1.1)

The audit path for the (m+1)st input d(m) is "the shortest list of
additional nodes in the Merkle Tree required to compute the Merkle
Tree Hash" from d(m). Recursively:

- PATH(0, {d(0)}) = {};
- for n > 1: PATH(m, D[n]) = PATH(m, D[0:k]) : MTH(D[k:n]) if m < k,
  and PATH(m, D[n]) = PATH(m - k, D[k:n]) : MTH(D[0:k]) if m >= k.

The verifier refolds the leaf up the path, choosing left/right
concatenation from the bits of m, and compares with the committed
root. Path length equals the leaf's depth, at most ceil(log2 n).
Soundness is the standard Merkle argument: an accepting path for a
wrong leaf yields a collision at the first level where the honest and
claimed values differ with equal parents.

## Append-only: the Merkle consistency proof (Section 2.1.2)

The novel object relative to a plain Merkle tree. Given an old size m
and root MTH(D[0:m]) and a new size n >= m and root MTH(D[n]), the
proof shows D[0:m] is a PREFIX of D[n], i.e. the log only appended.

Verbatim definition: PROOF(m, D[n]) = SUBPROOF(m, D[n], true), with

- SUBPROOF(m, D[m], true) = {} (the old tree IS the current subtree,
  and the verifier already knows its root);
- SUBPROOF(m, D[m], false) = {MTH(D[m])};
- for m < n, with k the split of D[n]:
  - m <= k: SUBPROOF(m, D[n], b) = SUBPROOF(m, D[0:k], b) :
    MTH(D[k:n]) (the old tree lies inside the left subtree; supply
    the right subtree's root);
  - m > k: SUBPROOF(m, D[n], b) = SUBPROOF(m - k, D[k:n], false) :
    MTH(D[0:k]) (the old tree covers the whole left subtree and
    spills into the right; the left root is shared structure).

The boolean b tracks whether the current subtree was part of the OLD
tree in its entirety and the verifier already holds its root (b =
true exactly until the recursion first descends into the right
half). The verifier refolds the supplied nodes TWICE: once
reconstructing the old root (using only the nodes that lie inside the
old tree), once reconstructing the new root (using all of them); it
accepts iff both match. "The number of nodes in the resulting proof
is bounded above by ceil(log2(n)) + 1."

Worked example (Section 2.1.3, 7-leaf tree): the consistency proof
between the size-3 root and the size-7 root is PROOF(3, D[7]) =
[c, d, g, l], four nodes.

The cryptographer's reading: the m <= k branch says old and new tree
share a perfect left subtree, so consistency reduces to the left
half; the m > k branch says the left half is COMMON STRUCTURE whose
root suffices. What makes this work is precisely that completed
(perfect) subtrees are immutable under append; the consistency proof
is a certificate that the log respected that immutability. This is
the same "interior nodes never change" property our paper states for
MMRs, surfaced as a verifiable statement between two digests.

## Signed statements: SCT and STH (Section 3)

Two signature types make log misbehaviour attributable:

- Signed Certificate Timestamp (SCT): issued on submission, "the
  log's promise to incorporate the certificate in the Merkle Tree
  within a fixed amount of time known as the Maximum Merge Delay
  (MMD)" (24h standard). SCTs are what TLS servers staple into
  handshakes (embedded in the certificate, in a TLS extension, or via
  OCSP); browsers require SCTs from multiple independent logs before
  accepting a certificate.
- Signed Tree Head (STH): periodically, the log signs (tree size,
  timestamp, root hash). An STH is a commitment to the entire history
  at that size.

The verification obligations these create: an SCT plus a later STH
should be reconcilable by an INCLUSION proof (the promised entry is
under the signed root); any two STHs should be reconcilable by a
CONSISTENCY proof. A log that cannot produce one on demand is caught
holding a signed statement it cannot justify.

## What the proofs do NOT give you: split views and gossip

The proofs bind statements to each other, not parties to a single
view. A malicious log can maintain two internally consistent forks,
showing one to the victim and one to the monitors ("split-view" or
equivocation attack); every proof each side sees verifies. The
countermeasure is OUT-OF-BAND: gossip/witnessing protocols in which
parties exchange the STHs they have seen (browsers, monitors, and
third-party witnesses cross-checking), so two forked STHs of the
same log eventually meet at some honest party, and the pair of
signatures is the evidence. Consistency proofs make equivocation
UNSUSTAINABLE-once-observed rather than impossible; the residual
assumption is one honest communication path. (Same observation as
Crosby-Wallach's commitment gossip; in ADS terms the digest is only
as authoritative as its distribution channel.)

## Production shape (CT project page)

Logs are operated by Google, Cloudflare, Let's Encrypt, DigiCert,
Sectigo and others; CAs submit a PREcertificate (the certificate with
a poison extension, signed before the real one exists) to obtain SCTs
for embedding; browsers (Chrome and Safari policies) require roughly
two SCTs from logs run by distinct operators; monitors offer
subscription services to domain owners. Scale is billions of entries
across logs; logs shard by certificate-expiry year to bound growth.
"Certificates can only be added to a log, not deleted, modified, or
retroactively inserted."

## Use in our paper

- Section 4 (append-only logs): present MTH, PATH, and SUBPROOF with
  the verified recursions and the ceil(log2 n) + 1 bound; state the
  consistency-proof security game (two verifying proofs from a
  common STH pair pin the shared prefix) with the Crosby-Wallach
  historical-consistency property as the formal ancestor.
- Section 5 bridge: the size-m tree's decomposition into perfect
  subtrees IS the MMR peak decomposition; consistency proofs are the
  digest-to-digest form of MMR interior-node immutability.
- Deployment paragraph: SCT/MMD/STH as the signed-statement layer,
  gossip as the anti-equivocation layer, browser policy as the
  enforcement layer.
- Reminder recorded in the plan: consistency proofs stay OUT of the
  canonical incremental-Merkle-tree property set (Zcash gets digest
  agreement from consensus); CT is the system where they are the
  whole point.
