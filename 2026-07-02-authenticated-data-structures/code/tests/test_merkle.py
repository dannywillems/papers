"""Tests for the Merkle-tree authenticated log."""

from __future__ import annotations

import hashlib
import math
import secrets

import pytest

from ads import MerkleLog, ProofStep, Side, verify_membership


def _random_log(n: int) -> MerkleLog:
    return MerkleLog([secrets.token_bytes(16) for _ in range(n)])


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 8, 9, 16, 17, 100])
def test_completeness(n: int) -> None:
    """Every honest membership proof verifies (Definition 3)."""
    log = _random_log(n)
    digest = log.digest()
    for i in range(n):
        proof = log.prove(i)
        assert verify_membership(digest, i, log.get(i), proof)


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 8, 9, 16, 17, 100])
def test_proof_size(n: int) -> None:
    """Proof length is at most ceil(log2 n) (Proposition 3)."""
    log = _random_log(n)
    height = math.ceil(math.log2(n)) if n > 1 else 0
    for i in range(n):
        assert len(log.prove(i)) <= height


def test_tamper_entry_rejected() -> None:
    """A wrong entry is rejected (soundness, Definition 4)."""
    log = _random_log(8)
    digest = log.digest()
    proof = log.prove(3)
    forged = bytes(b ^ 0xFF for b in log.get(3))
    assert not verify_membership(digest, 3, forged, proof)


def test_tamper_sibling_rejected() -> None:
    """Flipping a sibling digest in the proof is rejected."""
    log = _random_log(8)
    digest = log.digest()
    proof = log.prove(3)
    bad_sibling = bytes(b ^ 0x01 for b in proof[0].sibling)
    tampered = [ProofStep(bad_sibling, proof[0].side), *proof[1:]]
    assert not verify_membership(digest, 3, log.get(3), tampered)


def test_tamper_side_rejected() -> None:
    """Flipping a proof side bit is rejected."""
    log = _random_log(8)
    digest = log.digest()
    proof = log.prove(2)
    flipped_side = Side.LEFT if proof[0].side is Side.RIGHT else Side.RIGHT
    tampered = [ProofStep(proof[0].sibling, flipped_side), *proof[1:]]
    assert not verify_membership(digest, 2, log.get(2), tampered)


def test_wrong_digest_rejected() -> None:
    """A proof does not verify against a different log's digest."""
    log_a = _random_log(8)
    log_b = _random_log(8)
    proof = log_a.prove(1)
    assert not verify_membership(log_b.digest(), 1, log_a.get(1), proof)


def test_append_changes_digest() -> None:
    """Appending an entry changes the digest."""
    log = _random_log(4)
    before = log.digest()
    log.append(b"new-entry")
    assert log.digest() != before


def test_domain_separation() -> None:
    """A single-entry root is not the raw leaf-content hash.

    The leaf tag 0x00 must be mixed in, so the root differs from
    ``sha256(entry)``.
    """
    log = MerkleLog([b"payload"])
    assert log.digest() != hashlib.sha256(b"payload").digest()


def test_empty_log_digest_is_defined() -> None:
    """An empty log has a fixed digest and no provable positions."""
    log = MerkleLog()
    assert isinstance(log.digest(), bytes)
    with pytest.raises(IndexError):
        log.prove(0)


def test_prove_out_of_range() -> None:
    """Proving a non-existent position raises IndexError."""
    log = _random_log(3)
    with pytest.raises(IndexError):
        log.prove(3)
    with pytest.raises(IndexError):
        log.prove(-1)
