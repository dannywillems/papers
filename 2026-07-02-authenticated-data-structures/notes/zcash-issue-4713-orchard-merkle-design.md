# zcash/zcash issue #4713, "[Orchard] Commitment Merkle tree design"

- Authors: therealyingtong, daira, et al.
- Source: <https://github.com/zcash/zcash/issues/4713>, opened
  2020-09-06.
- Accessed: 2026-07-19.
- Status: summarised from the source by a research agent (issue and
  thread fetched); re-verify before citing.

## Core content (and a citation caution)

- CAUTION: the issue is much narrower than its title. The body reads,
  in full: "This looks straightforward. Domain separation for the tree
  layers needs to be specified."
- The thread specifies `MerkleCRH^Orchard`: per-layer domain
  separation via a layer prefix
  `l = I2LEBSP_{layerPrefixLength}(MerkleDepth^Orchard - 1 - layer)`
  prepended to `left || right` inside a collision-resistant hash with
  an 8-byte personalization (draft comment used
  `l_MerkleOrchard = 254`), closing with a pointer to the protocol
  spec (nu5.pdf, orchardmerklecrh).
- The issue does NOT contain the fast-forwardable-witness /
  bounded-checkpoint / spend-window discussion.

## Understanding and use in the paper

- Cite ONLY for the per-layer domain-separation decision (a nice
  contrast to our 0x00/0x01 leaf/node tags and Grin's position
  prefix: three domain-separation styles).
- For witness-scalability requirements cite the Orchard Book and the
  incrementalmerkletree/shardtree docs instead (see the sibling
  notes).
