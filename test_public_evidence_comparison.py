import unittest

from public_evidence_comparison import EVIDENCE_ORDER, evaluate, load_fixture, render


class PublicEvidenceComparisonTests(unittest.TestCase):
    def test_fixture_preserves_authoritative_sources(self):
        records = {record["kind"]: record for record in load_fixture()["records"]}
        self.assertEqual(records["MEASURED_ACCELERATION"]["source"], "https://geodesy.noaa.gov/GRAV-D/icag.shtml")
        self.assertEqual(records["MICROTUBULE_STRUCTURE"]["source"], "https://www.rcsb.org/structure/5JCO")

    def test_public_acceleration_favors_standard_over_zero(self):
        result = evaluate()
        comparison = result["acceleration"]
        self.assertEqual(comparison["winner"], "STANDARD_EXTERNAL_ACCELERATION")
        self.assertLess(comparison["standard_error_m_s2"], comparison["null_gpu_error_m_s2"])

    def test_microtubule_observation_does_not_expand_claim_scope(self):
        result = evaluate()
        self.assertTrue(result["microtubule_observed"])
        self.assertFalse(result["microtubule_proves_null_space"])
        self.assertFalse(result["microtubule_proves_consciousness"])

    def test_render_preserves_evidence_order_and_json_zero(self):
        rows = render().splitlines()
        self.assertEqual([row.split("|", 1)[0] for row in rows[:5]], list(EVIDENCE_ORDER))
        self.assertIn("winner=STANDARD_EXTERNAL_ACCELERATION", rows[1])
        self.assertIn("proves_null_space=0", rows[3])
        self.assertTrue(all(row.endswith("json=0") for row in rows))


if __name__ == "__main__":
    unittest.main()
