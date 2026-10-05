# Local verification — October 5, 2026

Approved PLAN stages1–4 and04:05 addendum implemented locally. Windows CPython3.13.7
only. Original exact-byte stdlib application; twenty hand oracles and four examples
frozen with SCHEMA/hashes BEFORE application code. No repository/dependency installation.

| Check | Actual result |
|---|---|
| Normal tests |28 passed, normal.log|
| Optimized tests and normal/-O child controls |28 passed, optimized.log|
| Pre-code frozen hashes |all six unchanged|
| Independent literals |twenty complete result oracles matched|
| Small comparison domains |all1360 pairs widths2..5, independent RFC inequalities|
| Small addition domains |680 defined via enumerated cycle paths;300 representative undefined|
| Width coverage |all2..32 wrap and half-adjacent controls|
| Chain distinctions |comparison ambiguity continues, undefined addition stops, defined row/undefined check flags distinct|
| Common admission |late invalid before evaluation; BOM/-0/version/type/caps/duplicates controls|
| Help/misuse/report errors |real normal/-O closed/both pipes and locally closed Python streams preserve2|
| Short/flush diagnostics |bounded seams in actual normal/-O children plus unit controls|
| Half-forced-order mutant |exit1, ten assertion failures, intended half test failed|
| Increment-H-admitted mutant |exit1, seven assertion failures, intended increment test failed|
| Chain collapsed to single sum mutant |exit1, seven assertion failures, intended chain test failed|
| Restoration |exact original source restored; final normal/-O/compile/SAST passed|
| Compilation |exit0|
| Bandit1.9.4 application/tests/verifier |zero findings/errors; nine narrow harness exclusions|
| Four examples |defined0/three rows, empty0, mixed3/four rows, invalid-late2/no stdout|

receipt.json binds ten current source/test/verifier/schema/oracle/frozen-receipt/example
files. Application SHA256:
`9df8c7650a41202f34c8c044caca25870fe3a31d4a443aee01319710eaaee4b1`.
Independent PowerShell hash reconciliation found zero mismatches. Latest-run passed;
failed/running marker makes any old receipt historical. Reusable verify.py checks
intended assertion names, not merely any exception/nonzero mutant exit. No source
changes after final checks; only completion documents/knowledge note updated.

## ECC actual-change self-review

Installed ecc-code-review/pinned code-reviewer checklist and ecc-verification-loop
applied to actual source, callers/admission/operations/encoding/main, tests, helper,
frozen schema/oracles/examples and portfolio records. No independent reviewer/audit.
Reviewed exact integers before shifts, no operand masking, half-range direction,
bounded JSON grammar/strings, whole admission, independent oracle forms, chain prefix/
continuation/null/aggregate flags, output counts/flush/failure paths and verifier
restoration/no shell/own-cache scope. Private-material review limited to authored
synthetic task files; no dedicated secret/history-scanner assurance.

Confirmed MEDIUM local correctness issue at serial_lab.py `_diagnostic` and main
error handlers (current lines254 and281): locally closed Python stream raises
ValueError rather than OSError. Original help child with stdout.close() exited1
instead of controlled2. Red test evidence retained in ecc-closed-stream-before.log.
Correction: catch OSError/ValueError, detach failed diagnostic/output sink and use
fixed no-input/path-echo message. Added actual normal/-O stdout/stderr/both/stdin local
closure controls; affected checks and all final mutations/tests/compile/Bandit rerun.
No unresolved confirmed in-scope defects. Zero critical/high/unresolved medium findings;
completion recommended locally only, no merge/publication authorization.

Nine narrow Bandit exclusions: tests B404 import and six fixed B603 local Python
subprocess sites; verifier B404 import and one fixed B603 subprocess site. Application
has no suppressions. No network/installation/foreign code/shell execution.

## Bounds and stress evidence

output-stress.json: largest admitted count/width/label/chain allocation shape,64rows,
256chain steps,16steps each, width32/max-start/max-valid increments/32-character IDs,
input10809 bytes and output74934 bytes (<262144). Remaining48 rows are comparison
controls. This is one stress measurement, not exact serialized maximum proof.
Negative/undefined forms can have longer status/reason strings; conservative shape
allowance covers them:1000bytes per row outside step-dependent arrays,320 per step
including repeated input increment token,1024 envelope. 64*1000+256*320+1024=146944
<262144. Fixed printable LDH labels/controlled strings need no extra escaping, integer
widths finite (aggregates<=11digits). No row truncation. Defensive output guard tested
by reducing cap to one byte at a narrow seam, not a reachable valid-overflow claim.

Raw/string/list limits are logical admission bounds, not hard RSS/time. Blocking
input devices/pipes remain outside bounded fixture usage. Forbidden-call mocks only
cover exercised application paths; actual source review supports no network/process
imports, not host containment. Buffered output can partially reach a failing sink.

Other Python/Linux/hostedCI/CodeQL/advisory/Scorecard/package execution/dedicated
secret-history scanner/independent audit NOT RUN. No real counters/traffic/devices/
captures/DNS/TCP/sorting/history/epoch/freshness/authenticity assurance. Original
scanner live Linux SYN unrun; prior accepted projects and parent work unchanged.
