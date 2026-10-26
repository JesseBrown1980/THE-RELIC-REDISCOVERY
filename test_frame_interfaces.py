import random
import unittest

from frame_interfaces import (
    colour_address,
    colour_intensity,
    colour_intensity_class,
    colour_inverse,
    colour_split,
    colour_triples,
    integer_rank,
    projector_rank,
    CENTER_COORDINATE,
    CENTER_COUNT,
    addresses,
    box_model,
    eisenstein_rotate,
    frame_dimension,
    from_jacobi,
    group_order,
    injectivity_witness,
    jacobi,
    landing_depth,
    nested_eval,
    nested_s3_generators,
    quantum_double_anyons,
    ray_model,
    regenerate_leaf,
    rotate_about_center,
    s3_elements,
    subtree_size,
    symmetric_triangle,
    transported_address,
    wave_depths,
    wreath_order,
)
from relic_rediscovery import anchor, exponent, waves


class FrameTests(unittest.TestCase):
    def test_one_centre_at_coordinate_zero(self):
        self.assertEqual((CENTER_COUNT, CENTER_COORDINATE), (1, 0))
        for perm in ((0, 1, 2), (1, 2, 0), (2, 0, 1), (1, 0, 2)):
            self.assertEqual(rotate_about_center((0, 0, 0), perm), (0, 0, 0))

    def test_frame_dimension_is_the_rank_of_the_outer_points(self):
        e = [tuple(int(i == j) for i in range(5)) for j in range(5)]
        for k in range(1, 6):
            self.assertEqual(frame_dimension(e[:k]), k)
        # dependent points add no dimension
        self.assertEqual(frame_dimension([(1, 2, 3), (2, 4, 6), (0, 1, 1)]), 2)
        self.assertEqual(frame_dimension([(3, 1, 0), (1, 0, 2), (4, 1, 2)]), 2)


class ReconstructionTests(unittest.TestCase):
    def test_one_point_plus_zero_reconstructs_a_constrained_state(self):
        for direction in ((2, -1, 3), (0, 5, 1), (1, 1, 1, 1)):
            nz = next(i for i, d in enumerate(direction) if d != 0)
            self.assertIsNone(injectivity_witness(ray_model(direction, 50), lambda x: x[nz]))

    def test_one_coordinate_cannot_reconstruct_an_unconstrained_state(self):
        pair = injectivity_witness(box_model(2, 3), lambda x: x[0])
        self.assertIsNotNone(pair)
        self.assertEqual(pair[0][0], pair[1][0])
        self.assertNotEqual(pair[0], pair[1])

    def test_full_frame_reconstructs_every_state(self):
        self.assertIsNone(injectivity_witness(box_model(3, 2), lambda x: x))


class NestingTests(unittest.TestCase):
    def test_addresses_and_landings(self):
        self.assertEqual([len(addresses(d)) for d in range(1, 5)], [3, 9, 27, 81])
        for n in range(8):
            self.assertEqual(landing_depth(n), exponent(n))
            self.assertEqual(3 ** landing_depth(n), anchor(n))
            self.assertEqual(landing_depth(n + 1) - landing_depth(n), n + 2)

    def test_waves_are_the_intervening_depths(self):
        for n in range(6):
            depths = wave_depths(n) + [landing_depth(n + 1)]
            self.assertEqual(tuple(3**d for d in depths), waves(n))

    def test_prefix_selects_a_subtree_lazily(self):
        depth = 4
        value, built = nested_eval(depth, lambda a: sum(a), lambda u, v: sum(v), prefix=(1,))
        self.assertEqual(value, 27 * 1)  # one fixed digit, the rest sum to 0
        self.assertEqual(built, sum(3**k for k in range(depth)))  # 1+3+9+27 nodes
        self.assertEqual(subtree_size(depth, 1), 27)


class NestedSymmetryTests(unittest.TestCase):
    def test_wreath_product_order(self):
        self.assertEqual(group_order(nested_s3_generators(1)), 6)
        self.assertEqual(group_order(nested_s3_generators(2)), 1296)
        self.assertEqual([wreath_order(d) for d in (1, 2, 3)], [6, 1296, 6**13])


class ThreeBodyTests(unittest.TestCase):
    def test_one_point_plus_zero_fixes_the_symmetric_triangle(self):
        for p in ((5, 2), (-3, 7), (1, 0), (11, -4)):
            tri = symmetric_triangle(p)
            self.assertEqual(tuple(map(sum, zip(*tri))), (0, 0))
            self.assertEqual(eisenstein_rotate(tri[2]), p)  # three rotations close

    def test_jacobi_coordinates_in_the_zero_frame_are_exact(self):
        rng = random.Random(3)
        for _ in range(200):
            m = (rng.randint(1, 9), rng.randint(1, 9), rng.randint(1, 9))
            mt = sum(m)
            q1 = (rng.randint(-50, 50) * mt, rng.randint(-50, 50) * mt)
            q2 = (rng.randint(-50, 50) * mt, rng.randint(-50, 50) * mt)
            # place body 3 so that the centre of mass is exactly 0
            num = tuple(-(m[0] * q1[k] + m[1] * q2[k]) for k in range(2))
            if any(x % m[2] for x in num):
                continue
            q3 = tuple(x // m[2] for x in num)
            total, r, rho = jacobi(m, [q1, q2, q3])
            self.assertEqual(total, (0, 0))
            back, den = from_jacobi(m, r, rho)
            for qi, bi in zip((q1, q2, q3), back):
                self.assertEqual(tuple(den * x for x in qi), bi)


class HebcTests(unittest.TestCase):
    def test_quantum_double_of_s3_has_eight_anyons(self):
        self.assertEqual(quantum_double_anyons(s3_elements()), 8)


class TransportTests(unittest.TestCase):
    def test_address_travels_and_the_leaf_regenerates(self):
        for level in range(6):
            for step in range(level + 3):
                addr = transported_address(level, step)
                self.assertLess(len(addr), 32)
                self.assertEqual(regenerate_leaf(addr), anchor(level) * 3**step)


class LightBankLab02Tests(unittest.TestCase):
    def test_twenty_seven_ordered_addresses(self):
        addrs = sorted(colour_address(t) for t in colour_triples())
        self.assertEqual(addrs, list(range(27)))
        self.assertEqual(colour_address((2, 0, 0)), 18)

    def test_centre_plus_differences_inverts_exactly(self):
        for t in colour_triples():
            s, d = colour_split(t)
            self.assertEqual(sum(d), 0)  # differences live off the free centre
            self.assertEqual(colour_inverse(s, d), t)
        self.assertEqual(colour_split((2, 0, 0)), (2, (4, -2, -2)))

    def test_intensity_alone_loses_the_order(self):
        self.assertEqual(len({colour_intensity(t) for t in colour_triples()}), 10)
        self.assertEqual(len({colour_intensity_class(t) for t in colour_triples()}), 7)
        self.assertEqual(colour_intensity((2, 0, 0)), (4, 4, 4))
        # a rotation R -> G -> B keeps the intensity and changes the address
        t, rot = (2, 0, 0), (0, 2, 0)
        self.assertEqual(colour_intensity(t), colour_intensity(rot))
        self.assertNotEqual(colour_address(t), colour_address(rot))

    def test_intensity_keeps_only_the_centre_and_the_difference_norm(self):
        for t in colour_triples():
            s, d = colour_split(t)
            a, q, _ = colour_intensity(t)
            self.assertEqual(a, s * s)
            self.assertEqual(sum(x * x for x in d), 6 * q)

    def test_projector_off_the_centre(self):
        self.assertEqual(projector_rank(), 2)
        three_p = [[3 * (i == j) - 1 for j in range(3)] for i in range(3)]
        self.assertEqual([sum(row) for row in three_p], [0, 0, 0])  # kills the all-ones centre
        self.assertEqual(integer_rank([[1, 1, 1]]), 1)

    def test_same_split_as_the_momentum_sectors(self):
        # Z3 rotating the channels: V = V^T (dimension 1, the centre) + one
        # two-dimensional rational part (the differences) -- the Mobius split
        # HEB-C uses for each momentum line.
        invariant = [t for t in colour_triples() if t[0] == t[1] == t[2]]
        self.assertEqual(len(invariant), 3)  # one per value of S/3: the centre line
        self.assertEqual(1 + projector_rank(), 3)


if __name__ == "__main__":
    unittest.main()
