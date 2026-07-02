/-
Copyright (c) 2026 Danny Willems. All rights reserved.
Released under the MIT license as described in the file LICENSE.
Authors: Danny Willems
-/

/-!
# Merkle-tree authenticated log: verified core

This module formalises the append-only Merkle log of the accompanying
paper and proves its three stated properties over an abstract leaf-hash
`hl` and node-hash `hn`. Using two distinct hash functions models the
domain separation of Construction 1 (leaf tag `0x00`, node tag `0x01`).

## Main statements

- `Ads.completeness`: an honest membership proof always verifies
  (Definition 3, Proposition 1).
- `Ads.soundness`: if a value distinct from the genuine leaf verifies
  against the honest root, a hash collision exists
  (Definition 4, Proposition 2).
- `Ads.proof_length`: a proof has exactly one step per tree level on the
  path (Proposition 3).

## References

* [Merkle, *A Digital Signature Based on a Conventional Encryption
  Function*][Merkle88]
-/

namespace Ads

universe u v

/-- Direction taken when descending into a node. `L` means we descend
into the left child (its sibling is the right child); `R` is the mirror
case. -/
inductive Dir where
  | L
  | R
  deriving DecidableEq, Repr

/-- A binary Merkle tree carrying data of type `α` at its leaves. -/
inductive Tree (α : Type u) where
  | leaf : α → Tree α
  | node : Tree α → Tree α → Tree α
  deriving Repr

namespace Tree

/-- The Merkle root of a tree under leaf-hash `hl` and node-hash `hn`. -/
def root {α : Type u} {δ : Type v} (hl : α → δ) (hn : δ → δ → δ) :
    Tree α → δ
  | leaf a => hl a
  | node l r => hn (root hl hn l) (root hl hn r)

end Tree

/-- One step of a membership proof: the descent direction and the sibling
digest at that level. -/
abbrev Step (δ : Type v) := Dir × δ

/-- A membership proof: the list of steps ordered from the root to the
leaf. -/
abbrev Proof (δ : Type v) := List (Step δ)

variable {α : Type u} {δ : Type v}

/-- Descend the tree along the directions `ds`. On success, return the
reached leaf value together with the membership proof collected along the
path (the sibling digests). Returns `none` when the directions do not fit
the tree shape. -/
def openTree? (hl : α → δ) (hn : δ → δ → δ) :
    Tree α → List Dir → Option (α × Proof δ)
  | Tree.leaf a, [] => some (a, [])
  | Tree.node l r, Dir.L :: ds =>
      (openTree? hl hn l ds).map
        (fun q => (q.1, (Dir.L, Tree.root hl hn r) :: q.2))
  | Tree.node l r, Dir.R :: ds =>
      (openTree? hl hn r ds).map
        (fun q => (q.1, (Dir.R, Tree.root hl hn l) :: q.2))
  | _, _ => none

/-- Recompute a root from a claimed leaf value `a` and a proof. This is
the verifier's fold (Algorithm 1), applied from the leaf up. -/
def recompute (hl : α → δ) (hn : δ → δ → δ) (a : α) : Proof δ → δ
  | [] => hl a
  | (Dir.L, sib) :: rest => hn (recompute hl hn a rest) sib
  | (Dir.R, sib) :: rest => hn sib (recompute hl hn a rest)

/-- The verifier: accept iff the recomputed root equals the digest. -/
def verify [DecidableEq δ] (hl : α → δ) (hn : δ → δ → δ)
    (rt : δ) (a : α) (p : Proof δ) : Bool :=
  decide (recompute hl hn a p = rt)

/-- A collision in either the leaf-hash or the node-hash. -/
def HasCollision (hl : α → δ) (hn : δ → δ → δ) : Prop :=
  (∃ x y : α, x ≠ y ∧ hl x = hl y) ∨
  (∃ a b c d : δ, (a, b) ≠ (c, d) ∧ hn a b = hn c d)

/-- Key completeness lemma: opening the tree along any path and then
recomputing from the reached leaf reconstructs the tree's root. -/
theorem recompute_openTree? (hl : α → δ) (hn : δ → δ → δ) :
    ∀ (t : Tree α) (ds : List Dir) (a : α) (p : Proof δ),
      openTree? hl hn t ds = some (a, p) →
        recompute hl hn a p = Tree.root hl hn t := by
  intro t
  induction t with
  | leaf x =>
    intro ds a p h
    cases ds with
    | nil =>
      simp only [openTree?, Option.some.injEq, Prod.mk.injEq] at h
      obtain ⟨ha, hp⟩ := h
      subst ha; subst hp
      rfl
    | cons d ds => simp [openTree?] at h
  | node l r ihl ihr =>
    intro ds a p h
    cases ds with
    | nil => simp [openTree?] at h
    | cons d ds =>
      cases d with
      | L =>
        simp only [openTree?] at h
        cases hq : openTree? hl hn l ds with
        | none => rw [hq] at h; simp at h
        | some q =>
          rw [hq] at h
          simp only [Option.map_some, Option.some.injEq, Prod.mk.injEq] at h
          obtain ⟨ha, hp⟩ := h
          subst ha; subst hp
          have := ihl ds q.1 q.2 hq
          simp only [recompute, Tree.root, this]
      | R =>
        simp only [openTree?] at h
        cases hq : openTree? hl hn r ds with
        | none => rw [hq] at h; simp at h
        | some q =>
          rw [hq] at h
          simp only [Option.map_some, Option.some.injEq, Prod.mk.injEq] at h
          obtain ⟨ha, hp⟩ := h
          subst ha; subst hp
          have := ihr ds q.1 q.2 hq
          simp only [recompute, Tree.root, this]

/-- Completeness (Definition 3, Proposition 1): an honest membership proof
always verifies against the honest root. -/
theorem completeness [DecidableEq δ] (hl : α → δ) (hn : δ → δ → δ)
    (t : Tree α) (ds : List Dir) (a : α) (p : Proof δ)
    (hopen : openTree? hl hn t ds = some (a, p)) :
    verify hl hn (Tree.root hl hn t) a p = true := by
  have h := recompute_openTree? hl hn t ds a p hopen
  simp [verify, h]

/-- If two distinct leaf values recompute to the same root along the same
proof, then `hl` or `hn` has a collision. -/
theorem collision_of_recompute_eq (hl : α → δ) (hn : δ → δ → δ) :
    ∀ (p : Proof δ) (a a' : α),
      a ≠ a' →
      recompute hl hn a p = recompute hl hn a' p →
        HasCollision hl hn := by
  intro p
  induction p with
  | nil =>
    intro a a' hne heq
    exact Or.inl ⟨a, a', hne, heq⟩
  | cons step rest ih =>
    intro a a' hne heq
    obtain ⟨d, sib⟩ := step
    cases d with
    | L =>
      simp only [recompute] at heq
      by_cases hu : recompute hl hn a rest = recompute hl hn a' rest
      · exact ih a a' hne hu
      · refine Or.inr ⟨recompute hl hn a rest, sib,
          recompute hl hn a' rest, sib, ?_, heq⟩
        intro hc; injection hc with h1 _; exact hu h1
    | R =>
      simp only [recompute] at heq
      by_cases hu : recompute hl hn a rest = recompute hl hn a' rest
      · exact ih a a' hne hu
      · refine Or.inr ⟨sib, recompute hl hn a rest,
          sib, recompute hl hn a' rest, ?_, heq⟩
        intro hc; injection hc with _ h2; exact hu h2

/-- Soundness (Definition 4, Proposition 2): if a value `a` distinct from
the genuine leaf value `a'` verifies against the honest root along the
honest proof, then a hash collision exists. Contrapositively, under
collision resistance the server cannot open a position to a wrong value.
-/
theorem soundness [DecidableEq δ] (hl : α → δ) (hn : δ → δ → δ)
    (t : Tree α) (ds : List Dir) (a a' : α) (p : Proof δ)
    (hopen : openTree? hl hn t ds = some (a', p))
    (hverify : verify hl hn (Tree.root hl hn t) a p = true)
    (hne : a ≠ a') :
    HasCollision hl hn := by
  have hgen : recompute hl hn a' p = Tree.root hl hn t :=
    recompute_openTree? hl hn t ds a' p hopen
  have hfor : recompute hl hn a p = Tree.root hl hn t :=
    of_decide_eq_true hverify
  have heq : recompute hl hn a p = recompute hl hn a' p := by
    rw [hfor, hgen]
  exact collision_of_recompute_eq hl hn p a a' hne heq

/-- Proof size (Proposition 3): a membership proof has exactly one step
per level of the descended path. -/
theorem proof_length (hl : α → δ) (hn : δ → δ → δ) :
    ∀ (t : Tree α) (ds : List Dir) (a : α) (p : Proof δ),
      openTree? hl hn t ds = some (a, p) → p.length = ds.length := by
  intro t
  induction t with
  | leaf x =>
    intro ds a p h
    cases ds with
    | nil =>
      simp only [openTree?, Option.some.injEq, Prod.mk.injEq] at h
      obtain ⟨_, hp⟩ := h
      subst hp; rfl
    | cons d ds => simp [openTree?] at h
  | node l r ihl ihr =>
    intro ds a p h
    cases ds with
    | nil => simp [openTree?] at h
    | cons d ds =>
      cases d with
      | L =>
        simp only [openTree?] at h
        cases hq : openTree? hl hn l ds with
        | none => rw [hq] at h; simp at h
        | some q =>
          rw [hq] at h
          simp only [Option.map_some, Option.some.injEq, Prod.mk.injEq] at h
          obtain ⟨_, hp⟩ := h
          subst hp
          have := ihl ds q.1 q.2 hq
          simp [this]
      | R =>
        simp only [openTree?] at h
        cases hq : openTree? hl hn r ds with
        | none => rw [hq] at h; simp at h
        | some q =>
          rw [hq] at h
          simp only [Option.map_some, Option.some.injEq, Prod.mk.injEq] at h
          obtain ⟨_, hp⟩ := h
          subst hp
          have := ihr ds q.1 q.2 hq
          simp [this]

end Ads
