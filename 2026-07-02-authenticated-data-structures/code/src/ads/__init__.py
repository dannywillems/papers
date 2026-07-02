"""Merkle-tree authenticated append-only log.

Reference implementation for the paper "Authenticated Data Structures:
A Merkle-Tree Log with Logarithmic Membership Proofs".
"""

from ads.merkle import (
    MerkleLog,
    ProofStep,
    Side,
    verify_membership,
)

__all__ = [
    "MerkleLog",
    "ProofStep",
    "Side",
    "verify_membership",
]
