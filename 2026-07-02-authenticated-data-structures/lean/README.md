# ADS Lean formalisation

Machine-checked proofs of the three properties of the Merkle-tree
authenticated log, over an abstract leaf-hash `hl` and node-hash `hn`
(two distinct functions, modelling the domain separation of the paper).

This is a core-Lean project (no Mathlib), so it builds in seconds.

## What is proved

- `Ads.completeness` - an honest membership proof always verifies
  (Definition 3, Proposition 1).
- `Ads.soundness` - if a value distinct from the genuine leaf verifies
  against the honest root, then `hl` or `hn` has a collision
  (Definition 4, Proposition 2). Contrapositively, under collision
  resistance no wrong value can be opened at a position.
- `Ads.proof_length` - a membership proof has exactly one step per level
  of the descended path (Proposition 3).

All three depend only on the standard axioms `propext`,
`Classical.choice`, and `Quot.sound`; none uses `sorry`
(`#print axioms`).

## Build and run

```bash
make build      # lake build --wfail (fails on any sorry)
make run        # run the demonstration executable
make check      # check no sorry, build, then run
```

`Main.lean` builds a sample tree, opens a path, and checks at runtime
that the honest proof is accepted and a forged value is rejected.
