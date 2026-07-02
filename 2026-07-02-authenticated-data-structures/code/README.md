# ADS reference implementation

Python reference implementation of the Merkle-tree authenticated
append-only log described in the paper in the parent directory.

## What it does

`ads.MerkleLog` builds a balanced binary Merkle tree over a sequence of
byte-string entries. It produces a logarithmic-size membership proof for
any position and verifies such a proof against the tree digest with
`ads.verify_membership`. Hashing is domain separated (leaf tag `0x00`,
internal tag `0x01`); the default hash is SHA-256.

## Usage

```python
from ads import MerkleLog, verify_membership

log = MerkleLog()
log.append(b"first")
i = log.append(b"second")

digest = log.digest()
proof = log.prove(i)
assert verify_membership(digest, i, b"second", proof)
```

## Development

This project uses [uv](https://docs.astral.sh/uv/).

```bash
make install      # install dependencies (uv sync)
make check        # format check, lint, typecheck, tests
make test         # run the test suite
```

Individual targets: `make format`, `make lint`, `make typecheck`.
