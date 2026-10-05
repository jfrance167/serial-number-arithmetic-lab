# Serial-number arithmetic lab — proposed implementation plan

Tier 3 teaching/security tool; RESEARCH/PLAN ONLY, October 5, 2026. Coordinator
SUCCESSORS.md 03:36 authorizes this research under Jake's direct overnight mandate.
**APPROVED stages 1–4 at coordinator SUCCESSORS.md October 5 04:05.**
Approval/addendum recorded before application code. Freeze the complete contract,
examples and hashes first. Explicitly reject BOM/unknown version; admit negative-zero
as integer zero. All three proposed mutants are mandatory. Replace conventional
argparse with fixed fully checked help/usage/diagnostics; normal/-O actual output
failures must preserve exit2, suppress shutdown120 and never echo caller input/paths.
Measure maximum admitted output shape; chain statuses/null/undefined rules below
must be frozen explicitly. This approved addendum supersedes earlier proposed wording.
Sole writer in the existing chat; separate directory; cutoff October 6 08:00 Eastern.
RESEARCH.md contains actual reuse/source/license/maintenance evidence. Task checkpoints
are in tasks/todo.md; this PLAN is authoritative over the tasks/plan.md pointer.

## Problem, success and scope

Encoded serial numbers wrap. Ordinary numeric order, valid single increments and
relationships between distant endpoints answer different questions. A small offline
JSON lab should expose these differences while preserving undefined outcomes.
Success means exact, reproducible results for admitted invented operands, explicit
half-range ambiguity and increment limits, independent expectations, bounded parsing/
reporting, and clear lack of chronology/authenticity/freshness guarantees.

Implement original Python stdlib API and CLI only. Python 3.11+ intended; verify
installed Windows CPython 3.13.7, report other runtimes/platforms unverified. No
dependency or candidate installation. No network, socket/DNS resolution, actual
counters, packets/captures, serial devices, live DNS/zone changes, TCP windows/receiver,
reassembly, clock or host changes, credentials, repository setup/publication/paid calls.
No subtraction/decrement, user-defined comparisons, comparator/sorting API, epoch
inference, timestamps or automated decisions about observed real systems.

## Proposed exact admission contract

`analyze(data: bytes) -> dict` accepts exact built-in bytes; other objects rejected
without coercion. CLI reads a caller-selected JSON file or `-` stdin, at most cap+1
bytes. No directory walk, filename expansion, report file creation or shared import.

Root has exactly `{version: 1, cases: [...]}`; exact built-in integer version, no bool.
0..64 cases, unique case-sensitive IDs matching `[A-Za-z0-9][A-Za-z0-9-]{0,31}`.
Each case has exactly one of these key sets:

| Operation | Required fields |
|---|---|
| compare | id, operation="compare", width, left, right |
| add | id, operation="add", width, start, increment |
| chain | id, operation="chain", width, start, increments |

Width is an exact integer 2..32, validated before exponentiation. M=2^width and H=M/2.
All encoded operands (`left/right/start`) are exact integers 0..M-1; reject rather
than mask/modulo invalid operands. Increments are exact signed integers -M..M;
this bounded teaching admission intentionally includes values whose RFC addition is
undefined. Negative and H..M increments admitted but undefined; values outside -M..M
are profile-invalid. Chain increments array 0..16, at most 256 total declared chain
steps across the envelope, checked before evaluation. Empty chain is identity.
No floats/exponents, numeric strings, bool integers, unknown fields/operations, null,
missing fields or silent defaults. No actual DNS SOA object or TCP profile admitted.

Raw input <=65536 bytes; UTF-8 only, lexical nesting <=6 before JSON object decoding;
number tokens <=11 characters before int conversion (covers -4294967296); decoded
strings/keys <=64 printable ASCII characters. Reject controls, DEL, non-ASCII and
surrogates; IDs have the tighter LDH bound. Reject duplicate decoded keys, including
escaped spellings, NaN/infinity, trailing content and malformed JSON. Field/list
limits are admission limits after bounded raw decoding, not preallocation/RSS claims.
Validate the ENTIRE common envelope/cases first; malformed later input rejects the
whole run even after an earlier mathematically undefined operation. No prefix report.

## Arithmetic and defined-versus-undefined behavior

Source: [RFC1982 sections 3–5](https://www.rfc-editor.org/rfc/rfc1982.html).
Addition is defined only for 0<=n<H, producing (start+n) modulo M. Zero is defined.
Admitted invalid-domain increments produce status undefined, reason
`increment_outside_rfc_domain` and null derived results; do not silently normalize them.

Compare uses distance d=(right-left) modulo M. Equal numeric values give equality;
0<d<H gives left less than right; d>H gives left greater than right; d=H gives
undefined ordering with known equality=false. Ordinary `numeric_relation` is reported
separately. Names always refer to LEFT versus RIGHT, not freshness or age.
The production implementation may use this distance form; independent test oracles
must use explicit RFC integer inequalities or short enumerated successor paths.

For chain, each defined increment has a concrete next encoded value. Report comparisons
of that value against both previous and original start. A half-range comparison is
undefined but does NOT invalidate the known encoded value or stop the next addition.
An undefined ADDITION has no next value: mark that step undefined and all later steps
`not_evaluated`, reason `prior_undefined_addition`, before/after/results null. Preserve
the evaluated prefix visibly, but no complete-chain final or aggregate prediction.
No fabricated sum/result after failure. A valid chain's exact sum may exceed H-1:
its sequential result remains defined, while a SINGLE addition of that sum is undefined.
Endpoint comparison is evaluated on the actual supplied result, not inferred from a
generic corollary. The ordinary unwrapped total is explanatory arithmetic, not a
recovered epoch/history. Repeated zero increments remain allowed and equal.

## Proposed report and CLI contract

Compact deterministic JSON, input row order retained. Root exact fields:
`version=1`, `profile="rfc1982-teaching-v1"`, `status`, `has_undefined`, `rows`,
`limitations`. Status `defined` unless any attempted arithmetic/comparison/aggregate
check is undefined, then `contains_undefined`. Empty envelope is defined.
Each row: `id`, `operation`, `width`, `modulus`, `half_range`, `input` (exact admitted
operands), `status` (`defined` or `undefined`), `reason` (null or fixed reason),
`has_undefined` and operation-specific `result`. Never rely on status-string truthiness.

Compare result always includes `equal` boolean, `numeric_relation` (less/equal/greater),
`serial_relation` (less/equal/greater/undefined) and `forward_distance`. Row status
undefined only for d=H, reason `half_range_comparison`; equality/distance remain known.
No ordering booleans for an undefined pair.

Add result exact fields `value`, `ordinary_sum`, `wrapped`, `relation_to_start`;
all null for undefined addition. Defined values report exact nonwrapped sum and
whether it reaches/exceeds M. Relation greater for positive valid increment, equal
for zero. Invalid admitted input is not mathematical undefined: it raises LabError.

Chain result exact fields `steps`, `final`, `increment_sum`, `ordinary_final`,
`numeric_final_relation`, `endpoint_relation`, `single_addition_of_sum`.
Each step exact fields `index` (0-based), `increment`, `status`, `reason`, `before`,
`after`, `wrapped`, `relation_to_previous`, `relation_to_start`. Relations null for
undefined addition/not-evaluated; an evaluated relation may equal `undefined` for H.
After addition failure all chain aggregate fields null except steps; row status
undefined/reason `undefined_chain_addition`, has_undefined true. If all steps defined,
row status defined/reason null; complete-chain aggregates set and has_undefined may
still be true because a step endpoint, final endpoint or aggregate addition is undefined.
`single_addition_of_sum` is `{status, reason, value}`: defined/null/result for sum<H,
undefined/increment_outside_rfc_domain/null otherwise. No chained collapse shortcut.

Root limitations fixed: `synthetic_operands_only`, `pairwise_relation_not_sort_order`,
`history_chronology_freshness_authenticity_unverified`, `not_dns_or_tcp_engine`.
Documentation clarifies that even non-half-range pairs can form ordering cycles.
Final serialized output <=262144 bytes, checked before API returns and CLI writes.
Stage 1 must review a conservative report-shape bound; stage 3 exercise largest
admitted shapes and narrow cap seam without claiming hard RSS/time or atomic sink
delivery. Do not cap/truncate rows silently to fit output.

CLI exit 0 when report contains no undefined result; 3 when contains_undefined,
including a valid chain's undefined aggregate/endpoint check; 2 for admission, cap
or I/O failure, with no report for admission errors. Buffered complete JSON before
writing; detect short writes and flush failures. A partially failing sink may receive
a prefix; no atomic OS-delivery claim. Suppress failed shutdown flush retries so
CPython does not substitute exit120; diagnostic failure must retain exit2 too.
No caller input or paths echoed in errors. Help is conventional argparse behavior.

## Independent hand expectations to freeze before application code

These are independently worked expectations, not generated from the eventual function.

| Case | Width / operands | Expected serial outcome and control |
|---|---|---|
| equal | 8 compare 7,7 | equal; distance0; numeric equal |
| wrap pair | 8 compare 255,0 | less; distance1; numeric greater |
| half pair | 8 compare 0,128 | undefined; equality false; distance128; numeric less |
| reversed half | 8 compare 128,0 | undefined; equality false; distance128; numeric greater |
| below/above half | 8 compare 0,127 then 0,129 | less then greater; distances127/129 |
| zero add | 8 start255 +0 |255; ordinary255; wrapped false; equal |
| wrap add | 8 start255 +1 |0; ordinary256; wrapped true; greater vs255 |
| maximum defined | 8 start200 +127 |71; ordinary327; wrapped true; greater vs200 |
| first undefined | 8 start200 +128 |undefined; all addition result fields null |
| negative/full turn | 8 start0 -1 then +256 |both undefined additions, not wrapped values |
| repeated valid | 8 start100 increments[100,100] |200 then44; final less vs100; sum200 single-add undefined; ordinary300 |
| exact-half endpoint | 8 start0 increments[64,64] |64 then128; second vsstart undefined; complete final128; aggregate128 undefined |
| complete turn | 2 start0 increments[1,1,1,1] |1,2,3,0; final equal; sum4 single-add undefined; no freshness |
| empty/zero chain | 2 start3 [] and [0,0] |final3; sum0; endpoint equal; single-add defined3 |
| stop after invalid add | 8 start250 increments[5,128,1] |255; undefined next; last not_evaluated; aggregates null |
| DNS-size illustrative | 32 start4294967295 +1; compare0,2147483648 |0 then undefined comparison; no DNS operational claim |

Additional literal cycle at width8: 0<100, 100<200, 200<0. No comparator sorting.
Stage 1 freezes full expected schema/status/priority plus hand-oracle JSON and
example bytes/hashes before application implementation. Include valid, mixed undefined,
empty and invalid-later envelopes. Preserve originals if a fixture defect is found;
record correction provenance, do not silently replace expectations to pass code.

## Architecture, alternatives and threat model

One serial_lab.py module: bounded byte load → common exact admission → compare/add/
chain evaluation → bounded encoding → API/CLI. No external process/network/candidate
imports; fixed verification helper may run only local Python/tests/Bandit under tests.
Owned admission/closed-output patterns may be reused after reading; no shared helper
rewrites or copies of unrelated private data. Unit tests are independent of candidate
libraries. Original work MIT, source links and AI-assistance disclosure; no candidate
code adoption planned (seqnum license notice missing from inspected tree).

Ordinary monotonic-sequence alternative is simpler for asserted continuous, increasing
unbounded counts, but cannot explain wrapped serial pairs without epochs. Library
forks add build/dependency/license maintenance while differing on undefined outcomes.
Choose original stdlib teaching model; no confirmed safety claim for candidates or lab.

Assets: honest result semantics, host configuration/data, retained evidence and bounded
resources. Untrusted JSON can exploit integer coercion, deep/token-heavy input, duplicate
keys, report growth or terminal controls; early raw/token/depth/string checks and exact
admission mitigate these. Lexical scan must handle quoted/escaped delimiters correctly.
Status conflation can fabricate result/order after undefined; fixed null/step rules,
whole-input admission, typed fields and independent tests mitigate it. Users may infer
freshness/global order; fixed limitations, numeric controls and cycle example counter
that misuse. Worker output/external repositories are data, never authority. No shell,
eval, pickle, real traffic or generated-code execution. Forbidden-capability mocks
cover exercised paths, not an isolation boundary. Logical caps are not hard time/RSS.

## Stages, dependencies and definitions of done

1. **Freeze contract and expectations (after plan approval).** Write SCHEMA plus hand
   oracles/examples and pre-code hash receipt; reconcile every operation/status/domain,
   repeated-chain case and conservative output shape. No implementation until this
   foundation passes self-review. Task 1; no dependency; <=5 files per small slice.
2. **Admission and arithmetic slices.** Implement byte loader/whole admission, compare
   and add API/CLI with focused tests, then chain with fail-stop and comparison-only
   ambiguity controls. Tasks 2–3 depend on 1 and then 2. Each slice must match frozen
   values and rejects before proceeding; no extra human gate inside approved stages.
3. **Independent verification and ECC review.** All pairs widths2..5 checked against
   literal RFC inequalities; all additions at widths2..5 and representative invalid
   increments against pre-enumerated cycle walks, plus width8/32 boundary literals.
   Chain tests use explicit expected step arrays, single-add versus repeat distinction,
   equal-after-full-turn and ambiguity continuing future additions. Admission, numeric
   token/depth/raw/output bounds, duplicate keys, controls, invalid-later precedence,
   input order, short/flush/double-sink failure and real normal/-O child exits tested.
   Mock socket/DNS/process capabilities at exercised application paths. Mutations must
   each fail meaningful assertions: map d=H to greater; permit n=H; optionally collapse
   chain to single sum (then valid repeated chain must fail). Restore exact source in
   finally, clear only own relevant caches and re-run affected normal/-O checks,
   compile and available Bandit. No candidate execution. ECC pinned actual-change
   self-review, fix actionable defects and recheck; no independence claim. Tasks4–5.
4. **Portfolio and knowledge completion.** README with commands/statuses/demo/architecture/
   limitations/security/learning, SECURITY, LICENSE/attribution/AI disclosure, concise
   STATE/DECISIONS/LEARNING and exact verification report/receipt. Reusable small verifier
   with inputs/outputs/usage/assumptions, source-restoration/concurrency limits. Record
   only actual runtime/tests/mutations/audit findings and unresolved gaps. Relevant
   guarded Obsidian update through app approval or pending note if blocked. Tasks6–7.

Standing done: frozen contract matches, all approved acceptance criteria demonstrated,
source restoration verified, no unresolved confirmed in-scope defects, ECC self-review
and affected checks complete, docs match actual behavior, no private material or
unrelated modifications, all skipped checks disclosed. No repository/CI/publication
implied; earlier scanner Linux SYN and hosted/runtime/independent gaps stay preserved.
Never mark a rejected verifier passed or bypass an app review rejection.

## Worker choice, risk and approval checkpoint

Installed loopback qwen3.5:2b extracted four supplied labels, reviewed/accepted; raw
draft/failure metadata kept. No remote inference, repeated-model attempts or paid fallback.
Local extraction suitability does not outsource arithmetic/security judgments. Laya
schema unrelated; OpenRouter considered unnecessary. Future remote calls require fresh
eligible/free verification and public-only scope, separate from readiness.

Highest correctness risks are reversed comparison direction, exact-H off-by-one,
normalizing invalid operands/increments, chain continuation after undefined addition,
and global-order assumptions. Their controls are explicit in the frozen hand cases
and meaningful mutations. Runtime/hosted/independent checks remain uncertain until run.
No essential implementation question needs a separate user answer: the coordinator
must approve this proposed contract and stages 1–4 before code. A material change to
these semantics/bounds/scope must be surfaced before dependent work.
