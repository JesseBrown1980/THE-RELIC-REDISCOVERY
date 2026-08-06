"""Offline comparison of scoped Relic hypotheses with attributed public observations."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

EVIDENCE_ORDER = ("HBI", "HBP", "SHA", "SH", "HASH")
FIXTURE = Path(__file__).with_name("public_evidence_fixture.json")
STANDARD_GRAVITY_M_S2 = 9.80665


def load_fixture(path: Path = FIXTURE) -> dict[str, Any]:
    raw = path.read_bytes()
    data = json.loads(raw)
    if data.get("schema") != "RELIC_PUBLIC_EVIDENCE_FIXTURE_V1":
        raise ValueError("unexpected fixture schema")
    if len(data.get("records", ())) != 2:
        raise ValueError("expected exactly two scoped public records")
    return data


def compare_acceleration(observed_m_s2: float) -> dict[str, float | str]:
    observed = float(observed_m_s2)
    if not math.isfinite(observed) or observed < 0:
        raise ValueError("observed acceleration must be finite and nonnegative")
    standard_error = abs(observed - STANDARD_GRAVITY_M_S2)
    null_error = abs(observed)
    return {
        "observed_m_s2": observed,
        "standard_error_m_s2": standard_error,
        "null_gpu_error_m_s2": null_error,
        "winner": "STANDARD_EXTERNAL_ACCELERATION" if standard_error < null_error else "NULL_SPACE_GPU_ZERO",
    }


def evaluate(path: Path = FIXTURE) -> dict[str, Any]:
    data = load_fixture(path)
    by_kind = {record["kind"]: record for record in data["records"]}
    acceleration = compare_acceleration(by_kind["MEASURED_ACCELERATION"]["value_m_s2"])
    microtubule = by_kind["MICROTUBULE_STRUCTURE"]
    return {
        "acceleration": acceleration,
        "microtubule_observed": microtubule["method"] == "ELECTRON_MICROSCOPY",
        "microtubule_resolution_angstrom": microtubule["resolution_angstrom"],
        "microtubule_proves_null_space": False,
        "microtubule_proves_consciousness": False,
    }


def render(path: Path = FIXTURE) -> str:
    raw = path.read_bytes()
    fixture_sha = hashlib.sha256(raw).hexdigest()
    result = evaluate(path)
    acceleration = result["acceleration"]
    basis = (
        f"fixture_sha256={fixture_sha}|records=2|"
        f"observed_m_s2={acceleration['observed_m_s2']:.8f}|"
        f"standard_error_m_s2={acceleration['standard_error_m_s2']:.8f}|"
        f"null_gpu_error_m_s2={acceleration['null_gpu_error_m_s2']:.8f}"
    )
    sha = hashlib.sha256(basis.encode("ascii")).hexdigest()
    final_hash = hashlib.sha256((sha + "|" + "_".join(EVIDENCE_ORDER)).encode("ascii")).hexdigest()
    rows = (
        f"HBI|dataset=PUBLIC_SCOPED_PAIR|{basis}|json=0",
        "HBP|hypotheses=STANDARD_EXTERNAL_ACCELERATION_VS_NULL_SPACE_GPU_ZERO|"
        f"winner={acceleration['winner']}|operator_alias=LIGHT_BALANCING|json=0",
        f"SHA|value={sha}|byte_commitment=1|json=0",
        "SH|microtubule_observed=1|method=ELECTRON_MICROSCOPY|"
        f"resolution_angstrom={result['microtubule_resolution_angstrom']:.1f}|"
        "proves_null_space=0|proves_consciousness=0|json=0",
        f"HASH|value={final_hash}|order=HBI_HBP_SHA_SH_HASH|transport_chain_inferred=0|json=0",
        "RESULT|simulation_distinct=1|public_observation_compared=1|"
        "physical_null_space_verdict=NOT_SUPPORTED_BY_THIS_DATA|json=0",
    )
    return "\n".join(rows)


if __name__ == "__main__":
    print(render())
