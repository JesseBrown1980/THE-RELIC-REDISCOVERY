"""Offline TRI_D_O_A_E_SCOPE radiation-pressure and gyro model.

This module models ordinary light momentum and three-axis angular momentum.  It
does not model antigravity, faster-than-light motion, or unverified space domains.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Sequence

LIGHT_SPEED_M_S = 299_792_458.0
STANDARD_GRAVITY_M_S2 = 9.80665
EVIDENCE_ORDER = ("HBI", "HBP", "SHA", "SH", "HASH")
GYRO_FAMILIES = ("GYRO", "ANTI_GYRO", "ANTI_ANTI_GYRO")
AXES = ("X", "Y", "Z")
UNVERIFIED_DOMAINS = ("NULL_SPACE", "HYPERSPACE", "QUAZI_SPACE", "QUASI_SPACE")
CENTER_SLOT = 4
CENTER_VALUE = 1
OUTER_SLOTS = (1, 2, 3)
OILED_LIGHT_COORDINATES = (
    "POLARIZATION", "PHASE", "ABSORPTION", "REFLECTION", "TRANSMISSION", "SPECTRAL_SHIFT"
)


def _finite_nonnegative(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return result


def _vector3(vector: Sequence[float], name: str) -> tuple[float, float, float]:
    result = tuple(float(value) for value in vector)
    if len(result) != 3 or any(not math.isfinite(value) for value in result):
        raise ValueError(f"{name} must be a finite three-vector")
    return result  # type: ignore[return-value]


def unit_vector(vector: Sequence[float]) -> tuple[float, float, float]:
    prepared = _vector3(vector, "vector")
    magnitude = math.sqrt(sum(value * value for value in prepared))
    if magnitude == 0:
        raise ValueError("vector magnitude must be nonzero")
    return tuple(value / magnitude for value in prepared)  # type: ignore[return-value]


def cross(left: Sequence[float], right: Sequence[float]) -> tuple[float, float, float]:
    a = _vector3(left, "left")
    b = _vector3(right, "right")
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


@dataclass(frozen=True)
class OpticalSurface:
    absorptance: float
    reflectance: float
    transmittance: float

    def __post_init__(self) -> None:
        values = tuple(
            _finite_nonnegative(value, name)
            for value, name in (
                (self.absorptance, "absorptance"),
                (self.reflectance, "reflectance"),
                (self.transmittance, "transmittance"),
            )
        )
        if any(value > 1 for value in values) or abs(sum(values) - 1.0) > 1e-12:
            raise ValueError("optical coefficients must be within [0,1] and sum to one")

    def force_newtons(self, incident_power_watts: float) -> float:
        """Normal-incidence force for forward transmission without beam redirection."""
        power = _finite_nonnegative(incident_power_watts, "incident_power_watts")
        return power * (self.absorptance + 2.0 * self.reflectance) / LIGHT_SPEED_M_S

    def absorbed_power_watts(self, incident_power_watts: float) -> float:
        return _finite_nonnegative(incident_power_watts, "incident_power_watts") * self.absorptance


def circular_beam_intensity(power_watts: float, radius_m: float) -> float:
    power = _finite_nonnegative(power_watts, "power_watts")
    radius = float(radius_m)
    if not math.isfinite(radius) or radius <= 0:
        raise ValueError("radius_m must be finite and positive")
    return power / (math.pi * radius * radius)


def coating_retention(
    initial_fraction: float, rate_per_joule_m2: float, intensity_w_m2: float, seconds: float
) -> float:
    """Phenomenological photobleaching retention, not a material qualification model."""
    initial = float(initial_fraction)
    if not math.isfinite(initial) or not 0 <= initial <= 1:
        raise ValueError("initial_fraction must be within zero and one")
    rate = _finite_nonnegative(rate_per_joule_m2, "rate_per_joule_m2")
    intensity = _finite_nonnegative(intensity_w_m2, "intensity_w_m2")
    duration = _finite_nonnegative(seconds, "seconds")
    return initial * math.exp(-rate * intensity * duration)


def radiation_force_vector(
    surface: OpticalSurface, power_watts: float, propagation: Sequence[float]
) -> tuple[float, float, float]:
    direction = unit_vector(propagation)
    magnitude = surface.force_newtons(power_watts)
    return tuple(magnitude * value for value in direction)  # type: ignore[return-value]


def optical_torque(
    lever_arm_m: Sequence[float], force_newtons: Sequence[float]
) -> tuple[float, float, float]:
    return cross(lever_arm_m, force_newtons)


def add_vectors(vectors: Sequence[Sequence[float]]) -> tuple[float, float, float]:
    prepared = tuple(_vector3(vector, "vector") for vector in vectors)
    return tuple(sum(vector[index] for vector in prepared) for index in range(3))  # type: ignore[return-value]


def spherical_shelf(radius: float) -> tuple[tuple[float, float, float], ...]:
    """Three equally spaced outer slots; address four is the separate free center."""
    prepared_radius = float(radius)
    if not math.isfinite(prepared_radius) or prepared_radius <= 0:
        raise ValueError("radius must be finite and positive")
    return tuple(
        (
            prepared_radius * math.cos(2.0 * math.pi * index / 3.0),
            prepared_radius * math.sin(2.0 * math.pi * index / 3.0),
            0.0,
        )
        for index in range(3)
    )


def shannon_entropy_bits(probabilities: Sequence[float]) -> float:
    values = tuple(float(value) for value in probabilities)
    if not values or any(not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("probabilities must be finite and nonnegative")
    if abs(sum(values) - 1.0) > 1e-12:
        raise ValueError("probabilities must sum to one")
    return -sum(value * math.log2(value) for value in values if value > 0)


def oiled_light_state(
    polarization: str,
    phase_radians: float,
    surface: OpticalSurface,
    spectral_shift_hz: float = 0.0,
) -> tuple[str, ...]:
    """Optical-state ledger; no material magnetization is inferred."""
    if not polarization or any(character in polarization for character in "|\r\n"):
        raise ValueError("polarization is empty or contains a tuple delimiter")
    phase = float(phase_radians)
    shift = float(spectral_shift_hz)
    if not math.isfinite(phase) or not math.isfinite(shift):
        raise ValueError("phase and spectral shift must be finite")
    return (
        f"POLARIZATION={polarization}",
        f"PHASE={phase:.17g}",
        f"ABSORPTION={surface.absorptance:.17g}",
        f"REFLECTION={surface.reflectance:.17g}",
        f"TRANSMISSION={surface.transmittance:.17g}",
        f"SPECTRAL_SHIFT={shift:.17g}",
    )


def invert_gyro(
    angular_momentum: Sequence[float], inversions: int
) -> tuple[float, float, float]:
    vector = _vector3(angular_momentum, "angular_momentum")
    if inversions not in (0, 1, 2):
        raise ValueError("inversions must be zero, one, or two")
    sign = -1.0 if inversions == 1 else 1.0
    return tuple(sign * value for value in vector)  # type: ignore[return-value]


def gyro_family(inversions: int) -> str:
    if inversions not in (0, 1, 2):
        raise ValueError("inversions must be zero, one, or two")
    return GYRO_FAMILIES[inversions]


def thrust_to_weight(force_newtons: float, mass_kg: float) -> float:
    force = _finite_nonnegative(force_newtons, "force_newtons")
    mass = float(mass_kg)
    if not math.isfinite(mass) or mass <= 0:
        raise ValueError("mass_kg must be finite and positive")
    return force / (mass * STANDARD_GRAVITY_M_S2)


def domain_status(domain: str) -> tuple[str, int]:
    if domain == "LIGHT_SPACE":
        return ("MEASURED_PHYSICS_AVAILABLE", 1)
    if domain in UNVERIFIED_DOMAINS:
        return ("UNVERIFIED", 0)
    raise ValueError("unknown domain")


def render_demo() -> str:
    surface = OpticalSurface(absorptance=0.0, reflectance=1.0, transmittance=0.0)
    forces = tuple(
        radiation_force_vector(surface, 1.0, direction)
        for direction in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    )
    net = add_vectors(forces)
    shelf = spherical_shelf(1.0)
    outer_entropy = shannon_entropy_bits((1.0 / 3.0,) * 3)
    whole_entropy = shannon_entropy_bits((0.25,) * 4)
    oiled = oiled_light_state("LINEAR_SYNTHETIC", 0.0, surface)
    basis = (
        f"families={'_'.join(GYRO_FAMILIES)}|axes={'_'.join(AXES)}|"
        f"outer_slots={'_'.join(map(str, OUTER_SLOTS))}|center_slot={CENTER_SLOT}|"
        f"center_value={CENTER_VALUE}|shelf_points={len(shelf)}|"
        f"outer_shannon_bits={outer_entropy:.17g}|whole_shannon_bits={whole_entropy:.17g}|"
        f"force_x={net[0]:.17g}|force_y={net[1]:.17g}|force_z={net[2]:.17g}"
    )
    sha = hashlib.sha256(basis.encode("utf-8")).hexdigest()
    final_hash = hashlib.sha256((sha + "|" + "_".join(EVIDENCE_ORDER)).encode("ascii")).hexdigest()
    rows = (
        f"HBI|model=TRI_D_O_A_E_SCOPE|{basis}|source_3i_atlas=HELD_FOR_EXACT_HF_POINTER|json=0",
        "HBP|force=radiation_pressure|formula=P_over_c_times_A_plus_2R|"
        f"object=3D_SPHERICAL_DRADIL_X3_CENTER_4|oiled={'_'.join(oiled)}|"
        "magnetization=0|translation=MEASURED_PHYSICS|rotation=MEASURED_PHYSICS|json=0",
        f"SHA|value={sha}|byte_commitment=1|json=0",
        "SH|antigravity=0|ftl=0|null_space=UNVERIFIED|hyperspace=UNVERIFIED|"
        "quazi_space=UNVERIFIED|quasi_space=UNVERIFIED|json=0",
        f"HASH|value={final_hash}|order=HBI_HBP_SHA_SH_HASH|"
        "transport_chain_inferred=0|json=0",
        "BOUNDARY|simulation_only=1|laser_build_instruction=0|human_exposure=0|"
        "device_claim=0|json=0",
    )
    return "\n".join(rows)


if __name__ == "__main__":
    print(render_demo())
