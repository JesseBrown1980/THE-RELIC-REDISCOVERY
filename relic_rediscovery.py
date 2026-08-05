"""Reference model for the Relic Rediscovery expanding ternary waves."""

from __future__ import annotations

import argparse
from dataclasses import dataclass

FREE_CENTER = "C"


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
    outward_addresses: int
    wave_count_to_next: int
    multiplier_to_next: int
    next_anchor: int


def structure(level: int) -> Structure:
    wave = waves(level)
    return Structure(
        level=level,
        center=FREE_CENTER,
        outward_addresses=anchor(level),
        wave_count_to_next=len(wave),
        multiplier_to_next=multiplier(level),
        next_anchor=wave[-1],
    )


def render(levels: int) -> str:
    if levels <= 0:
        raise ValueError("levels must be positive")
    rows = [
        "level | center | outward | waves-to-next | multiplier | next-anchor",
        "------|--------|---------|---------------|------------|------------",
    ]
    for level in range(levels):
        item = structure(level)
        rows.append(
            f"{item.level} | {item.center} | {item.outward_addresses} | "
            f"{item.wave_count_to_next} | {item.multiplier_to_next} | {item.next_anchor}"
        )
        rows.append("waves | " + " -> ".join(map(str, waves(level))))
    return "\n".join(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--levels", type=int, default=5)
    args = parser.parse_args()
    print(render(args.levels))


if __name__ == "__main__":
    main()
