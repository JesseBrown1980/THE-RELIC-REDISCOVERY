import math
import unittest

from sentience_microtubule_model import (
    CENTER_ANATOMICAL_HYPOTHESIS,
    CENTER_VALUE,
    EVIDENCE_ORDER,
    NEXT_PATH,
    PHYSICAL_STATUS,
    SENTIENCE_LABEL,
    TubuleFixture,
    assign_foggy_subnet,
    fuzzy_membership,
    landing_offset,
    landing_residuals,
    logical_port_address,
    normalized_weighted_degree,
    permutation_p_value,
    predicted_landing_frequencies,
    recurrence_score,
    render_demo,
)


class SentienceMicrotubuleModelTests(unittest.TestCase):
    def test_evidence_order_is_exact(self):
        self.assertEqual(EVIDENCE_ORDER, ("HBI", "HBP", "SHA", "SH", "HASH"))

    def test_sentience_and_claustrum_are_scoped_hypothesis_labels(self):
        self.assertEqual(SENTIENCE_LABEL, "SEN_T_I_E_N_C_E")
        self.assertEqual(CENTER_ANATOMICAL_HYPOTHESIS, "CLAUSTRUM")
        self.assertEqual(CENTER_VALUE, 1)
        self.assertEqual(PHYSICAL_STATUS, "UNVERIFIED")

    def test_landing_offsets_preserve_relic_recurrence(self):
        self.assertEqual([landing_offset(level) for level in range(5)], [0, 2, 5, 9, 14])

    def test_exact_ternary_landing_spectrum_has_zero_residual(self):
        frequencies = predicted_landing_frequencies(2.0, 5)
        residuals = landing_residuals(frequencies, 2.0, 4)
        self.assertTrue(all(abs(residual) < 1e-12 for residual in residuals))
        self.assertEqual(recurrence_score(frequencies, 2.0, 4, 1e-10), 5)

    def test_off_grid_spectrum_does_not_force_a_match(self):
        residual = landing_residuals((2.0 * 3.0**1.5,), 2.0, 4)[0]
        self.assertGreater(residual, 0.49)
        self.assertEqual(recurrence_score((2.0 * 3.0**1.5,), 2.0, 4, 0.1), 0)

    def test_permutation_test_is_deterministic_and_bounded(self):
        frequencies = predicted_landing_frequencies(2.0, 4)
        first = permutation_p_value(frequencies, 2.0, 3, 0.01, trials=99, seed=7)
        second = permutation_p_value(frequencies, 2.0, 3, 0.01, trials=99, seed=7)
        self.assertEqual(first, second)
        self.assertGreater(first, 0.0)
        self.assertLessEqual(first, 1.0)

    def test_foggy_memberships_are_normalized(self):
        memberships = fuzzy_membership(
            (0.9, 0.1), ((1.0, 0.0), (0.0, 1.0)), sigma=0.25
        )
        self.assertTrue(math.isclose(sum(memberships), 1.0))
        self.assertGreater(memberships[0], memberships[1])

    def test_clear_subnet_is_admitted(self):
        self.assertEqual(assign_foggy_subnet((0.8, 0.1, 0.1)), "FOGGY_SUBNET_0")

    def test_ambiguous_subnet_is_held(self):
        self.assertEqual(
            assign_foggy_subnet((0.5, 0.5), threshold=0.5, margin=0.1),
            "HELD_FOR_REVIEW",
        )

    def test_claustrum_analogy_requires_measured_graph_centrality(self):
        adjacency = ((0.0, 1.0, 1.0), (1.0, 0.0, 4.0), (1.0, 4.0, 0.0))
        self.assertLess(normalized_weighted_degree(adjacency, 0), 1.0)
        self.assertEqual(normalized_weighted_degree(adjacency, 1), 1.0)

    def test_logical_port_is_stable_and_not_a_network_port(self):
        first = logical_port_address("T1", (0.2, 0.8))
        second = logical_port_address("T1", (0.2, 0.8))
        self.assertEqual(first, second)
        self.assertTrue(first.startswith("BIO0-"))
        self.assertNotIn("http", first.lower())

    def test_render_fails_closed_at_z_and_preserves_boundaries(self):
        output = render_demo()
        rows = output.splitlines()
        self.assertEqual([row.split("|", 1)[0] for row in rows[1:6]], list(EVIDENCE_ORDER))
        self.assertIn(f"path={NEXT_PATH}", output)
        self.assertIn("negative=S", output)
        self.assertIn("z_self_connected=1", output)
        self.assertIn("logical_instant=1", output)
        self.assertIn("physical_instant=UNVERIFIED", output)
        self.assertIn("order=HBI_HBP_SHA_SH_HASH", output)
        self.assertIn("transport_chain_inferred=0", output)
        self.assertIn("http=0", output)
        self.assertIn("socket_open=0", output)
        self.assertIn("network=0", output)
        self.assertIn("physical_status=UNVERIFIED", output)
        self.assertTrue(all(row.endswith("json=0") for row in rows))

    def test_invalid_biological_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            fuzzy_membership((-1.0,), ((0.0,),), 1.0)
        with self.assertRaises(ValueError):
            predicted_landing_frequencies(0.0, 1)
        with self.assertRaises(ValueError):
            normalized_weighted_degree(((0.0, 1.0),), 0)


if __name__ == "__main__":
    unittest.main()
