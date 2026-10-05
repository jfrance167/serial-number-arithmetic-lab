"""Bounded invented-number RFC1982 arithmetic; exact contract in SCHEMA.md."""

from __future__ import annotations

import json
import re
import sys

MAX_INPUT = 65536
MAX_OUTPUT = 262144
FIELDS = {"compare": {"left", "right"}, "add": {"start", "increment"},
          "chain": {"start", "increments"}}
LIMITATIONS = ["synthetic_operands_only", "pairwise_relation_not_sort_order",
               "history_chronology_freshness_authenticity_unverified", "not_dns_or_tcp_engine"]
HELP = b"Serial arithmetic teaching lab\nUsage: serial_lab.py SCENARIO | - | --help\nInvented JSON integers only; undefined results exit 3. No ordering/freshness guarantee.\n"
USAGE = "serial-lab: invalid arguments\nUsage: serial_lab.py SCENARIO | - | --help\n"


class LabError(ValueError):
    """Invalid bounded input or failed report delivery; no caller data in errors."""


def _pairs(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise LabError("duplicate JSON key")
        result[key] = value
    return result


def _integer(token: str) -> int:
    if len(token) > 11:
        raise LabError("numeric token exceeds 11 characters")
    return int(token)


def _noninteger(token: str) -> None:
    raise LabError("only integer JSON numbers allowed")


def _strings(value: object) -> None:
    if isinstance(value, str):
        if len(value) > 64 or any(ord(c) < 32 or ord(c) > 126 for c in value):
            raise LabError("strings must be bounded printable ASCII")
    elif isinstance(value, dict):
        for key, child in value.items():
            _strings(key)
            _strings(child)
    elif isinstance(value, list):
        for child in value:
            _strings(child)


def _load(data: bytes) -> object:
    # Owned packet/route-lab pattern. Preflight bounds nesting; json owns grammar.
    if type(data) is not bytes or len(data) > MAX_INPUT:
        raise LabError("input must be exact bytes within 65536 bytes")
    if data.startswith(b"\xef\xbb\xbf"):
        raise LabError("UTF-8 BOM not allowed")
    try:
        text = data.decode("utf-8")
    except UnicodeError as exc:
        raise LabError("input must be UTF-8") from exc
    depth, quoted, escaped = 0, False, False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            if depth > 6:
                raise LabError("JSON nesting exceeds 6")
        elif char in "]}":
            depth -= 1
    try:
        root = json.loads(text, object_pairs_hook=_pairs, parse_int=_integer,
                          parse_float=_noninteger, parse_constant=_noninteger)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise LabError("invalid JSON") from exc
    _strings(root)
    return root


def _fields(value: object, keys: set[str]) -> dict:
    if type(value) is not dict or set(value) != keys:
        raise LabError("invalid, unknown or missing fields")
    return value


def _number(value: object, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise LabError("integer outside profile bounds")
    return value


def _validate(root: object) -> list[dict]:
    root = _fields(root, {"version", "cases"})
    _number(root["version"], 1, 1)
    cases = root["cases"]
    if type(cases) is not list or len(cases) > 64:
        raise LabError("cases must be an array of at most 64")
    ids, count = set(), 0
    for case in cases:
        if type(case) is not dict or type(case.get("operation")) is not str or case["operation"] not in FIELDS:
            raise LabError("unknown operation or invalid case")
        operation = case["operation"]
        _fields(case, {"id", "operation", "width"} | FIELDS[operation])
        label = case["id"]
        if type(label) is not str or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,31}", label):
            raise LabError("invalid fictional ID")
        if label in ids:
            raise LabError("duplicate case ID")
        ids.add(label)
        width = _number(case["width"], 2, 32)
        modulus = 1 << width
        if operation == "compare":
            _number(case["left"], 0, modulus - 1)
            _number(case["right"], 0, modulus - 1)
        else:
            _number(case["start"], 0, modulus - 1)
            if operation == "add":
                _number(case["increment"], -modulus, modulus)
            else:
                values = case["increments"]
                if type(values) is not list or len(values) > 16:
                    raise LabError("chain increments must be an array of at most 16")
                for value in values:
                    _number(value, -modulus, modulus)
                count += len(values)
                if count > 256:
                    raise LabError("total chain steps exceed 256")
    return cases


def _numeric(left: int, right: int) -> str:
    return "less" if left < right else "greater" if left > right else "equal"


def _relation(left: int, right: int, modulus: int) -> str:
    distance = (right - left) % modulus
    half = modulus // 2
    if distance == 0:
        return "equal"
    if distance == half:
        return "undefined"
    return "less" if distance < half else "greater"


def _addition(start: int, increment: int, modulus: int) -> dict:
    if not 0 <= increment < modulus // 2:
        return {"value": None, "ordinary_sum": None, "wrapped": None, "relation_to_start": None}
    total = start + increment
    return {"value": total % modulus, "ordinary_sum": total, "wrapped": total >= modulus,
            "relation_to_start": "greater" if increment else "equal"}


def _chain(case: dict, modulus: int) -> tuple[dict, bool, bool]:
    start, current = case["start"], case["start"]
    steps, ambiguous = [], False
    for index, increment in enumerate(case["increments"]):
        step = {"index": index, "increment": increment, "status": "not_evaluated",
                "reason": "prior_undefined_addition", "before": None, "after": None,
                "wrapped": None, "relation_to_previous": None, "relation_to_start": None}
        if current is not None:
            added = _addition(current, increment, modulus)
            step.update(before=current, after=added["value"], wrapped=added["wrapped"],
                        relation_to_previous=added["relation_to_start"])
            if added["value"] is None:
                step.update(status="undefined", reason="increment_outside_rfc_domain")
            else:
                relation = _relation(added["value"], start, modulus)
                step.update(status="defined", reason=None, relation_to_start=relation)
                ambiguous |= relation == "undefined"
            current = added["value"]
        steps.append(step)
    result = {"steps": steps, "final": None, "increment_sum": None, "ordinary_final": None,
              "numeric_final_relation": None, "endpoint_relation": None, "single_addition_of_sum": None}
    if current is None:
        return result, False, True
    total = sum(case["increments"])
    final = current
    aggregate = _addition(start, total, modulus)
    aggregate_defined = aggregate["value"] is not None
    endpoint = _relation(final, start, modulus)
    result.update(final=final, increment_sum=total, ordinary_final=start + total,
                  numeric_final_relation=_numeric(final, start), endpoint_relation=endpoint,
                  single_addition_of_sum={"status": "defined" if aggregate_defined else "undefined",
                                          "reason": None if aggregate_defined else "increment_outside_rfc_domain",
                                          "value": aggregate["value"]})
    return result, True, ambiguous or endpoint == "undefined" or not aggregate_defined


def _evaluate(case: dict) -> dict:
    operation, modulus = case["operation"], 1 << case["width"]
    defined, ambiguous, reason = True, False, None
    if operation == "compare":
        left, right = case["left"], case["right"]
        relation = _relation(left, right, modulus)
        ambiguous = relation == "undefined"
        defined = not ambiguous
        reason = "half_range_comparison" if ambiguous else None
        result = {"equal": left == right, "numeric_relation": _numeric(left, right),
                  "serial_relation": relation, "forward_distance": (right - left) % modulus}
    elif operation == "add":
        result = _addition(case["start"], case["increment"], modulus)
        defined = result["value"] is not None
        ambiguous = not defined
        reason = None if defined else "increment_outside_rfc_domain"
    else:
        result, defined, ambiguous = _chain(case, modulus)
        reason = None if defined else "undefined_chain_addition"
    return {"id": case["id"], "operation": operation, "width": case["width"],
            "modulus": modulus, "half_range": modulus // 2,
            "input": {key: case[key] for key in sorted(FIELDS[operation])},
            "status": "defined" if defined else "undefined", "reason": reason,
            "has_undefined": ambiguous, "result": result}


def _encode(report: dict) -> bytes:
    encoded = (json.dumps(report, ensure_ascii=True, separators=(",", ":")) + "\n").encode("utf-8")
    if len(encoded) > MAX_OUTPUT:
        raise LabError("serialized output exceeds 262144 bytes")
    return encoded


def analyze(data: bytes) -> dict:
    """Admit all exact JSON bytes, then return bounded invented serial arithmetic.

    LabError rejects invalid input/output size before returning a report. Undefined
    math remains explicit data; neither defined comparisons nor sums prove history.
    """
    cases = _validate(_load(data))
    rows = [_evaluate(case) for case in cases]
    ambiguous = any(row["has_undefined"] for row in rows)
    report = {"version": 1, "profile": "rfc1982-teaching-v1",
              "status": "contains_undefined" if ambiguous else "defined",
              "has_undefined": ambiguous, "rows": rows, "limitations": list(LIMITATIONS)}
    _encode(report)
    return report


def _diagnostic(message: str) -> None:
    try:
        if sys.stderr.write(message) != len(message):
            raise OSError("short diagnostic write")
        sys.stderr.flush()
    except (OSError, ValueError):
        # Failed diagnostics must not become CPython shutdown exit120.
        sys.stderr = None


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1 or (args[0].startswith("-") and args[0] not in ("-", "-h", "--help")):
        _diagnostic(USAGE)
        return 2
    writing = False
    try:
        if args[0] in ("-h", "--help"):
            output, status = HELP, 0
        else:
            if args[0] == "-":
                data = sys.stdin.buffer.read(MAX_INPUT + 1)
            else:
                with open(args[0], "rb") as stream:
                    data = stream.read(MAX_INPUT + 1)
            report = analyze(data)
            output, status = _encode(report), 3 if report["has_undefined"] else 0
        writing = True
        if sys.stdout.buffer.write(output) != len(output):
            raise LabError("short output write")
        sys.stdout.buffer.flush()
        return status
    except (OSError, ValueError) as exc:
        if writing:
            sys.stdout = None
        message = str(exc) if isinstance(exc, LabError) else "input/output operation failed"
        _diagnostic("serial-lab: " + message + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
