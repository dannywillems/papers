import Ads

open Ads

/-- Toy leaf-hash for the demonstration run. Not cryptographic; the
security guarantees live in the proofs, not in this function. -/
def demoLeaf (a : Nat) : Nat := (a * 2654435761 + 1) % 1000000007

/-- Toy node-hash for the demonstration run. -/
def demoNode (x y : Nat) : Nat := (x * 31 + y * 17 + 2) % 1000000007

/-- A four-leaf sample tree. -/
def sample : Tree Nat :=
  .node (.node (.leaf 10) (.leaf 20)) (.node (.leaf 30) (.leaf 40))

def main : IO UInt32 := do
  let rt := Tree.root demoLeaf demoNode sample
  IO.println s!"root digest = {rt}"
  match openTree? demoLeaf demoNode sample [Dir.L, Dir.R] with
  | some (a, p) =>
    IO.println s!"opened leaf = {a}, proof length = {p.length}"
    if verify demoLeaf demoNode rt a p then
      IO.println "verify honest proof: accept"
    else
      IO.println "verify honest proof: reject (unexpected)"
      return 1
    if verify demoLeaf demoNode rt 999 p then
      IO.println "verify forged value: accept (BUG)"
      return 1
    else
      IO.println "verify forged value: reject (expected)"
    IO.println "all runtime checks passed"
    return 0
  | none =>
    IO.println "openTree? failed (unexpected)"
    return 1
