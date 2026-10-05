# Frozen serial teaching contract v1

Approved PLAN + coordinator04:05 addendum. Frozen before serial_lab.py. Pure exact
bytes API, JSON file/`-` CLI. RFC1982 illustrative arithmetic, no real system/order/
freshness/authenticity claim. Input/root/version/operation shapes and bounds below
are exact; no defaults, coercion, masking, truncation or unsupported-version fallback.

Admission priority: (1) exact bytes/raw<=65536; (2) explicit UTF-8 BOM rejection,
UTF-8 decode; (3) quote/escape-aware lexical nesting<=6; (4) JSON grammar, duplicate
decoded keys, integer token<=11, reject float/exponent/NaN/infinity; (5) all decoded
strings/keys <=64 printable ASCII; (6) root exact version/cases fields and exact
integer version1; (7) cases array<=64; (8) each input-order case: object/operation
enum, exact fields, ID pattern/duplicate, exact width2..32, encoded operands0..M-1,
increments signed-M..M, chain array<=16 and running total declared steps<=256.
All cases admitted before arithmetic; no partial report on invalid input. JSON grammar
errors remain invalid rather than pretending to be mathematical undefined. JSON -0
is accepted/canonicalized to integer0; token spelling is not retained. BOM including
leading BOM after whitespace remains invalid JSON. Unknown version is invalid.

ID `[A-Za-z0-9][A-Za-z0-9-]{0,31}`, unique case-sensitive; trailing hyphen allowed.
Exact built-in integer values; bool not integer. M=2^width; H=M/2. Exact cases:
- compare: id,operation="compare",width,left,right.
- add: id,operation="add",width,start,increment.
- chain: id,operation="chain",width,start,increments (array0..16).
Empty cases and empty chain valid. Increments outside signed-M..M profile-invalid;
inside admission but outside0..H-1 yield undefined addition. No subtraction operation.

Root report: version1, profile="rfc1982-teaching-v1", status="defined" or
"contains_undefined", has_undefined boolean, rows in input order, limitations exactly
["synthetic_operands_only","pairwise_relation_not_sort_order",
"history_chronology_freshness_authenticity_unverified","not_dns_or_tcp_engine"].
Row fields exactly id,operation,width,modulus,half_range,input,status,reason,
has_undefined,result. input contains only supplied operands (left/right, start/increment,
or start/increments). Row status defined or undefined, reason null or fixed reason.

Compare: distance=(right-left)%M; zero equal; (0,H) less; (H,M) greater; H undefined.
LEFT versus RIGHT naming. Result fields equal boolean, numeric_relation (ordinary
less/equal/greater), serial_relation (less/equal/greater/undefined), forward_distance.
Half case status undefined/reason half_range_comparison, equal=false and known distance.
Other comparisons defined/null reason. has_undefined iff serial relation undefined.

Add: defined iff0<=increment<H. Result fields value,ordinary_sum,wrapped,
relation_to_start; all null for undefined addition/status undefined/reason
increment_outside_rfc_domain. Defined value=(start+n)%M, ordinary_sum=start+n,
wrapped iffsum>=M, relation greater for positive n/equal for0; reason null.

Chain result fields steps,final,increment_sum,ordinary_final,numeric_final_relation,
endpoint_relation,single_addition_of_sum. Steps each index,increment,status,reason,
before,after,wrapped,relation_to_previous,relation_to_start. Defined addition step:
reason null, concrete before/after, wrapped flag, relation_to_previous greater/equal,
relation_to_start evaluated final-LEFT versus original-start-RIGHT, possibly undefined.
Such comparison ambiguity does not stop future steps. Undefined addition step status
undefined/reason increment_outside_rfc_domain; before known, after/wrapped/relations
null. Later steps status not_evaluated/reason prior_undefined_addition; before and all
derived fields null. Original declared increment and index remain visible.
After undefined addition row status undefined/reason undefined_chain_addition and
has_undefined true; all result aggregate fields null except steps. No further sum.
All-valid chain row status defined/reason null, including empty identity. final actual
sequential result; increment_sum exact sum; ordinary_final=start+sum; numeric_final_relation
compares encoded final numerically vsstart; endpoint_relation serial final vsstart.
single_addition_of_sum exactly status/reason/value, defined/null/(start+sum)%M iff
sum<H, otherwise undefined/increment_outside_rfc_domain/null. has_undefined true if
ANY attempted relation or aggregate addition undefined; root aggregates row flags.
Thus defined chain can have has_undefined=true and root contains_undefined/exit3.
No chain collapse, comparator sorting, chronology/epoch inference or maximal serial.

API rejects LabError before return on invalid input or final output cap. Compact ASCII
JSON plus newline <=262144 bytes, no row truncation. CLI exact one argument: `-h` or
`--help` fixed help, `-` stdin or non-leading-hyphen path. Others fixed usage diagnostic
exit2. No argument/paths/input echoed. Help exit0 if delivered; report exit0 defined,
3 contains_undefined; admission/I/O/cap/short-write/flush/diagnostic failures exit2.
Fully check stdout/stderr write counts and flush; detach only failed streams to suppress
shutdown120. Partial sink write can leave bytes; no atomic-delivery promise. API performs
no network/process and file reading only occurs in CLI. Fixed logical limits are not
hard time/RSS containment; other Python/platform/hosted/independent checks unverified.
