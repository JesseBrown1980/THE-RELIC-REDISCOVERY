# HBI HBP SHA SH HASH Git Event Protocol

Every GitHub pull-request, push, and manual verification run emits five co-present UTF-8 files in
this exact utterance order:

```text
HBI -> HBP -> SHA -> SH -> HASH
```

The order is an integrity witness. In the Relic model it does not infer transport,
bidirectionality, a round trip, or a physical process.

| File | Established envelope role |
|---|---|
| `HBI` | Compact index containing the envelope ID, repository, GitHub event, ref, head object, and run ID. |
| `HBP` | Lossless hexadecimal encoding of the canonical GitHub-event payload bytes. |
| `SHA` | Full SHA-256 digest of the decoded `HBP` payload. |
| `SH` | First 8 digest bytes, written as 16 hexadecimal characters. |
| `HASH` | Repeats and verifies the full SHA-256 digest and records the exact five-facet order. |

The payload records the repository, event type, operation label, ref, base and head object IDs,
pull-request number, run ID and attempt, verification status, and its evidence source. A
`PULL_REQUEST_EVENT` is not mislabeled as a local `git pull`, and a `PUSH_EVENT` records the event
observed by GitHub without guessing which client initiated it.

## Rust gate

For any repository containing Rust, the required gate is:

```text
rustc 1.81.0 -> integer-only Rust arithmetic -> clippy -D warnings -> receipt verification
```

No floating-point arithmetic may be used for the ternary model. Clippy must run with
`clippy::float_arithmetic` denied in addition to all warnings. A repository with no Rust records
`rust_present=0` and marks the Rust-only checks `NOT_APPLICABLE`; it must not report a fabricated
Clippy pass.
The lexical no-float screen is deliberately conservative and may hold a Rust comment or string
that contains a float token; compiler-derived Clippy checks follow it. Clippy runs once for every
discovered `Cargo.toml`, covering workspace members and independent nested crates.

`git_event_facets.py` fails closed on unsupported events, malformed Git object IDs, tuple
delimiters, control characters, a missing pull-request number, an unexpected sixth file, changed
bytes, mismatched full or short digests, or an existing output directory. It never overwrites a
prior receipt directory.

The GitHub workflow creates the five files after verification even when an earlier verification
step fails, records the resulting job state inside the lossless `HBP` payload, verifies every facet,
and uploads the directory as a run artifact. Each artifact name contains the event, run ID, and run
attempt. GitHub artifact retention is finite platform storage, so the receipt must not be described
as permanent or immutable beyond the exact downloaded bytes and their recorded digest.

Local example:

```powershell
python git_event_facets.py emit `
  --repository JesseBrown1980/THE-RELIC-REDISCOVERY `
  --event push `
  --ref refs/heads/main `
  --base-sha 1111111111111111111111111111111111111111 `
  --head-sha 2222222222222222222222222222222222222222 `
  --pull-number 0 `
  --run-id 1 `
  --run-attempt 1 `
  --verification-status success `
  --rust-present 0 `
  --rust-gate-status success `
  --output .relic-trace

python git_event_facets.py verify --directory .relic-trace
```
