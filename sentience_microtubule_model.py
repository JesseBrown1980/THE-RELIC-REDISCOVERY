"""Offline falsification model for the Relic microtubule/claustrum hypothesis.

All ports and subnets in this module are logical addresses.  It opens no socket,
performs no MRI acquisition, and makes no claim of consciousness or quantum biology.
"""

from __future__ import annotations

import argparse
import hashlib
import math
import random
from dataclasses import dataclass
from typing import Sequence

EVIDENCE_ORDER = ("HBI", "HBP", "SHA", "SH", "HASH")
SENTIENCE_LABEL = "SEN_T_I_E_N_C_E"
CENTER_ANATOMICAL_HYPOTHESIS = "CLAUSTRUM"
FRANCIS_REFERENCE = "FRANCIS_CRICK"
CENTER_VALUE = 1
LOCAL_ZERO = 0
NEGATIVE_START = "S"
POSITIVE_ENDPOINT = "Z"
Z_SELF_CONNECTED = 1
NEXT_PATH = "S_NEGATIVE_TO_Z_POSITIVE_TO_END_0_TO_NEXT_IS"
PHYSICAL_STATUS = "UNVERIFIED"


def landing_offset(level: int) -> int:
    """Ternary exponent offset from the first Relic landing."""
    if level < 0:
        raise ValueError("level must be nonnegative")
    return level * (level + 3) // 2


def predicted_landing_frequencies(base_hz: float, levels: int) -> tuple[float, ...]:
    """Dimensionless Relic scaling applied to a preregistered base frequency."""
    if not math.isfinite(base_hz) or base_hz <= 0:
        raise ValueError("base_hz must be finite and positive")
    if levels <= 0:
        raise ValueError("levels must be positive")
    return tuple(base_hz * 3.0 ** landing_offset(level) for level in range(levels))


def landing_residuals(
    frequencies_hz: Sequence[float], base_hz: float, max_level: int
) -> tuple[float, ...]:
    """Distance in log-base-three space to the nearest predicted landing."""
    if max_level < 0:
        raise ValueError("max_level must be nonnegative")
    if not math.isfinite(base_hz) or base_hz <= 0:
        raise ValueError("base_hz must be finite and positive")
    offsets = tuple(landing_offset(level) for level in range(max_level + 1))
    residuals = []
    for frequency in frequencies_hz:
        if not math.isfinite(frequency) or frequency <= 0:
            raise ValueError("frequencies must be finite and positive")
        coordinate = math.log(frequency / base_hz, 3.0)
        residuals.append(min(abs(coordinate - offset) for offset in offsets))
    return tuple(residuals)


def recurrence_score(
    frequencies_hz: Sequence[float], base_hz: float, max_level: int, tolerance: float
) -> int:
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and nonnegative")
    return sum(
        residual <= tolerance
        for residual in landing_residuals(frequencies_hz, base_hz, max_level)
    )


def permutation_p_value(
    frequencies_hz: Sequence[float],
    base_hz: float,
    max_level: int,
    tolerance: float,
    trials: int = 999,
    seed: int = 3174,
) -> float:
    """Log-uniform null test; intended for preregistered, held-out spectra."""
    if len(frequencies_hz) < 2:
        raise ValueError("at least two frequencies are required")
    if trials <= 0:
        raise ValueError("trials must be positive")
    observed = recurrence_score(frequencies_hz, base_hz, max_level, tolerance)
    lower = min(frequencies_hz)
    upper = max(frequencies_hz)
    if lower == upper:
        raise ValueError("frequency range must be nonzero")
    random_source = random.Random(seed)
    log_lower = math.log(lower)
    log_upper = math.log(upper)
    at_least_observed = 0
    for _ in range(trials):
        null = tuple(
            math.exp(random_source.uniform(log_lower, log_upper))
            for _ in frequencies_hz
        )
        if recurrence_score(null, base_hz, max_level, tolerance) >= observed:
            at_least_observed += 1
    return (at_least_observed + 1) / (trials + 1)


def fuzzy_membership(
    concentrations: Sequence[float],
    centroids: Sequence[Sequence[float]],
    sigma: float,
) -> tuple[float, ...]:
    """Stable radial memberships for the symbolic foggy concentration matrix."""
    if not centroids:
        raise ValueError("at least one centroid is required")
    if not math.isfinite(sigma) or sigma <= 0:
        raise ValueError("sigma must be finite and positive")
    vector = tuple(float(value) for value in concentrations)
    if not vector or any(not math.isfinite(value) or value < 0 for value in vector):
        raise ValueError("concentrations must be finite and nonnegative")
    prepared = tuple(tuple(float(value) for value in centroid) for centroid in centroids)
    if any(len(centroid) != len(vector) for centroid in prepared):
        raise ValueError("centroid dimensions must match concentrations")
    if any(not math.isfinite(value) or value < 0 for centroid in prepared for value in centroid):
        raise ValueError("centroids must be finite and nonnegative")
    scores = tuple(
        -sum((value - center) ** 2 for value, center in zip(vector, centroid))
        / (2.0 * sigma**2)
        for centroid in prepared
    )
    maximum = max(scores)
    weights = tuple(math.exp(score - maximum) for score in scores)
    total = sum(weights)
    return tuple(weight / total for weight in weights)


def assign_foggy_subnet(
    memberships: Sequence[float], threshold: float = 0.6, margin: float = 0.1
) -> str:
    """Admit a subnet only when both confidence and winner margin pass."""
    values = tuple(float(value) for value in memberships)
    if not values or any(not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("memberships must be finite and nonnegative")
    if abs(sum(values) - 1.0) > 1e-9:
        raise ValueError("memberships must sum to one")
    if not 0 <= threshold <= 1 or not 0 <= margin <= 1:
        raise ValueError("threshold and margin must be within zero and one")
    ordered = sorted(enumerate(values), key=lambda item: (-item[1], item[0]))
    winner, winner_value = ordered[0]
    runner_up = ordered[1][1] if len(ordered) > 1 else 0.0
    if winner_value < threshold or winner_value - runner_up < margin:
        return "HELD_FOR_REVIEW"
    return f"FOGGY_SUBNET_{winner}"


def normalized_weighted_degree(
    adjacency: Sequence[Sequence[float]], node_index: int
) -> float:
    """Normalized graph centrality used to test, not assume, the claustrum analogy."""
    matrix = tuple(tuple(float(value) for value in row) for row in adjacency)
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("adjacency must be a nonempty square matrix")
    if not 0 <= node_index < size:
        raise ValueError("node_index is outside the matrix")
    if any(not math.isfinite(value) or value < 0 for row in matrix for value in row):
        raise ValueError("adjacency weights must be finite and nonnegative")
    degrees = tuple(sum(row) for row in matrix)
    maximum = max(degrees)
    return 0.0 if maximum == 0 else degrees[node_index] / maximum


def logical_port_address(tubule_id: str, concentrations: Sequence[float]) -> str:
    """Content address only; this is never an operating-system or HTTP port."""
    if not tubule_id or any(character in tubule_id for character in "|\r\n"):
        raise ValueError("tubule_id is empty or contains a tuple delimiter")
    vector = tuple(float(value) for value in concentrations)
    if not vector or any(not math.isfinite(value) or value < 0 for value in vector):
        raise ValueError("concentrations must be finite and nonnegative")
    material = f"{tubule_id}|" + ",".join(format(value, ".17g") for value in vector)
    return "BIO0-" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class TubuleFixture:
    tubule_id: str
    concentrations: tuple[float, ...]

    def rows(self, centroids: Sequence[Sequence[float]], sigma: float) -> tuple[str, ...]:
        memberships = fuzzy_membership(self.concentrations, centroids, sigma)
        subnet = assign_foggy_subnet(memberships)
        address = logical_port_address(self.tubule_id, self.concentrations)
        membership_text = "_".join(format(value, ".12g") for value in memberships)
        basis = (
            f"id={self.tubule_id}|local_zero={LOCAL_ZERO}|logical_address={address}|"
            f"memberships={membership_text}|subnet={subnet}"
        )
        sha = hashlib.sha256(basis.encode("utf-8")).hexdigest()
        final_hash = hashlib.sha256((sha + "|" + "_".join(EVIDENCE_ORDER)).encode("ascii")).hexdigest()
        return (
            f"HBI|{basis}|http=0|socket_open=0|network=0|json=0",
            f"HBP|center={CENTER_ANATOMICAL_HYPOTHESIS}|center_value={CENTER_VALUE}|"
            f"negative={NEGATIVE_START}|positive_endpoint={POSITIVE_ENDPOINT}|"
            f"z_self_connected={Z_SELF_CONNECTED}|logical_instant=1|"
            f"physical_instant=UNVERIFIED|path={NEXT_PATH}|json=0",
            f"SHA|value={sha}|byte_commitment=1|json=0",
            f"SH|sentience_label={SENTIENCE_LABEL}|evidence=OPERATOR_CANON_HYPOTHESIS|"
            f"physical_status={PHYSICAL_STATUS}|subjective_experience=UNVERIFIED|json=0",
            f"HASH|value={final_hash}|order=HBI_HBP_SHA_SH_HASH|"
            f"transport_chain_inferred=0|json=0",
        )


def render_demo() -> str:
    fixture = TubuleFixture("SYNTHETIC_TUBULE_1", (0.8, 0.1, 0.1))
    rows = (
        "SENTIENCEHYPOTHESIS|name=SEN_T_I_E_N_C_E|science_emergence=TEST_MEASURE|"
        "center=CLAUSTRUM|center_value=1|francis_reference=FRANCIS_CRICK|"
        "microtubule_quantum=UNVERIFIED|claustrum_free_center=UNVERIFIED|json=0",
        *fixture.rows(((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)), 0.25),
        "BOUNDARY|human_intervention=0|mri_acquisition=0|http=0|socket_open=0|"
        "network=0|drug_instruction=0|physical_claim=0|json=0",
    )
    return "\n".join(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(render_demo())


if __name__ == "__main__":
    main()
