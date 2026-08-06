import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from git_event_facets import FACET_NAMES, build_git_facets, emit_facet_directory, verify_facet_directory


class GitEventFacetTests(unittest.TestCase):
    def push_fields(self):
        return {
            "repository": "JesseBrown1980/THE-RELIC-REDISCOVERY",
            "event": "push",
            "ref": "refs/heads/main",
            "base_sha": "1" * 40,
            "head_sha": "2" * 40,
            "pull_number": 0,
            "run_id": 123,
            "run_attempt": 1,
            "verification_status": "success",
            "rust_present": 0,
            "rust_gate_status": "success",
        }

    def test_emit_creates_exact_five_files_in_canonical_order(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "receipt"
            rows = emit_facet_directory(output, **self.push_fields())
            self.assertEqual(tuple(rows), FACET_NAMES)
            self.assertEqual({item.name for item in output.iterdir()}, set(FACET_NAMES))
            self.assertEqual([rows[name].split("|", 1)[0] for name in FACET_NAMES], list(FACET_NAMES))

    def test_hbp_losslessly_carries_canonical_event_payload(self):
        facets = build_git_facets(**self.push_fields())
        hbp = dict(part.split("=", 1) for part in facets["HBP"].decode().strip().split("|")[1:])
        payload = bytes.fromhex(hbp["payload_hex"])
        decoded = json.loads(payload)
        self.assertEqual(decoded["operation"], "PUSH_EVENT")
        self.assertEqual(decoded["head_sha"], "2" * 40)
        self.assertEqual(decoded["rust_present"], 0)
        self.assertEqual(decoded["rust_toolchain"], "NOT_APPLICABLE")
        self.assertEqual(decoded["rust_clippy"], "NOT_APPLICABLE")
        self.assertEqual(int(hbp["slice_len"]), len(payload))

    def test_sha_sh_and_hash_are_full_short_and_verified_aliases(self):
        facets = build_git_facets(**self.push_fields())
        parsed = {
            name: dict(part.split("=", 1) for part in facets[name].decode().strip().split("|")[1:])
            for name in ("HBP", "SHA", "SH", "HASH")
        }
        payload = bytes.fromhex(parsed["HBP"]["payload_hex"])
        digest = hashlib.sha256(payload).hexdigest()
        self.assertEqual(parsed["SHA"]["digest"], digest)
        self.assertEqual(parsed["SH"]["value"], digest[:16])
        self.assertEqual(parsed["HASH"]["value"], digest)
        self.assertEqual(parsed["HASH"]["verified"], "1")

    def test_pull_receipt_requires_and_records_pull_number(self):
        fields = self.push_fields()
        fields.update(event="pull_request", ref="refs/pull/7/merge", pull_number=7)
        facets = build_git_facets(**fields)
        hbp = dict(part.split("=", 1) for part in facets["HBP"].decode().strip().split("|")[1:])
        payload = json.loads(bytes.fromhex(hbp["payload_hex"]))
        self.assertEqual(payload["operation"], "PULL_REQUEST_EVENT")
        self.assertEqual(payload["pull_number"], 7)
        fields["pull_number"] = 0
        with self.assertRaisesRegex(ValueError, "positive pull_number"):
            build_git_facets(**fields)

    def test_verifier_rejects_a_change_to_each_facet(self):
        mutations = {
            "HBI": (b"kind=github_event_index", b"kind=changed_index"),
            "HBP": (b"kind=lossless_git_event_payload", b"kind=changed_payload"),
            "SHA": (b"algorithm=SHA-256", b"algorithm=SHA-512"),
            "SH": (b"bytes=8", b"bytes=9"),
            "HASH": (b"verified=1", b"verified=0"),
        }
        for name, (before, after) in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / "receipt"
                emit_facet_directory(output, **self.push_fields())
                path = output / name
                payload = path.read_bytes()
                self.assertIn(before, payload)
                path.write_bytes(payload.replace(before, after, 1))
                with self.assertRaises(ValueError):
                    verify_facet_directory(output)

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "receipt"
            emit_facet_directory(output, **self.push_fields())
            hbi = (output / "HBI").read_bytes()
            old_id = hbi.split(b"|id=", 1)[1].split(b"|", 1)[0]
            new_id = b"RELICGIT-0000000000000000"
            for name in FACET_NAMES:
                path = output / name
                path.write_bytes(path.read_bytes().replace(old_id, new_id, 1))
            with self.assertRaises(ValueError):
                verify_facet_directory(output)


if __name__ == "__main__":
    unittest.main()
