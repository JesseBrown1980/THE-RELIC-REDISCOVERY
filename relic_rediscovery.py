"""Reference model for the Relic Rediscovery expanding ternary waves."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from fractions import Fraction

FREE_CENTER = "C"


CENTER_VALUE = 1
Z_LEVELS = (Fraction(-1, 3), Fraction(0, 1), Fraction(1, 3))
END_ZERO = 0
ROTATIONAL_CLOSURE = 'X_TO_Y_TO_Z_TO_END_0_TO_NEXT_IS'
CENTER_SIGN = ('HBI', 'HBP', 'SHA', 'SH', 'HASH')
CURRENT_UTTERANCE_ORDER = CENTER_SIGN


def center_at_z(_z: object) -> int:
    '''The invariant center remains one at every Z coordinate.'''
    return CENTER_VALUE


def _require_nonnegative(value: int, name: str) -> None:
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")


def exponent(level: int) -> int:
    """Exponent of three at a completed structural landing."""
    _require_nonnegative(level, "level")
    return 3 + level * (level + 3) // 2


def anchor(level: int) -> int:
    """Outward address count at a completed structural landing."""
    return 3 ** exponent(level)


def multiplier(level: int) -> int:
    """Multiplier from this landing to the next landing."""
    _require_nonnegative(level, "level")
    return 3 ** (level + 2)


def waves(level: int) -> tuple[int, ...]:
    """All x3 waves after this landing, including the next landing."""
    start = anchor(level)
    return tuple(start * 3**step for step in range(1, level + 3))


@dataclass(frozen=True)
class Structure:
    level: int
    center: str
    center_value: int
    outward_addresses: int
    wave_count_to_next: int
    multiplier_to_next: int
    next_anchor: int


def structure(level: int) -> Structure:
    wave = waves(level)
    return Structure(
        level=level,
        center=FREE_CENTER,
        center_value=CENTER_VALUE,
        outward_addresses=anchor(level),
        wave_count_to_next=len(wave),
        multiplier_to_next=multiplier(level),
        next_anchor=wave[-1],
    )


def render(levels: int) -> str:
    if levels <= 0:
        raise ValueError("levels must be positive")
    rows = [
        "level | center | value | outward | waves-to-next | multiplier | next-anchor",
        "------|--------|-------|---------|---------------|------------|------------",
    ]
    for level in range(levels):
        item = structure(level)
        rows.append(
            f"{item.level} | {item.center} | {item.center_value} | {item.outward_addresses} | "
            f"{item.wave_count_to_next} | {item.multiplier_to_next} | {item.next_anchor}"
        )
        rows.append("waves | " + " -> ".join(map(str, waves(level))))
    rows.append(
        "closure | X -> Y -> Z -> END_0 -> NEXT_IS | "
        "bidirectional=0 | reverse=0 | round_trip=0 | exchange=0"
    )
    rows.append("center-sign | " + " -> ".join(CURRENT_UTTERANCE_ORDER))
    return "\n".join(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--levels", type=int, default=5)
    args = parser.parse_args()
    print(render(args.levels))


if __name__ == "__main__":
    main()
