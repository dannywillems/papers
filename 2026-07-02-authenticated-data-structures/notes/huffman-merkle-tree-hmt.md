# "Huffman-Merkle Tree (HMT)": identification of the term

- Status: term identification by a research agent; the local PDF
  `eprint/2026-1235.pdf` (provided manually) is to be read whole
  before citing anything beyond the abstract.

## The referent

The issue comment "Huffman-Merkle Tree (HMT)" most plausibly refers
to:

- Ziheng (Tom) Shangguan, Aviv Yaish, Dahlia Malkhi, "Authenticated
  Data Structures for Dynamic Workloads", Cryptology ePrint Archive
  2026/1235, June 2026. <https://eprint.iacr.org/2026/1235>.
- Introduces the "Huffman-Merkle Tree (HMT)": a tiered ADS for
  skewed, time-varying access patterns; hot items are laid out by
  Huffman-coding principles (frequently accessed items closer to the
  root, shorter proofs/updates); cold and new items live in a binary
  Merkle tree.
- Abstract-reported numbers (NOT yet verified against the PDF): best
  configuration about 2.4x fewer average hash operations than
  Ethereum's Merkle Patricia Trie and 0.34x fewer than the proposed
  Unified Binary Tree; proofs 0.18x shorter than MPT and 0.55x
  shorter than UBT.

## Distinct constructions with similar names

- "HuffMHT": Munoz, Forne, Esparza, Rey, "Efficient Certificate
  Revocation System Implementation: Huffman Merkle Hash Tree
  (HuffMHT)", TrustBus 2005, LNCS 3592, pp. 119-127.
  DOI: 10.1007/11537878_13. Certificate-revocation tree shaped by
  Huffman coding over query frequencies (minimizes expected proof
  length). The older ancestor of the idea.
- False friend: "HMT: A Hardware-centric Hybrid Bonsai Merkle Tree
  Algorithm for High-performance Authentication" (ACM TECS 2023;
  arXiv 2204.08976): memory-integrity tree, unrelated.

## Use in the paper

- One related-work sentence: Huffman-shaped ADSs optimize EXPECTED
  proof/update cost under skewed access, an orthogonal metric to the
  witness-update-frequency optimality of Bonneau et al. Cite
  2026/1235 (and optionally HuffMHT as the precursor) after reading
  the local PDF.
