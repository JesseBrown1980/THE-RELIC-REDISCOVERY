"""The zero-centred frame and its interfaces (FRAME-AND-INTERFACES.md).

Integer-only reference implementation. Every check is exact.

One centre, coordinate 0, and an observer who supplies the readout frame:
    (0; p1, p2, p3; O),   R(0) = 0.
"""

from __future__ import annotations

import argparse
from itertools import permutations, product

CENTER_COUNT = 1
CENTER_COORDINATE = 0


# --------------------------------------------------------------------------
# 1. The frame: points around a fixed zero


def rotate_about_center(point: tuple[int, ...], perm: tuple[int, ...]) -> tuple[int, ...]:
    """A coordinate permutation acting on an outer point; it fixes the centre."""
    return tuple(point[i] for i in perm)


def integer_rank(rows: list[list[int]]) -> int:
    """Exact rank over the rationals by fraction-free (Bareiss) elimination."""
    m = [list(r) for r in rows]
    if not m:
        return 0
    n_rows, n_cols = len(m), len(m[0])
    rank, prev = 0, 1
    for col in range(n_cols):
        pivot = next((r for r in range(rank, n_rows) if m[r][col] != 0), None)
        if pivot is None:
            continue
        m[rank], m[pivot] = m[pivot], m[rank]
        for r in range(rank + 1, n_rows):
            for c in range(col + 1, n_cols):
                num = m[rank][col] * m[r][c] - m[r][col] * m[rank][c]
                assert num % prev == 0
                m[r][c] = num // prev
            m[r][col] = 0
        prev = m[rank][col]
        rank += 1
        if rank == n_rows:
            break
    return rank


def frame_dimension(points: list[tuple[int, ...]]) -> int:
    """dim aff{0, p1, ..., pk} = rank [p1 ... pk]."""
    return integer_rank([list(p) for p in points])


# --------------------------------------------------------------------------
# 2. Reconstruction: when a fraction of the data is enough


def injectivity_witness(model: list[tuple[int, ...]], observe) -> tuple | None:
    """None if the observer is injective on the model class, else a colliding pair."""
    seen: dict = {}
    for x in model:
        y = observe(x)
        if y in seen and seen[y] != x:
            return (seen[y], x)
        seen[y] = x
    return None


def ray_model(direction: tuple[int, ...], span: int) -> list[tuple[int, ...]]:
    """States constrained to the line through 0 and one point: x = t * direction."""
    return [tuple(t * d for d in direction) for t in range(-span, span + 1)]


def box_model(dim: int, span: int) -> list[tuple[int, ...]]:
    """Unconstrained states in a box."""
    return [tuple(v) for v in product(range(-span, span + 1), repeat=dim)]


# --------------------------------------------------------------------------
# 3. Nested addresses: the network inside the network


def addresses(depth: int) -> list[tuple[int, ...]]:
    """A_d = {-1, 0, +1}^d."""
    return [tuple(a) for a in product((-1, 0, 1), repeat=depth)]


def landing_depth(level: int) -> int:
    """Relic landing exponent e_n = 3 + n(n+3)/2; A_n = 3^(e_n)."""
    return 3 + level * (level + 3) // 2


def wave_depths(level: int) -> list[int]:
    """Ternary depths strictly between landing n and landing n+1."""
    return list(range(landing_depth(level) + 1, landing_depth(level + 1)))


def subtree_size(total_depth: int, prefix_len: int) -> int:
    """A finite address prefix selects a whole subtree of 3^(D - k) leaves."""
    return 3 ** (total_depth - prefix_len)


def nested_eval(depth: int, leaf_value, combine, prefix: tuple[int, ...] = ()) -> tuple[int, int]:
    """F_u = f(x_u, F_u1, F_u2, F_u3), evaluated lazily on the subtree under `prefix`.

    Returns (value, nodes_materialised). Only the selected subtree is built.
    """
    if len(prefix) == depth:
        return leaf_value(prefix), 1
    vals, count = [], 1
    for digit in (-1, 0, 1):
        v, c = nested_eval(depth, leaf_value, combine, prefix + (digit,))
        vals.append(v)
        count += c
    return combine(prefix, vals), count


# --------------------------------------------------------------------------
# 4. Nested S3 symmetry: the iterated wreath product


def nested_s3_generators(depth: int) -> list[tuple[int, ...]]:
    """Generators of the S3 acting at every internal node, as leaf permutations."""
    leaves = list(product(range(3), repeat=depth))
    index = {leaf: i for i, leaf in enumerate(leaves)}
    gens = []
    for level in range(depth):
        for node in product(range(3), repeat=level):
            for sigma in ((1, 0, 2), (1, 2, 0)):  # a transposition and a 3-cycle
                perm = []
                for leaf in leaves:
                    if leaf[:level] == node:
                        moved = leaf[:level] + (sigma[leaf[level]],) + leaf[level + 1 :]
                        perm.append(index[moved])
                    else:
                        perm.append(index[leaf])
                gens.append(tuple(perm))
    return gens


def group_order(generators: list[tuple[int, ...]]) -> int:
    """Order of the permutation group by closure."""
    n = len(generators[0])
    identity = tuple(range(n))
    seen = {identity}
    frontier = [identity]
    while frontier:
        nxt = []
        for g in frontier:
            for s in generators:
                h = tuple(g[s[i]] for i in range(n))
                if h not in seen:
                    seen.add(h)
                    nxt.append(h)
        frontier = nxt
    return len(seen)


def wreath_order(depth: int) -> int:
    """6^((3^d - 1)/2): one S3 per internal node of the depth-d ternary tree."""
    return 6 ** ((3**depth - 1) // 2)


# --------------------------------------------------------------------------
# 5. Three bodies around a zero centre of mass


def eisenstein_rotate(p: tuple[int, int]) -> tuple[int, int]:
    """Multiply a + b*w by w (w = e^(2 pi i/3)): exact 120-degree rotation."""
    a, b = p
    return (-b, a - b)


def symmetric_triangle(p: tuple[int, int]) -> list[tuple[int, int]]:
    """One point plus the zero centre fixes the equilateral (Lagrange) triangle."""
    q = eisenstein_rotate(p)
    return [p, q, eisenstein_rotate(q)]


def jacobi(masses: tuple[int, int, int], q: list[tuple[int, ...]]):
    """Scaled Jacobi coordinates: (M*R_cm, r, (m1+m2)*rho), all integer."""
    m1, m2, m3 = masses
    dim = len(q[0])
    total = tuple(m1 * q[0][k] + m2 * q[1][k] + m3 * q[2][k] for k in range(dim))
    r = tuple(q[1][k] - q[0][k] for k in range(dim))
    rho = tuple(
        (m1 + m2) * q[2][k] - (m1 * q[0][k] + m2 * q[1][k]) for k in range(dim)
    )
    return total, r, rho


def from_jacobi(masses: tuple[int, int, int], r: tuple[int, ...], rho: tuple[int, ...]):
    """Positions in the zero centre-of-mass frame, as (numerators, common denominator)."""
    m1, m2, m3 = masses
    m12, mt = m1 + m2, m1 + m2 + m3
    den = m12 * mt
    q1 = tuple(-m2 * mt * r[k] - m3 * rho[k] for k in range(len(r)))
    q2 = tuple(m1 * mt * r[k] - m3 * rho[k] for k in range(len(r)))
    q3 = tuple(m12 * rho[k] for k in range(len(r)))
    return [q1, q2, q3], den


# --------------------------------------------------------------------------
# 6. HEB-C: the local zero and the torus ground space


def s3_elements() -> list[tuple[int, ...]]:
    return list(permutations(range(3)))


def compose(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a[b[i]] for i in range(len(b)))


def inverse(a: tuple[int, ...]) -> tuple[int, ...]:
    out = [0] * len(a)
    for i, ai in enumerate(a):
        out[ai] = i
    return tuple(out)


def conjugacy_classes(group: list[tuple[int, ...]]) -> list[frozenset]:
    classes, seen = [], set()
    for g in group:
        if g in seen:
            continue
        cls = frozenset(compose(compose(h, g), inverse(h)) for h in group)
        classes.append(cls)
        seen |= cls
    return classes


def quantum_double_anyons(group: list[tuple[int, ...]]) -> int:
    """Number of irreps of D(G): sum over classes [g] of #classes of the centralizer of g."""
    total = 0
    for cls in conjugacy_classes(group):
        g = next(iter(cls))
        centralizer = [h for h in group if compose(h, g) == compose(g, h)]
        total += len(conjugacy_classes(centralizer))
    return total


# --------------------------------------------------------------------------
# 7. HTTP-0 transport: the address travels, the leaves regenerate


def transported_address(level: int, step: int) -> bytes:
    return f"RELIC|level={level}|step={step}".encode()


def regenerate_leaf(address: bytes) -> int:
    fields = dict(part.split("=") for part in address.decode().split("|")[1:])
    level, step = int(fields["level"]), int(fields["step"])
    return 3 ** (landing_depth(level) + step)


# --------------------------------------------------------------------------


def report() -> str:
    rows = [
        f"FRAME|center_count={CENTER_COUNT}|center_coordinate={CENTER_COORDINATE}",
        "DIMENSION|"
        + "|".join(
            f"k={k}:dim={frame_dimension([tuple(int(i == j) for i in range(4)) for j in range(k)])}"
            for k in range(1, 5)
        ),
        f"RECONSTRUCT|ray_one_point_plus_zero_injective="
        f"{int(injectivity_witness(ray_model((2, -1, 3), 40), lambda x: x[0]) is None)}"
        f"|box_one_coordinate_injective="
        f"{int(injectivity_witness(box_model(2, 3), lambda x: x[0]) is None)}",
        "NESTING|landing_depths="
        + ",".join(str(landing_depth(n)) for n in range(5))
        + "|addresses_d3="
        + str(len(addresses(3))),
        f"WREATH|d1={group_order(nested_s3_generators(1))}|d2={group_order(nested_s3_generators(2))}"
        f"|formula_d1={wreath_order(1)}|formula_d2={wreath_order(2)}|formula_d3={wreath_order(3)}",
        f"THREE_BODY|triangle_sum_zero="
        f"{int(tuple(map(sum, zip(*symmetric_triangle((5, 2))))) == (0, 0))}",
        f"HEBC|quantum_double_S3_anyons={quantum_double_anyons(s3_elements())}"
        f"|torus_ground_space=8",
        f"HTTP0|address_bytes={len(transported_address(4, 5))}"
        f"|leaf_digits={len(str(regenerate_leaf(transported_address(4, 5))))}",
    ]
    return "\n".join(rows)


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(report())


if __name__ == "__main__":
    main()
