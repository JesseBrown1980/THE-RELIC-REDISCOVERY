import math
import unittest

from tridoscope_model import (
    CENTER_SLOT,
    CENTER_VALUE,
    EVIDENCE_ORDER,
    GYRO_FAMILIES,
    LIGHT_SPEED_M_S,
    OpticalSurface,
    add_vectors,
    circular_beam_intensity,
    coating_retention,
    domain_status,
    gyro_family,
    invert_gyro,
    optical_torque,
    oiled_light_state,
    radiation_force_vector,
    render_demo,
    shannon_entropy_bits,
    spherical_shelf,
    thrust_to_weight,
)


class TridoscopeModelTests(unittest.TestCase):
    def test_absorber_receives_p_over_c(self):
        surface = OpticalSurface(1.0, 0.0, 0.0)
        self.assertTrue(math.isclose(surface.force_newtons(3.0), 3.0 / LIGHT_SPEED_M_S))

    def test_reflector_receives_two_p_over_c(self):
        surface = OpticalSurface(0.0, 1.0, 0.0)
        self.assertTrue(math.isclose(surface.force_newtons(3.0), 6.0 / LIGHT_SPEED_M_S))

    def test_forward_transmission_transfers_no_momentum_in_this_model(self):
        surface = OpticalSurface(0.0, 0.0, 1.0)
        self.assertEqual(surface.force_newtons(3.0), 0.0)

    def test_optical_coefficients_fail_closed(self):
        with self.assertRaises(ValueError):
            OpticalSurface(0.5, 0.5, 0.5)

    def test_circular_intensity_uses_pi_radius_squared(self):
        self.assertTrue(math.isclose(circular_beam_intensity(math.pi, 1.0), 1.0))

    def test_photobleaching_retention_only_decreases(self):
        retained = coating_retention(1.0, 0.01, 2.0, 3.0)
        self.assertGreater(retained, 0.0)
        self.assertLess(retained, 1.0)

    def test_three_orthogonal_optical_forces_remain_three_dimensional(self):
        surface = OpticalSurface(0.0, 1.0, 0.0)
        forces = tuple(
            radiation_force_vector(surface, 1.0, axis)
            for axis in ((1, 0, 0), (0, 1, 0), (0, 0, 1))
        )
        net = add_vectors(forces)
        self.assertTrue(all(value > 0 for value in net))

    def test_offset_force_produces_torque_without_antigravity(self):
        torque = optical_torque((0.0, 1.0, 0.0), (1.0, 0.0, 0.0))
        self.assertEqual(torque, (0.0, 0.0, -1.0))

    def test_gyro_anti_and_anti_anti_preserve_identity_and_algebra(self):
        vector = (1.0, -2.0, 3.0)
        self.assertEqual(invert_gyro(vector, 0), vector)
        self.assertEqual(invert_gyro(vector, 1), (-1.0, 2.0, -3.0))
        self.assertEqual(invert_gyro(vector, 2), vector)
        self.assertEqual(tuple(gyro_family(i) for i in range(3)), GYRO_FAMILIES)

    def test_three_outer_slots_balance_on_the_spherical_shelf(self):
        points = spherical_shelf(2.0)
        self.assertEqual(len(points), 3)
        for point in points:
            self.assertTrue(math.isclose(math.sqrt(sum(value * value for value in point)), 2.0))
        total = add_vectors(points)
        self.assertTrue(all(abs(value) < 1e-12 for value in total))

    def test_address_four_is_center_with_value_one(self):
        self.assertEqual(CENTER_SLOT, 4)
        self.assertEqual(CENTER_VALUE, 1)

    def test_shannon_levels_keep_outer_and_whole_populations_separate(self):
        self.assertTrue(math.isclose(shannon_entropy_bits((1 / 3, 1 / 3, 1 / 3)), math.log2(3)))
        self.assertEqual(shannon_entropy_bits((0.25, 0.25, 0.25, 0.25)), 2.0)

    def test_zero_shannon_level_is_deterministic_not_empty(self):
        self.assertEqual(shannon_entropy_bits((1.0, 0.0, 0.0)), 0.0)

    def test_oiled_light_is_an_optical_state_not_magnetization(self):
        state = oiled_light_state("LINEAR", 0.5, OpticalSurface(0.2, 0.3, 0.5), 2.0)
        self.assertEqual(len(state), 6)
        self.assertIn("POLARIZATION=LINEAR", state)

    def test_radiation_pressure_does_not_silently_become_gravity_cancellation(self):
        surface = OpticalSurface(0.0, 1.0, 0.0)
        ratio = thrust_to_weight(surface.force_newtons(1.0), 1.0)
        self.assertGreater(ratio, 0.0)
        self.assertLess(ratio, 1e-8)

    def test_unverified_domains_grant_no_force_authority(self):
        self.assertEqual(domain_status("LIGHT_SPACE"), ("MEASURED_PHYSICS_AVAILABLE", 1))
        for domain in ("NULL_SPACE", "HYPERSPACE", "QUAZI_SPACE", "QUASI_SPACE"):
            self.assertEqual(domain_status(domain), ("UNVERIFIED", 0))

    def test_render_preserves_order_and_safety_boundaries(self):
        rows = render_demo().splitlines()
        self.assertEqual([row.split("|", 1)[0] for row in rows[:5]], list(EVIDENCE_ORDER))
        self.assertIn("families=GYRO_ANTI_GYRO_ANTI_ANTI_GYRO", rows[0])
        self.assertIn("source_3i_atlas=HELD_FOR_EXACT_HF_POINTER", rows[0])
        self.assertIn("outer_slots=1_2_3", rows[0])
        self.assertIn("center_slot=4", rows[0])
        self.assertIn("center_value=1", rows[0])
        self.assertIn("object=3D_SPHERICAL_DRADIL_X3_CENTER_4", rows[1])
        self.assertIn("magnetization=0", rows[1])
        self.assertIn("antigravity=0", rows[3])
        self.assertIn("ftl=0", rows[3])
        self.assertIn("order=HBI_HBP_SHA_SH_HASH", rows[4])
        self.assertTrue(all(row.endswith("json=0") for row in rows))


if __name__ == "__main__":
    unittest.main()
