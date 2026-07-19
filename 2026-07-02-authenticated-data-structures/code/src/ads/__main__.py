"""Runnable demonstration of the Merkle log.

Builds a small log, prints its digest, produces a membership proof,
verifies it, and shows that a tampered entry is rejected. Run it with
``python -m ads`` (or the Run button on the paper's web page).
"""

from __future__ import annotations

from ads import MerkleLog, verify_membership


def main() -> None:
    """Append a few entries, then prove and verify membership."""
    entries = [f"entry-{i}".encode() for i in range(8)]
    log = MerkleLog(entries)
    digest = log.digest()
    print(f"log size      : {len(log)}")
    print(f"digest        : {digest.hex()}")

    index = 3
    proof = log.prove(index)
    print(f"proof for #{index}  : {len(proof)} steps")
    for step in proof:
        print(f"  {step.side.value:<5} {step.sibling.hex()[:16]}...")

    ok = verify_membership(digest, index, log.get(index), proof)
    print(f"verify honest : {'accept' if ok else 'reject'}")

    forged = bytes(b ^ 0xFF for b in log.get(index))
    bad = verify_membership(digest, index, forged, proof)
    print(f"verify forged : {'accept (BUG)' if bad else 'reject'}")


if __name__ == "__main__":
    main()
