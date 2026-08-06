"""Create and verify five-file HBI/HBP/SHA/SH/HASH GitHub event receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable


FACET_NAMES = ("HBI", "HBP", "SHA", "SH", "HASH")
SCHEMA = "RELIC_GIT_EVENT_V1"
_EVENT_OPERATIONS = {
    "push": "PUSH_EVENT",
    "pull_request": "PULL_REQUEST_EVENT",
    "workflow_dispatch": "MANUAL_EVENT",
}
_VERIFICATION_STATES = {"SUCCESS", "FAILURE", "CANCELLED", "SKIPPED"}
_GIT_OBJECT_RE = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")


def _atom(name: str, value: object, *, maximum: int = 512) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{name} must not be empty")
    if len(text) > maximum:
        raise ValueError(f"{name} is too long")
    if "|" in text or any(ord(character) < 32 for character in text):
        raise ValueError(f"{name} contains a tuple delimiter or control character")
    return text


def _git_object(name: str, value: object) -> str:
    text = _atom(name, value).lower()
    if not _GIT_OBJECT_RE.fullmatch(text):
        raise ValueError(f"{name} must be a 40- or 64-character hexadecimal Git object ID")
    return text


def _integer(name: str, value: object, *, allow_zero: bool = False) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be an integer") from error
    minimum = 0 if allow_zero else 1
    if number < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return number


def _line(label: str, fields: Iterable[tuple[str, object]]) -> bytes:
    parts = [label]
    for key, value in fields:
        maximum = 8192 if key == "payload_hex" else 512
        parts.append(f"{_atom('field name', key)}={_atom(key, value, maximum=maximum)}")
    return ("|".join(parts) + "\n").encode("utf-8")


def _digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_payload(fields: dict[str, object]) -> bytes:
    return json.dumps(
        fields,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def build_git_facets(
    *,
    repository: str,
    event: str,
    ref: str,
    base_sha: str,
    head_sha: str,
    pull_number: int,
    run_id: int,
    run_attempt: int,
    verification_status: str,
    rust_present: int,
    rust_gate_status: str,
) -> dict[str, bytes]:
    """Build the five canonical facet files without touching the filesystem."""

    repository = _atom("repository", repository)
    if repository.count("/") != 1:
        raise ValueError("repository must use owner/name form")
    event = _atom("event", event).lower()
    if event not in _EVENT_OPERATIONS:
        raise ValueError(f"unsupported event: {event}")
    operation = _EVENT_OPERATIONS[event]
    ref = _atom("ref", ref)
    base_sha = _git_object("base_sha", base_sha)
    head_sha = _git_object("head_sha", head_sha)
    pull_number = _integer("pull_number", pull_number, allow_zero=True)
    run_id = _integer("run_id", run_id)
    run_attempt = _integer("run_attempt", run_attempt)
    verification_status = _atom("verification_status", verification_status).upper()
    if verification_status not in _VERIFICATION_STATES:
        raise ValueError(f"unsupported verification status: {verification_status}")
    rust_present = _integer("rust_present", rust_present, allow_zero=True)
    if rust_present not in (0, 1):
        raise ValueError("rust_present must be zero or one")
    rust_gate_status = _atom("rust_gate_status", rust_gate_status).upper()
    if rust_gate_status not in _VERIFICATION_STATES:
        raise ValueError(f"unsupported Rust gate status: {rust_gate_status}")
    if event == "pull_request" and pull_number == 0:
        raise ValueError("pull_request events require a positive pull_number")
    if event != "pull_request" and pull_number != 0:
        raise ValueError("only pull_request events may carry a pull_number")

    if rust_present:
        rust_toolchain = "1.81.0" if rust_gate_status == "SUCCESS" else "HOLD"
        rust_numeric_domain = "INTEGER_ONLY_PASS" if rust_gate_status == "SUCCESS" else "HOLD"
        rust_clippy = "PASS" if rust_gate_status == "SUCCESS" else "HOLD"
    else:
        rust_toolchain = "NOT_APPLICABLE"
        rust_numeric_domain = "NOT_APPLICABLE"
        rust_clippy = "NOT_APPLICABLE"

    payload_fields: dict[str, object] = {
        "base_sha": base_sha,
        "event": event,
        "evidence_source": "GITHUB_EVENT_CONTEXT",
        "head_sha": head_sha,
        "operation": operation,
        "pull_number": pull_number,
        "ref": ref,
        "repository": repository,
        "run_attempt": run_attempt,
        "run_id": run_id,
        "rust_clippy": rust_clippy,
        "rust_gate_status": rust_gate_status,
        "rust_numeric_domain": rust_numeric_domain,
        "rust_present": rust_present,
        "rust_toolchain": rust_toolchain,
        "schema": SCHEMA,
        "verification_status": verification_status,
    }
    payload = _canonical_payload(payload_fields)
    digest = _digest(payload)
    short = digest[:16]
    envelope_id = f"RELICGIT-{short}"

    hbi = _line(
        "HBI",
        (
            ("id", envelope_id),
            ("kind", "github_event_index"),
            ("repository", repository),
            ("event", event),
            ("ref", ref),
            ("head_sha", head_sha),
            ("run_id", run_id),
            ("transport_chain_inferred", 0),
            ("json", 0),
        ),
    )
    hbp = _line(
        "HBP",
        (
            ("id", envelope_id),
            ("kind", "lossless_git_event_payload"),
            ("slice_len", len(payload)),
            ("payload_hex", payload.hex()),
            ("transport_chain_inferred", 0),
            ("json", 0),
        ),
    )
    sha = _line(
        "SHA",
        (
            ("id", envelope_id),
            ("algorithm", "SHA-256"),
            ("digest", digest),
            ("transport_chain_inferred", 0),
            ("json", 0),
        ),
    )
    sh = _line(
        "SH",
        (
            ("id", envelope_id),
            ("kind", "host8_short_coordinate"),
            ("bytes", 8),
            ("value", short),
            ("transport_chain_inferred", 0),
            ("json", 0),
        ),
    )
    final_hash = _line(
        "HASH",
        (
            ("id", envelope_id),
            ("algorithm", "SHA-256"),
            ("value", digest),
            ("verified", 1),
            ("order", "HBI_HBP_SHA_SH_HASH"),
            ("closure", "END"),
            ("transport_chain_inferred", 0),
            ("json", 0),
        ),
    )
    return {"HBI": hbi, "HBP": hbp, "SHA": sha, "SH": sh, "HASH": final_hash}


def _parse_line(expected_label: str, payload: bytes) -> dict[str, str]:
    if not payload.endswith(b"\n") or payload.count(b"\n") != 1 or b"\r" in payload:
        raise ValueError(f"{expected_label} must use one canonical LF-terminated line")
    text = payload.decode("utf-8")[:-1]
    parts = text.split("|")
    if not parts or parts[0] != expected_label:
        raise ValueError(f"expected {expected_label} record")
    fields: dict[str, str] = {}
    for part in parts[1:]:
        key, separator, value = part.partition("=")
        if not separator or not key or not value or key in fields:
            raise ValueError(f"malformed {expected_label} field")
        fields[key] = value
    return fields


def verify_facet_directory(directory: Path) -> dict[str, str]:
    """Verify exact file membership, payload bytes, ordering witness, and digest aliases."""

    directory = Path(directory)
    entries = tuple(directory.iterdir())
    observed_names = {entry.name for entry in entries}
    if observed_names != set(FACET_NAMES) or any(not entry.is_file() for entry in entries):
        raise ValueError(
            f"facet directory must contain exactly {FACET_NAMES}; observed {tuple(sorted(observed_names))}"
        )
    payloads = {name: (directory / name).read_bytes() for name in FACET_NAMES}
    fields = {name: _parse_line(name, payloads[name]) for name in FACET_NAMES}

    ids = {fields[name].get("id") for name in FACET_NAMES}
    if len(ids) != 1 or None in ids:
        raise ValueError("facet envelope IDs differ")
    try:
        event_payload = bytes.fromhex(fields["HBP"]["payload_hex"])
    except (KeyError, ValueError) as error:
        raise ValueError("HBP payload_hex is malformed") from error
    if fields["HBP"].get("slice_len") != str(len(event_payload)):
        raise ValueError("HBP slice length mismatch")
    try:
        decoded = json.loads(event_payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("HBP payload is not canonical UTF-8 JSON") from error
    if not isinstance(decoded, dict) or _canonical_payload(decoded) != event_payload:
        raise ValueError("HBP payload is not canonical event JSON")

    expected_payload_fields = {
        "base_sha",
        "event",
        "evidence_source",
        "head_sha",
        "operation",
        "pull_number",
        "ref",
        "repository",
        "run_attempt",
        "run_id",
        "rust_clippy",
        "rust_gate_status",
        "rust_numeric_domain",
        "rust_present",
        "rust_toolchain",
        "schema",
        "verification_status",
    }
    if set(decoded) != expected_payload_fields:
        raise ValueError("HBP event payload fields differ from the canonical schema")
    try:
        rebuilt = build_git_facets(
            repository=decoded["repository"],
            event=decoded["event"],
            ref=decoded["ref"],
            base_sha=decoded["base_sha"],
            head_sha=decoded["head_sha"],
            pull_number=decoded["pull_number"],
            run_id=decoded["run_id"],
            run_attempt=decoded["run_attempt"],
            verification_status=decoded["verification_status"],
            rust_present=decoded["rust_present"],
            rust_gate_status=decoded["rust_gate_status"],
        )
    except (TypeError, ValueError) as error:
        raise ValueError("HBP event payload values are invalid") from error
    if any(payloads[name] != rebuilt[name] for name in FACET_NAMES):
        raise ValueError("facet bytes differ from the canonical rebuilt receipt")

    digest = _digest(event_payload)
    short = digest[:16]
    if fields["HBI"].get("repository") != decoded.get("repository"):
        raise ValueError("HBI repository does not match HBP")
    if fields["HBI"].get("event") != decoded.get("event"):
        raise ValueError("HBI event does not match HBP")
    if fields["HBI"].get("ref") != decoded.get("ref"):
        raise ValueError("HBI ref does not match HBP")
    if fields["HBI"].get("head_sha") != decoded.get("head_sha"):
        raise ValueError("HBI head SHA does not match HBP")
    if fields["SHA"].get("algorithm") != "SHA-256" or fields["SHA"].get("digest") != digest:
        raise ValueError("SHA digest mismatch")
    if (
        fields["SH"].get("kind") != "host8_short_coordinate"
        or fields["SH"].get("bytes") != "8"
        or fields["SH"].get("value") != short
    ):
        raise ValueError("SH short coordinate mismatch")
    if (
        fields["HASH"].get("algorithm") != "SHA-256"
        or fields["HASH"].get("value") != digest
        or fields["HASH"].get("verified") != "1"
        or fields["HASH"].get("order") != "HBI_HBP_SHA_SH_HASH"
        or fields["HASH"].get("closure") != "END"
    ):
        raise ValueError("HASH verification mismatch")
    if any(fields[name].get("transport_chain_inferred") != "0" for name in FACET_NAMES):
        raise ValueError("transport-chain boundary mismatch")
    return {name: payloads[name].decode("utf-8").rstrip("\n") for name in FACET_NAMES}


def emit_facet_directory(directory: Path, **event_fields: object) -> dict[str, str]:
    """Create a new, non-overwriting five-file receipt and verify it immediately."""

    directory = Path(directory)
    if directory.exists():
        raise FileExistsError(f"refusing to overwrite existing receipt directory: {directory}")
    facets = build_git_facets(**event_fields)
    directory.mkdir(parents=True)
    for name in FACET_NAMES:
        (directory / name).write_bytes(facets[name])
    return verify_facet_directory(directory)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    emit = commands.add_parser("emit", help="create and immediately verify a new receipt")
    emit.add_argument("--repository", required=True)
    emit.add_argument("--event", required=True, choices=tuple(_EVENT_OPERATIONS))
    emit.add_argument("--ref", required=True)
    emit.add_argument("--base-sha", required=True)
    emit.add_argument("--head-sha", required=True)
    emit.add_argument("--pull-number", required=True, type=int)
    emit.add_argument("--run-id", required=True, type=int)
    emit.add_argument("--run-attempt", required=True, type=int)
    emit.add_argument("--verification-status", required=True)
    emit.add_argument("--rust-present", required=True, type=int, choices=(0, 1))
    emit.add_argument("--rust-gate-status", required=True)
    emit.add_argument("--output", required=True, type=Path)
    verify = commands.add_parser("verify", help="verify an existing five-file receipt")
    verify.add_argument("--directory", required=True, type=Path)
    return parser


def main() -> int:
    arguments = _parser().parse_args()
    if arguments.command == "emit":
        rows = emit_facet_directory(
            arguments.output,
            repository=arguments.repository,
            event=arguments.event,
            ref=arguments.ref,
            base_sha=arguments.base_sha,
            head_sha=arguments.head_sha,
            pull_number=arguments.pull_number,
            run_id=arguments.run_id,
            run_attempt=arguments.run_attempt,
            verification_status=arguments.verification_status,
            rust_present=arguments.rust_present,
            rust_gate_status=arguments.rust_gate_status,
        )
    else:
        rows = verify_facet_directory(arguments.directory)
    for name in FACET_NAMES:
        print(rows[name])
    print("RESULT|status=PASS|files=HBI_HBP_SHA_SH_HASH|transport_chain_inferred=0|json=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
