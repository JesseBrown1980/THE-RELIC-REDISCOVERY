import unittest

from relic_rediscovery import (
    CENTER_VALUE,
    CURRENT_UTTERANCE_ORDER,
    FREE_CENTER,
    Z_LEVELS,
    anchor,
    center_at_z,
    exponent,
    multiplier,
    render,
    structure,
    waves,
)


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
            self.assertEqual(structure(level).center_value, CENTER_VALUE)

    def test_center_is_one_at_every_z_level(self):
        for z in (*Z_LEVELS, -999, 999, "ANY_Z"):
            self.assertEqual(center_at_z(z), 1)

    def test_z_closes_forward_without_bidirectionality(self):
        output = render(1)
        self.assertIn("X -> Y -> Z -> END_0 -> NEXT_IS", output)
        self.assertIn("bidirectional=0", output)
        self.assertIn("reverse=0", output)
        self.assertIn("round_trip=0", output)
        self.assertIn("exchange=0", output)

    def test_center_sign_preserves_current_utterance_order(self):
        self.assertEqual(
            CURRENT_UTTERANCE_ORDER,
            ("HBI", "HBP", "SHA", "SH", "HASH"),
        )

    def test_negative_levels_are_rejected(self):
        with self.assertRaises(ValueError):
            anchor(-1)


if __name__ == "__main__":
    unittest.main()
