# Security model

Invented JSON operands only; no actual network/counter/device/DNS/TCP operations.
Application uses json/re/sys; no socket/process/eval/deserialization/foreign dependency
or automatic file discovery. CLI reads the caller-selected synthetic JSON file/stdin,
bounded cap+1; API takes exact bytes. This is not an isolation boundary.

Untrusted representation: raw64KiB, nesting6 before object decoding, integer tokens11,
decoded printable-ASCII strings64, exact fields/types, width2..32 before exponentiation,
bounded operands/increments/cases/steps, duplicate keys/IDs rejected. All admission
before outcomes. BOM/negative-zero/version behavior explicit in SCHEMA. Final JSON
256KiB guard checked before return/write; no truncation. Logical caps do not enforce
hard memory/time or protect against a blocking input device/pipe; callers use fixtures.

Semantic risk: mathematical undefined never becomes an invented value/order; undefined
addition stops chain evaluation while comparison ambiguity preserves known values.
No comparator sorting/freshness/authenticity/epoch inference. Fixed limitations remain
in each report. Ordinary controls do not become observations of actual systems.

Delivery risk: short/flush/closed stdout/stderr errors retain controlled exit2, including
help/misuse. Fixed diagnostics avoid input/path echo. Partial failing sink can receive
bytes; no atomic report delivery. Only Windows3.13.7 tested. Tests/mock coverage is
evidence for exercised paths, not general containment or protocol conformance.

ECC implementing-agent self-review and Bandit application/tests/verifier completed;
no independent audit, hosted scans or dedicated secrets/history scanner. No repository
or publication created. Report future defects to the owner with bounded invented
reproducer; do not include private real-system evidence or credentials.
