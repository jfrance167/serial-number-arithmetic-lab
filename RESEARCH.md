# Serial-number arithmetic research — October 5, 2026

Research-stage record, authorized by coordinator SUCCESSORS.md 03:36 under Jake's
verified overnight successor mandate. No application code, candidate execution,
installation, new repository, publication, live systems or additional spending.
That describes the research milestone. Coordinator subsequently approved stages1–4
at04:05; local implementation/verification are complete. Current STATE and
verification/REPORT.md distinguish actual results and retained limits.

## Existing work and distinct learning gap

Read applicable AGENTS, shared STARTUP/routing guidance, vault Home/Integration and
targeted research/project notes. Searches for RFC1982, serial-number arithmetic,
half-range and wraparound found no matching dedicated lab in the searched notes.
One unrelated admission-budget note uses monotonic time; it does not establish
serial arithmetic. This is a bounded search, not an exhaustive vault assurance.

Inspected actual local dns-cache-semantics-lab/cache_lab.py load/validate: normalized
cache events use simulated milliseconds and TTL expiry, not SOA serial comparison.
network-forensics-pcap-lab/generate_synthetic_pcap.py:tcp writes a supplied sequence
integer to a header; pcap_forensics.py:_parse_frame drops sequence numbers from its
Packet representation. No matching comparison/reassembly model was found in these
sections. No capture opened or generator executed. Packet-budget exact-byte admission
and bounded output/error patterns, including CPython shutdown-flush handling, are
useful owned-code patterns; the new arithmetic remains independent, without sibling
runtime imports or changes. Earlier scanner live Linux SYN remains unrun.

## Primary standard and interpretation

[RFC1982](https://www.rfc-editor.org/rfc/rfc1982.html), sections 2–5 and 7, read via
official browsing. Let M=2^w, H=M/2. Encoded values are integers 0..M-1. Defined
increments are 0..H-1; additions outside that interval are undefined. Comparison
must preserve exact-H ambiguity, distinct from known inequality. At width 8,
255+1 wraps to 0; 0 and 128 have undefined ordering. Valid successive +100 steps
from 100 reach 200 then 44, which compares below 100. Therefore local valid steps
do not imply global ordering. DNS uses width 32; smaller widths are teaching examples.
Do not treat this as a TCP engine, chronology, freshness or authenticity evidence.

Inference for this lab: preserve undefined as a report state, avoid comparator/sort
APIs, and show numeric ordering separately. Each concrete endpoint comparison is
evaluated; the corollaries do not mean every multi-step endpoint is undefined.
The errata page request failed; no errata review claim. No official standard-status,
advisory or security certification was established from these reads.

## Connected GitHub candidates actually inspected

Searches `rfc1982` and `serial number arithmetic` returned agrommek/SerialNumber,
lgrahl/sna, io7m-com/jserial, ypoluektovich/serial-number-arithmetic.rs,
sweet-security/seqnum and dustins/sna. Strongest bounded arithmetic candidates below
received actual source/tests/manifests/tree/maintenance inspection; other search hits
were not equivalently assessed. Tree listings were not truncated. No star-based claim.

### lgrahl/sna

Pin [eda1fe2db1f0076116f526e10d3a2c648b216aa4](https://github.com/lgrahl/sna/tree/eda1fe2db1f0076116f526e10d3a2c648b216aa4).
Latest commit returned by date-sorted search: November 18, 2017 (clippy linting).
Read complete [src/lib.rs](https://github.com/lgrahl/sna/blob/eda1fe2db1f0076116f526e10d3a2c648b216aa4/src/lib.rs),
in-file tests, README, Cargo.toml, LICENSE, .travis.yml and appveyor.yml.
Source blob e01507aeed90b952de770e5f5730fd3d7f15fd93.

Unsigned 8/16/32/64-bit wrappers; comparison returns None for half-range pairs.
Actual addition uses Wrapping for every unsigned increment, with tests adding the
type maximum. This exceeds the standard's defined increment interval; unsuitable
as this lab's addition oracle. Source-derived example: width 8 one plus 255 is
returned as zero, whereas the lab must label that increment undefined. No execution
or exploit claim. Comparison test coverage includes ambiguous pairs and RFC examples.

MIT, copyright Lennart Grahl 2017, actual notice inspected: retain copyright and
permission notice if copying substantial code. Default features empty; one optional
clippy 0.0.171 dependency. Historic Travis builds/tests stable/beta/nightly on Linux,
then downloads unpinned kcov master and pipes remote Codecov script into bash.
AppVeyor downloads rustup and runs Windows builds/tests. These are inspection findings,
not current CI passes; do not execute or import those workflows. No issues returned
by the bounded repository issue query; that does not prove absence of defects.

### sweet-security/seqnum

Pin [3d47abd16a2efe9ca55095f60b76a2a14bb8f41a](https://github.com/sweet-security/seqnum/tree/3d47abd16a2efe9ca55095f60b76a2a14bb8f41a).
Latest commit returned: initial commit October 8, 2025. Read complete
[src/lib.rs](https://github.com/sweet-security/seqnum/blob/3d47abd16a2efe9ca55095f60b76a2a14bb8f41a/src/lib.rs),
its test function, README, Cargo.toml/lock and complete tree.
Source blob 95ef2b7c5b724170331bfe43bc9de1aa7bf6bf03.

Generic Rust unsigned storage plus declared width, mask/wrapping operations.
PartialOrd always delegates to Ord; exact half-range differences fall through to
Greater. Source-derived width-8 pair 0/128 therefore produces Greater in BOTH
directions. Tests contain wrapping cases but no exact half-range control. This
does not preserve the proposed undefined contract; ordinary total-order expectations
must not be inferred from its Ord interface. Add accepts unrestricted storage-width
increments. Width checks use debug_assert, and From masks values rather than rejecting
out-of-range input; those differ from strict teaching admission. No candidate run.

Cargo manifest declares MIT and no dependencies; lock contains only this package.
Complete inspected tree lacks LICENSE and CI definitions. MIT declaration alone
does not supply a verified notice/copyright attribution; no adoption/copying planned.
No issues returned by bounded query. One returned commit and absent inspected CI
do not establish current compatibility, maintenance quality or security.

## Recommendation and alternatives

Build original Python stdlib exact integer arithmetic after plan approval. Both
inspected crates are useful source comparisons but unsuitable unchanged for explicit
undefined addition/comparison admission. Forking adds Rust/build/license maintenance
without meeting the small Python JSON teaching contract. No suitable unchanged
candidate found in these searches; not a claim of exhaustive discovery or insecurity.

Alternative: ordinary monotonically increasing sequence ledger. It gives familiar
total integer order when continuity/nondecrease is asserted, but cannot explain wrapped
values without extra epoch/history assumptions. Choose the serial lab; report ordinary
numeric comparisons/unwrapped sums as explanatory controls, not real sequence recovery.
No dependencies needed for powers, integer arithmetic, JSON and unittest. This reduces
installation scope, not a claim that stdlib is automatically safe. Supply-chain review,
Scorecard, advisories, package artifacts and hosted runs were not performed.

## Worker and evidence choices

One sandbox attempt was denied loopback access (EACCES) before inference; raw failure
metadata retained. Normal app-approved loopback execution with a fresh output accepted
exactly four supplied labels in 5340 ms, 17 output tokens, done_reason stop. Raw
brief/draft/metadata retained separately. No generated code executed. Codex retains
source/math/security judgment; accepted labels do not demonstrate general capability.
Explicitly considered free OpenRouter via OmniRoute; unnecessary after local extraction.
Shared read-only startup report was checked at 07:34 UTC, inference_requests_sent zero;
it is not proof of inference/pricing/eligibility for a future remote call. No remote
draft, readiness refresh, config change or extra spending. Laya's tested classification/
triage schema does not fit arithmetic planning. PLAN.md defines the approval gate.
