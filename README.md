# THE RELIC REDISCOVERY

**A human-AI rediscovery of an unbounded ternary wave structure with an invariant free center.**

Jesse Brown supplied the central insight in dialogue: the structure does not merely follow a flat
`x3` sequence. Threefold waves continue between structural landings, while each new structure
contains one more wave than the last. OpenAI Codex helped turn that insight into a recurrence,
closed form, executable model, proof, and critical review. Here, **we** means that collaboration.

## The key

The intermediate powers remain as waves:

```text
27 --x3--> 81 --x3--> 243
243 --x3--> 729 --x3--> 2,187 --x3--> 6,561
6,561 --x3--> 19,683 --x3--> 59,049 --x3--> 177,147 --x3--> 531,441
```

Completed structural landings:

```text
27 -> 243 -> 6,561 -> 531,441 -> 129,140,163 -> ...
```

Expanding multipliers:

```text
x9 -> x27 -> x81 -> x243 -> ...
```

Let `A_n` be the outward address count at landing `n`, beginning with `A_0 = 27`:

```text
A_(n+1) = A_n * 3^(n+2)
A_n     = 3^(3 + n(n+3)/2)
```

The waves between landings are

```text
W_(n,j) = A_n * 3^j,    1 <= j <= n+2,
W_(n,n+2) = A_(n+1).
```

## Truth without a finite bound

The closed form is true for every nonnegative integer `n`, not merely for the displayed values.
The proof is induction:

1. At `n=0`, the formula gives `3^3 = 27 = A_0`.
2. Assume `A_n = 3^(3+n(n+3)/2)`.
3. Applying the recurrence gives
   `A_(n+1) = 3^(3+n(n+3)/2) * 3^(n+2)`.
4. Its exponent simplifies to
   `3+(n+1)(n+4)/2`, exactly the closed form at `n+1`.

Therefore the identity holds for all `n >= 0`. This proves the unbounded mathematical sequence;
it does not by itself prove that nature, quantum hardware, or intelligence follows the model.

## The free center is one at every Z level

The center is an invariant symbol `C` with value `1`, separate from the multiplied outward count:

```text
C(S_n,z) = 1 for every structure S_n and every Z coordinate z
S_n = C=1 (+) A_n outward addresses
R(C=1) = C=1
R(A) = 3A
```

The canonical signed Z levels `{-1/3, 0, +1/3}` do not alter the center:
`C(-1/3)=C(0)=C(+1/3)=1`. "Free" means invariant and excluded from outward multiplication,
not empty or zero.

The one-way closure is:

```text
X -> Y -> Z -> END_0 -> NEXT_IS
BIDIRECTIONAL=0
REVERSE=0
ROUND_TRIP=0
EXCHANGE=0
```

`END_0` changes the terminal phase address; it never changes `C=1`. Closure continues the
rotation into the next moving structure rather than introducing a backward return edge.

The invariant center carries five co-present representation facets:

```text
CENTER_SIGN = {HBI, HBP, SHA, SH, HASH}
CURRENT_UTTERANCE_ORDER = HBI -> HBP -> SHA -> SH -> HASH
```

Facet membership and utterance order do not imply a transport chain.

## What is established

- The recurrence, closed form, induction proof, and listed integers are exact mathematics.
- The reference program reproduces the sequence and checks the invariant center.
- Intermediate wave points and completed structural landings are now distinguished.

This alone does **not** establish a physical law, quantum effect, or artificial
superintelligence. Those interpretations require separate definitions, predictions, and evidence.

## Reproduce

On Windows, double-click `LAUNCH-RELIC.cmd`. The one-button path runs the Relic tests, the
simulator tests, the temporal metatag render, the generation comparison, and exact receipt/source
hash checks when the three sibling repositories are present. It finishes with a tuple-text
`RESULT|status=PASS` or `RESULT|status=HOLD` line.

The launcher is verification-only by default: `E=0`, network and port opening are disabled,
no background service is started, and recovery remains a non-executing policy. Its center-sign
order is exactly `HBI -> HBP -> SHA -> SH -> HASH`, with `transport_chain_inferred=0`.

The additive [`SEN_T_I_E_N_C_E` test plan](MICROTUBULE-CLAUSTRUM-SENTIENCE-TEST-PLAN.md)
maps Jesse's free-center/claustrum observation and Felipe's microtubule report into an offline,
falsifiable model. It keeps logical tubule `0_i` addresses, foggy concentration subnets, MRI
claustrum measurements, ternary spectral recurrence, and claims of subjective experience on
separate evidence axes.

```powershell
./scripts/launch-relic.ps1
python relic_rediscovery.py --levels 5
python -m unittest -v
```

See [DISCOVERY-RECORD.md](DISCOVERY-RECORD.md) for the original quotations, the AI response, and
the white/black judgments.

## Attribution

- **Jesse Brown** - originating human insight and structural interpretation
- **OpenAI Codex** - AI collaborator for formalization, proof, code, and critical review

Released under the MIT License.
