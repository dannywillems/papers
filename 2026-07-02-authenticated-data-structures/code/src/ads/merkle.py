"""Binary Merkle-tree authenticated append-only log.

This module implements Construction 1 of the accompanying paper: an
append-only log whose digest is the root of a balanced binary Merkle
tree over the log entries. It supports appending entries, producing a
logarithmic-size membership proof for any position, and verifying such
a proof against a digest.

Hashing is domain separated: leaves are hashed with the tag ``0x00`` and
internal nodes with the tag ``0x01``. This blocks the second-preimage
attack that would otherwise identify a leaf digest with an internal
digest.
"""

from __future__ import annotations

import enum
import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

# Domain-separation tags (see Construction 1 in the paper).
_LEAF_TAG = b"\x00"
_NODE_TAG = b"\x01"
_EMPTY_TAG = b"\x02"


def sha256(data: bytes) -> bytes:
    """Return the SHA-256 digest of ``data``.

    Used as the default collision-resistant hash function.
    """
    return hashlib.sha256(data).digest()


class Side(enum.Enum):
    """Position of a proof sibling relative to the running node."""

    LEFT = "left"
    RIGHT = "right"


@dataclass(frozen=True)
class ProofStep:
    """One level of a membership proof.

    ``sibling`` is the digest of the sibling node, and ``side`` records
    whether that sibling sits on the ``LEFT`` or ``RIGHT`` of the running
    node at this level.
    """

    sibling: bytes
    side: Side


def _leaf_hash(entry: bytes, hash_fn: Callable[[bytes], bytes]) -> bytes:
    return hash_fn(_LEAF_TAG + entry)


def _node_hash(
    left: bytes,
    right: bytes,
    hash_fn: Callable[[bytes], bytes],
) -> bytes:
    return hash_fn(_NODE_TAG + left + right)


class MerkleLog:
    """An append-only log authenticated by a Merkle-tree digest.

    Entries are arbitrary byte strings. The digest is the Merkle root
    over all appended entries. When a tree level has an odd number of
    nodes, the last node is promoted unchanged to the next level.
    """

    def __init__(
        self,
        entries: Sequence[bytes] | None = None,
        hash_fn: Callable[[bytes], bytes] = sha256,
    ) -> None:
        self._entries: list[bytes] = list(entries) if entries else []
        self._hash_fn = hash_fn

    def __len__(self) -> int:
        return len(self._entries)

    @property
    def entries(self) -> tuple[bytes, ...]:
        """Return the log entries in append order."""
        return tuple(self._entries)

    def append(self, entry: bytes) -> int:
        """Append ``entry`` to the log and return its position."""
        self._entries.append(entry)
        return len(self._entries) - 1

    def get(self, index: int) -> bytes:
        """Return the entry at ``index``."""
        return self._entries[index]

    def _levels(self) -> list[list[bytes]]:
        """Return the tree levels, leaves first, root last."""
        if not self._entries:
            return [[self._hash_fn(_EMPTY_TAG)]]
        level = [_leaf_hash(e, self._hash_fn) for e in self._entries]
        levels = [level]
        while len(level) > 1:
            nxt: list[bytes] = []
            for j in range(0, len(level), 2):
                if j + 1 < len(level):
                    nxt.append(
                        _node_hash(level[j], level[j + 1], self._hash_fn)
                    )
                else:
                    nxt.append(level[j])
            levels.append(nxt)
            level = nxt
        return levels

    def digest(self) -> bytes:
        """Return the Merkle root of the current log.

        For an empty log the digest is ``H(0x02)``, a fixed value
        distinct from any leaf or internal digest.
        """
        return self._levels()[-1][0]

    def prove(self, index: int) -> list[ProofStep]:
        """Return a membership proof for the entry at ``index``.

        The proof lists one sibling digest per tree level on the path
        from the leaf to the root, from leaf to root. Levels at which the
        node is promoted (it has no sibling) contribute no step.
        """
        if not 0 <= index < len(self._entries):
            raise IndexError("index out of range")
        levels = self._levels()
        proof: list[ProofStep] = []
        idx = index
        for level in levels[:-1]:
            if idx % 2 == 0:
                sibling = idx + 1
                if sibling < len(level):
                    proof.append(ProofStep(level[sibling], Side.RIGHT))
            else:
                proof.append(ProofStep(level[idx - 1], Side.LEFT))
            idx //= 2
        return proof


def verify_membership(
    digest: bytes,
    index: int,
    entry: bytes,
    proof: Sequence[ProofStep],
    hash_fn: Callable[[bytes], bytes] = sha256,
) -> bool:
    """Verify a membership proof against ``digest`` (Algorithm 1).

    Recompute the leaf-to-root path: hash ``entry`` into a leaf digest,
    fold in each sibling according to its side, and accept iff the
    recomputed root equals ``digest``. The positional information is
    carried by the sides in ``proof``; ``index`` is part of the
    interface (Verify(d, i, e, pi)) and is not otherwise required.
    """
    del index  # position is encoded by the proof sides
    running = _leaf_hash(entry, hash_fn)
    for step in proof:
        if step.side is Side.LEFT:
            running = _node_hash(step.sibling, running, hash_fn)
        else:
            running = _node_hash(running, step.sibling, hash_fn)
    return running == digest
