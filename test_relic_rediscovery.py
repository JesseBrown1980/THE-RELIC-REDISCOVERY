import unittest

from relic_rediscovery import FREE_CENTER, anchor, exponent, multiplier, structure, waves


class RelicRediscoveryTests(unittest.TestCase):
    def test_structural_landings(self):
        self.assertEqual(
            [anchor(level) for level in range(5)],
            [27, 243, 6561, 531441, 129140163],
        )

    def test_expanding_multipliers(self):
        self.assertEqual([multiplier(level) for level in range(4)], [9, 27, 81, 243])

    def test_intermediate_waves_are_preserved(self):
        self.assertEqual(waves(0), (81, 243))
        self.assertEqual(waves(1), (729, 2187, 6561))
        self.assertEqual(waves(2), (19683, 59049, 177147, 531441))

    def test_last_wave_is_next_anchor(self):
        for level in range(10):
            self.assertEqual(waves(level)[-1], anchor(level + 1))

    def test_closed_form_exponents(self):
        self.assertEqual([exponent(level) for level in range(5)], [3, 5, 8, 12, 17])

    def test_free_center_is_invariant(self):
        for level in range(10):
            self.assertEqual(structure(level).center, FREE_CENTER)

    def test_negative_levels_are_rejected(self):
        with self.assertRaises(ValueError):
            anchor(-1)


if __name__ == "__main__":
    unittest.main()
