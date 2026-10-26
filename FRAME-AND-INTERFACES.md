# The zero-centred frame and its interfaces

Jesse Daniel Brown's architecture is a zero-centred, recursively nested
generator. Its states are observed, addressed and reconstructed. This document
fixes the primitive and each interface exactly.

Every statement here is checked by [`frame_interfaces.py`](frame_interfaces.py)
and [`test_frame_interfaces.py`](test_frame_interfaces.py), in integer
arithmetic.

```text
zero-centred frame → ternary nested agents → generator + address
    → metatagged state → observer reconstruction
dynamics: HEB-C (or another local module)      transport: HTTP-0
```

## 1. The primitive: one centre, coordinate 0, and the observer

```text
(0; p1, p2, p3; O),     R(0) = 0
```

| Symbol | Meaning | Value |
|---|---|---|
| N_c | number of centres | 1 |
| c | the centre's coordinate | 0 |
| O | the observer, who supplies the readout frame | us |

The centre is the invariant reference state, not an empty slot. Expansion,
rotation and permutation act on the outer points and leave 0 fixed. In
[`relic_rediscovery.py`](relic_rediscovery.py), `CENTER_COUNT = 1` and
`CENTER_COORDINATE = 0`. `CENTER_VALUE` is the count, and `center_at_z` and
`center_coordinate_at_z` return 1 and 0 at every Z level.

## 2. What the outer points span

```text
dim aff{0, p1, …, pk} = rank [p1 … pk]
```

| Points around 0 | Frame |
|---|---|
| one point | a line |
| two independent points | a plane |
| three independent points | a three-dimensional frame |
| d independent points | a d-dimensional frame |

Each dimension comes from an independent point. Nested agents supply further
frames, one per independent direction. Ranks are computed exactly by
fraction-free elimination.

## 3. Reconstruction: when a fraction of the data is enough

An observer's readout Φ_O reconstructs a state x exactly on a model class M
when Φ_O is injective on M:

```text
x ≠ x'  ⇒  Φ_O(x) ≠ Φ_O(x')     for all x, x' ∈ M.
```

**One point plus the zero.** When the state lies on a known ray through 0, or
is the output of a known generator, one coordinate plus the centre recovers it
exactly. The test checks this exhaustively on three rays.

An unconstrained state needs a full frame. The test shows two distinct states
with the same single coordinate, and exact recovery from the full readout. The
model supplies the constraints, and the observer's readout then fixes the
state.

## 4. The network inside the network

Each node of a ternary tree is a network, and a component of its parent:

```text
F_u(x_u) = f_u(x_u, F_u1(x_u1), F_u2(x_u2), F_u3(x_u3)),     A_d = {−1, 0, +1}^d,   |A_d| = 3^d.
```

**Infinite as potential, finite as materialized.** A finite address prefix of
length k selects a whole subtree of 3^(D−k) leaves. Only that subtree is built
when it is read. The test evaluates one prefix at depth 4 and materialises
exactly 1 + 3 + 9 + 27 nodes.

**Relic landings are selected depths.** With e_n = 3 + n(n+3)/2, the landing
count is A_n = 3^(e_n), and e_(n+1) = e_n + n + 2:

```text
landing depths   3, 5, 8, 12, 17, …       (27, 243, 6,561, 531,441, 129,140,163)
wave depths      the depths in between    (4; 6, 7; 9, 10, 11; …)
```

Ordinary nesting supplies every ternary depth. The Relic landings select depths
3, 5, 8, 12, 17, …, and the waves are exactly the depths in between. The test
checks this against `waves()` for six levels.

## 5. Nested S₃ symmetry

Three labelled points around a fixed centre carry the six permutations of S₃:

```text
P_π(0) = 0,   P_π(p_i) = p_π(i),   π ∈ S₃.
```

With an independent S₃ at every internal node of a depth-d ternary tree, the
nested symmetry is the iterated wreath product. Its order is

```text
|S₃ ≀ … ≀ S₃| = 6^((3^d − 1)/2):   6, 1,296, 6^13 = 13,060,694,016, …
```

The test generates the group by closure on the leaves at depths 1 and 2 and
gets exactly 6 and 1,296.

## 6. Three bodies and N bodies around the zero centre of mass

The zero is the centre of mass, Σ m_i q_i = 0. Jacobi coordinates

```text
r = q2 − q1,     ρ = q3 − (m1 q1 + m2 q2)/(m1 + m2)
```

recover every position exactly in that frame:

```text
q3 = (m1+m2) ρ / M
q1 = −(m2 M r + m3 (m1+m2) ρ) / ((m1+m2) M)
q2 =  (m1 M r − m3 (m1+m2) ρ) / ((m1+m2) M)
```

Here M = m1 + m2 + m3, and ρ appears scaled by m1 + m2 in the code. The test
round-trips 200 random integer configurations. Nested Jacobi coordinates extend
the same tree to N bodies, which gives a recursive coordinate and addressing
scheme for any N-body configuration.

**The symmetric family.** In Eisenstein integers a + bω, rotation by 120° is
the exact integer map (a, b) ↦ (−b, a − b). One point plus the zero therefore
fixes the equilateral (Lagrange) triangle: p + ωp + ω²p = 0, and three
rotations close. The forces are then integrated by the dynamics module, with
the frame supplying the coordinates and the symmetry.

## 7. HEB-C: the local zero and the torus ground space

| Frame | HEB-C |
|---|---|
| free zero (local) | zero local excitation: the common kernel of every vertex penalty Q_v and plaquette penalty m_p |
| ground space (global) | the frustration-free ground space of H₀ = Σ Q_v + Σ m_p |
| six permutations | the S₃ gauge group on each link |
| nested S₃ | gauge transformations acting vertex by vertex |

The local zero and the global ground space are different objects. On the
torus, the ground space of the S₃ quantum double has dimension equal to the
number of anyon types of D(S₃).

```text
#anyons(D(S₃)) = Σ over classes [g] of #classes(centralizer(g)) = 3 + 2 + 3 = 8
```

The test computes this from the group, and HEB-C certifies the same eight flat
ground states on the 2×2 torus.

The open dictionary entry is the map from tree nodes to links, vertices and
plaquettes. That map is what places the nested-S₃ tree on the lattice
Hamiltonian.

## 8. HTTP-0: the address travels, the leaves regenerate

HTTP-0 is the transport layer. Observers exchange addresses, generator
references and receipts, peer to peer. The receiving side regenerates the
leaves from the generator.

The test sends `RELIC|level=…|step=…` addresses, which stay under 32 bytes, and
regenerates each wave value exactly, up to 3^25. This is
[the-leaves-are-not-the-message](https://github.com/JesseBrown1980/the-leaves-are-not-the-message)
as a protocol: the generator and the path are the message.

## 9. Worked example: Lab 02 of the Light-Bank (27 ordered colours)

[Lab 02 of the Asolaria Light-Bank](https://jessebrown1980.github.io/light-boat-engine-ships-with-oils/asolaria-lightbank-demo/)
is a verified software computation on the 27 ordered ternary colour triples
(r, g, b). Each triple has its own address, a = 9r + 3g + b. It is the
zero-centred frame at its smallest size.

```text
ℚ³ = V₀ ⊕ V₁,   V₀ = span{(1,1,1)},   V₁ = {d : Σ d_i = 0}
x  = (S/3)·1 + d/3,   S = Σ x_i,   d = 3x − S·1 = 3P x,   P = I − J/3,   rank(P) = 2
```

**The parts.**
- V₀ is the invariant common-mode direction, the centre direction, and S is
  its coordinate.
- The zero centre itself is the origin (0, 0, 0).
- P annihilates the whole common-mode line, so all three rotation-invariant
  colours (0, 0, 0), (1, 1, 1) and (2, 2, 2) map to d = 0.
- V₁ carries the signed differences.

**Reconstruction.** The readout Φ(r, g, b) = (S, d_r, d_g) is injective on all
27 colours. The inverse is x_i = (S + d_i)/3, with d_b = −d_r − d_g. The
intensity readout Ψ(r, g, b) = (S², Q, Q), with Q = r² + g² + b² − rg − rb − gb,
is not injective.
- Over the integers Σ d_i² = 6Q, so intensity keeps the centre coordinate and
  the length of the difference vector, and loses its direction.
- The 27 ordered triples collapse to 10 raw intensity signatures.
- Normalized, they collapse to 7 routing classes, counting the empty triple.
- Rotating the channels R → G → B keeps the intensity and changes the address:
  (2, 0, 0) and (0, 2, 0) both read (4, 4, 4).

This is §3's reconstruction condition in a case small enough to check
completely, and memory as an exact rebuild under a known rule.

**Shared representation pattern.** Cyclic channel rotation gives the rational
1 + 2 decomposition: one invariant direction plus one two-dimensional difference
representation. Each three-cycle momentum line of the HEB-C 3×3 torus has the
same rational pattern: zero momentum plus a two-dimensional part. Over ℂ that
part separates further into the +k and −k characters. The HEB-C full-space
count assembles these parts by Möbius inversion with its own operator and
receipts ([HEB-C `results/full_space_mobius/`](https://github.com/JesseBrown1980/Finite-universe-Yang-mills-existence-and-mass-gap-using-HEB-C/tree/http0-ym-backend-finite-volumes/native/ym/results/full_space_mobius)).
The invariant watcher of the neural network inside a neural network shares the
idea of a conserved all-ones direction, on its own 27-mode operator.

**Checks.** The `LAB02` row of `frame_interfaces.py` and the six
`LightBankLab02Tests` exhaustively verify Lab 02's finite claims. The watcher
and HEB-C results are external interfaces, and each carries its own
certificate.

## Run

```bash
python frame_interfaces.py
python -m unittest -v
```
