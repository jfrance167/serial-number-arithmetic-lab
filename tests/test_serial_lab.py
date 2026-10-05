"""Independent literals/path oracles and bounded admission/delivery regressions."""

import io
import json
from pathlib import Path
import socket
import subprocess  # nosec B404: fixed local owned Python test children, no shell.
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import serial_lab as lab


def raw(cases):
    return json.dumps({"version": 1, "cases": cases}).encode()


def compare(left=0, right=1, width=8, label="c"):
    return {"id": label, "operation": "compare", "width": width, "left": left, "right": right}


def add(start=0, increment=1, width=8, label="a"):
    return {"id": label, "operation": "add", "width": width, "start": start, "increment": increment}


def chain(start=0, increments=(), width=8, label="s"):
    return {"id": label, "operation": "chain", "width": width, "start": start, "increments": list(increments)}


def row(case):
    return lab.analyze(raw([case]))["rows"][0]


def inequality_oracle(left, right, width):
    """RFC integer inequalities, deliberately not production modular distance."""
    half = 2 ** (width - 1)
    if left == right:
        return "equal"
    if (left < right and right - left < half) or (left > right and left - right > half):
        return "less"
    if (left < right and right - left > half) or (left > right and left - right < half):
        return "greater"
    return "undefined"


class Sink:
    def __init__(self, mode="ok"):
        self.buffer = self
        self.mode = mode
        self.data = []

    def write(self, value):
        self.data.append(value)
        if self.mode == "closed":
            raise BrokenPipeError()
        return len(value) - 1 if self.mode == "short" else len(value)

    def flush(self):
        if self.mode == "flush":
            raise BrokenPipeError()


class ArithmeticTests(unittest.TestCase):
    def test_precode_hand_oracles(self):
        oracles = json.loads((ROOT / "tests/hand-oracles.json").read_text())
        self.assertEqual(len(oracles), 20)
        for expected in oracles:
            with self.subTest(case=expected["case"]["id"]):
                actual = row(expected["case"])
                for key in ("status", "has_undefined", "result"):
                    self.assertEqual(actual[key], expected[key])

    def test_all_small_pairs_independent_inequalities(self):
        for width in range(2, 6):
            for left in range(2 ** width):
                for right in range(2 ** width):
                    actual = row(compare(left, right, width))["result"]
                    expected = inequality_oracle(left, right, width)
                    self.assertEqual(actual["serial_relation"], expected, (width, left, right))
                    self.assertEqual(actual["equal"], left == right)

    def test_small_additions_enumerated_successor_paths(self):
        for width in range(2, 6):
            cycle = list(range(2 ** width))
            for start in cycle:
                path = cycle[start:] + cycle[:start]
                for increment in range(len(cycle) // 2):
                    actual = row(add(start, increment, width))
                    self.assertEqual(actual["result"]["value"], path[increment])
                    self.assertEqual(actual["status"], "defined")
                for increment in (-len(cycle), -1, len(cycle) // 2, len(cycle) - 1, len(cycle)):
                    self.assertEqual(row(add(start, increment, width))["status"], "undefined")

    def test_mandatory_half_boundary(self):
        self.assertEqual(row(compare(0, 128))["result"]["serial_relation"], "undefined")
        self.assertEqual(row(compare(128, 0))["result"]["serial_relation"], "undefined")

    def test_mandatory_increment_boundary(self):
        self.assertEqual(row(add(0, 127))["result"]["value"], 127)
        self.assertEqual(row(add(0, 128))["status"], "undefined")

    def test_mandatory_chain_not_single_sum(self):
        value = row(chain(100, [100, 100]))
        self.assertEqual(value["status"], "defined")
        self.assertEqual(value["result"]["final"], 44)
        self.assertEqual(value["result"]["single_addition_of_sum"]["status"], "undefined")

    def test_comparison_ambiguity_continues_chain(self):
        value = row(chain(0, [64, 64, 1]))
        self.assertEqual(value["status"], "defined")
        self.assertEqual([s["after"] for s in value["result"]["steps"]], [64, 128, 129])
        self.assertEqual([s["relation_to_start"] for s in value["result"]["steps"]],
                         ["greater", "undefined", "less"])
        self.assertTrue(value["has_undefined"])

    def test_undefined_addition_stops_without_sum(self):
        value = row(chain(3, [2, 1, 1], 2))["result"]
        self.assertEqual([s["status"] for s in value["steps"]],
                         ["undefined", "not_evaluated", "not_evaluated"])
        self.assertEqual(value["steps"][0]["before"], 3)
        self.assertIsNone(value["steps"][1]["before"])
        for key in ("final", "increment_sum", "ordinary_final", "numeric_final_relation",
                    "endpoint_relation", "single_addition_of_sum"):
            self.assertIsNone(value[key])

    def test_cycle_is_not_sort_order(self):
        for left, right in ((0, 100), (100, 200), (200, 0)):
            self.assertEqual(row(compare(left, right))["result"]["serial_relation"], "less")

    def test_width32_limits_and_domain(self):
        self.assertEqual(row(add(4294967295, 2147483647, 32))["result"]["value"], 2147483646)
        for increment in (-4294967296, 2147483648, 4294967296):
            self.assertEqual(row(add(0, increment, 32))["status"], "undefined")
        self.assertEqual(row(compare(0, 2147483648, 32))["status"], "undefined")

    def test_every_admitted_width_half_and_wrap(self):
        for width in range(2, 33):
            modulus, half = 2 ** width, 2 ** (width - 1)
            self.assertEqual(row(add(modulus - 1, 1, width))["result"]["value"], 0)
            for right, expected in ((half - 1, "less"), (half, "undefined"), (half + 1, "greater")):
                self.assertEqual(row(compare(0, right, width))["result"]["serial_relation"], expected)

    def test_defined_chain_and_root_flags_separate(self):
        value = lab.analyze(raw([chain(0, [1, 1, 1, 1], 2)]))
        self.assertEqual(value["rows"][0]["status"], "defined")
        self.assertEqual(value["rows"][0]["result"]["final"], 0)
        self.assertTrue(value["rows"][0]["has_undefined"])
        self.assertEqual(value["status"], "contains_undefined")

    def test_empty_identity_and_input_order(self):
        self.assertFalse(lab.analyze(raw([]))["has_undefined"])
        self.assertEqual(row(chain(255))["result"]["final"], 255)
        cases = [compare(label="Z"), add(label="a"), chain(label="A")]
        self.assertEqual([r["id"] for r in lab.analyze(raw(cases))["rows"]], ["Z", "a", "A"])


class AdmissionTests(unittest.TestCase):
    def bad(self, data):
        with self.assertRaises(lab.LabError):
            lab.analyze(data)

    def test_exact_bytes_utf8_bom(self):
        for value in ("{}", bytearray(raw([])), memoryview(raw([])), None, b"\xff", b"\xef\xbb\xbf" + raw([]),
                      b" \xef\xbb\xbf" + raw([])):
            self.bad(value)

    def test_negative_zero_and_unknown_version(self):
        self.assertEqual(row(add(0, 0))["result"]["value"], 0)
        value = raw([add()]).replace(b'"increment": 1', b'"increment": -0')
        self.assertEqual(lab.analyze(value)["rows"][0]["input"]["increment"], 0)
        for version in (0, 2, True, "1", None):
            self.bad(json.dumps({"version": version, "cases": []}).encode())

    def test_json_ambiguity_numbers_grammar(self):
        for value in (b'{"version":1,"version":1,"cases":[]}',
                      b'{"version":1,"versi\\u006fn":1,"cases":[]}',
                      b'{"version":1.0,"cases":[]}', b'{"version":1e0,"cases":[]}',
                      b'{"version":NaN,"cases":[]}', b'{"version":Infinity,"cases":[]}',
                      b'{"version":100000000000,"cases":[]}', b'{}{}', b'{', b'[]', b'null'):
            self.bad(value)

    def test_raw_depth_string_caps(self):
        empty = raw([])
        self.assertEqual(lab.analyze(empty + b" " * (65536 - len(empty)))["rows"], [])
        self.bad(empty + b" " * (65537 - len(empty)))
        with self.assertRaisesRegex(lab.LabError, "nesting"):
            lab.analyze(b"[" * 7 + b"0" + b"]" * 7)
        for label in ("x" * 65, "\n", "\x7f", "é", "\ud800"):
            self.bad(raw([compare(label=label)]))
        # Brackets within a quoted string do not create nesting; string guard wins.
        with self.assertRaisesRegex(lab.LabError, "strings"):
            lab.analyze(b'{"version":1,"cases":[],"x":"[[[[[[[\\\"' + b'x' * 65 + b'"}')

    def test_types_width_encoded_increment_domain(self):
        for width in (True, 1, 33, 1000000000, "8", None):
            self.bad(raw([compare(width=width)]))
        for operand in (-1, 256, True, "1", 1.5, None):
            self.bad(raw([compare(left=operand)]))
            self.bad(raw([compare(right=operand)]))
            self.bad(raw([add(start=operand)]))
        for increment in (-257, 257, True, "0", None):
            self.bad(raw([add(increment=increment)]))
            self.bad(raw([chain(increments=[increment])]))

    def test_fields_labels_duplicates_counts(self):
        for label in ("", "-x", "x_", "x" * 33):
            self.bad(raw([compare(label=label)]))
        self.assertEqual(row(compare(label="A-"))["id"], "A-")
        self.bad(raw([compare(), compare()]))
        for op in ("sort", True, None):
            value = compare()
            value["operation"] = op
            self.bad(raw([value]))
        for mutate in (lambda c: c.pop("right"), lambda c: c.update(extra=1)):
            value = compare()
            mutate(value)
            self.bad(raw([value]))
        self.bad(raw([compare(label=str(i)) for i in range(65)]))
        self.bad(raw([chain(increments=[0] * 17)]))
        self.bad(raw([chain(increments=[0] * 16, label=str(i)) for i in range(17)]))
        for values in (None, "", True, {}):
            value = chain()
            value["increments"] = values
            self.bad(raw([value]))

    def test_common_admission_before_undefined_and_priority(self):
        with patch.object(lab, "_evaluate", side_effect=AssertionError("must not evaluate")):
            self.bad(raw([compare(0, 128), add(width=True)]))
        with self.assertRaisesRegex(lab.LabError, "unknown operation"):
            lab.analyze(raw([{"operation": "sort", "width": True}]))
        with self.assertRaisesRegex(lab.LabError, "duplicate case"):
            lab.analyze(raw([compare(), compare(width=True)]))
        with self.assertRaisesRegex(lab.LabError, "numeric token"):
            lab.analyze(b'{"version":100000000000,"cases":[]}')

    def test_output_cap_seam_and_max_shape(self):
        with patch.object(lab, "MAX_OUTPUT", 1):
            self.bad(raw([]))
        cases = [chain(4294967295, [2147483647] * 16, 32, "X" * 30 + f"{i:02}") for i in range(16)]
        cases += [compare(4294967295, 2147483647, 32, "Y" * 30 + f"{i:02}") for i in range(48)]
        output = lab._encode(lab.analyze(raw(cases)))
        self.assertLessEqual(len(output), 262144)
        self.assertEqual(len(json.loads(output)["rows"]), 64)

    def test_forbidden_capabilities_exercised(self):
        with patch.object(socket, "socket", side_effect=AssertionError("network")), \
             patch.object(socket, "getaddrinfo", side_effect=AssertionError("DNS")), \
             patch.object(subprocess, "Popen", side_effect=AssertionError("process")):
            self.assertEqual(row(chain(100, [100, 100]))["result"]["final"], 44)


class DeliveryTests(unittest.TestCase):
    def invoke(self, args, payload=b"", out_mode="ok", err_mode="ok"):
        stdout, stderr = Sink(out_mode), Sink(err_mode)
        with patch.object(sys, "stdout", stdout), patch.object(sys, "stderr", stderr), \
             patch.object(sys, "stdin", type("Input", (), {"buffer": io.BytesIO(payload)})()):
            status = lab.main(args)
        return status, stdout, stderr

    def test_help_usage_fixed_and_no_echo(self):
        for flag in ("-h", "--help"):
            status, out, err = self.invoke([flag])
            self.assertEqual(status, 0)
            self.assertEqual(out.data, [lab.HELP])
            self.assertEqual(err.data, [])
        for args in ([], ["--PRIVATE-MARKER"], ["PRIVATE-MARKER", "OTHER"]):
            status, out, err = self.invoke(args)
            self.assertEqual(status, 2)
            self.assertEqual(out.data, [])
            self.assertEqual(err.data, [lab.USAGE])

    def test_short_flush_closed_stdout_and_diagnostic_seams(self):
        for args, payload in ((["--help"], b""), (["-"], raw([])), (["-"], raw([compare(0, 128)]))):
            for mode in ("short", "flush", "closed"):
                for err_mode in ("ok", "short", "flush", "closed"):
                    with self.subTest(args=args, mode=mode, err=err_mode):
                        self.assertEqual(self.invoke(args, payload, mode, err_mode)[0], 2)
        for args, payload in ((["--bad"], b""), ([], b""), (["-"], b"{}")):
            for err_mode in ("short", "flush", "closed"):
                self.assertEqual(self.invoke(args, payload, err_mode=err_mode)[0], 2)

    def test_cli_demos_stdin_missing_and_optimized(self):
        for optimized in (False, True):
            command = [sys.executable, *( ["-O"] if optimized else []), str(ROOT / "serial_lab.py")]
            for name, expected in (("defined", 0), ("mixed", 3), ("empty", 0), ("invalid-late", 2)):
                child = subprocess.run([*command, str(ROOT / "examples" / (name + ".json"))],
                                       capture_output=True, timeout=10)  # nosec B603: fixed owned CLI/examples.
                self.assertEqual(child.returncode, expected)
                self.assertEqual(bool(child.stdout), expected != 2)
            child = subprocess.run([*command, "-"], input=raw([]), capture_output=True,
                                   timeout=10)  # nosec B603: fixed owned CLI, bounded synthetic stdin.
            self.assertEqual(child.returncode, 0)
            child = subprocess.run([*command, str(ROOT / "PRIVATE-MISSING-FIXTURE")],
                                   capture_output=True, timeout=10)  # nosec B603: fixed nonexistent own test path.
            self.assertEqual(child.returncode, 2)
            self.assertNotIn(b"PRIVATE-MISSING-FIXTURE", child.stderr)

    def test_actual_children_short_flush_diagnostics(self):
        # Bounded stream seams inside actual normal/-O interpreters, not OS short writes.
        bootstrap = "import sys;sys.path.insert(0,sys.argv[1]);from test_serial_lab import Sink;import serial_lab;sys.stdout=Sink(sys.argv[2]);sys.stderr=Sink(sys.argv[3]);raise SystemExit(serial_lab.main(sys.argv[4:]))"
        for optimized in (False, True):
            for args, out_mode, err_mode in ((["--help"], "short", "ok"), (["--help"], "flush", "ok"),
                                            (["--help"], "short", "short"), (["--help"], "flush", "flush"),
                                            (["--bad-PRIVATE"], "ok", "short"), ([], "ok", "flush"),
                                            ([str(ROOT / "examples/empty.json")], "short", "ok"),
                                            ([str(ROOT / "examples/mixed.json")], "flush", "flush")):
                child = subprocess.run([sys.executable, *( ["-O"] if optimized else []), "-c", bootstrap,
                                        str(ROOT / "tests"), out_mode, err_mode, *args], capture_output=True,
                                       timeout=10)  # nosec B603: fixed owned test sink/module, no shell.
                self.assertEqual(child.returncode, 2, (optimized, args, out_mode, err_mode))
                self.assertEqual(child.stdout, b"")
                self.assertEqual(child.stderr, b"")

    def test_actual_locally_closed_python_streams(self):
        bootstrap = "import sys;sys.path.insert(0,sys.argv[1]);import serial_lab;streams=sys.argv[2];[getattr(sys,name).close() for name in streams.split(',')];raise SystemExit(serial_lab.main(sys.argv[3:]))"
        for optimized in (False, True):
            for streams, args in (("stdout", ["--help"]), ("stderr", ["--bad"]),
                                  ("stdout,stderr", ["--help"]), ("stderr", []), ("stdin", ["-"])):
                child = subprocess.run([sys.executable, *( ["-O"] if optimized else []), "-c", bootstrap,
                                        str(ROOT), streams, *args], capture_output=True,
                                       timeout=10)  # nosec B603: fixed owned CLI and local stream-closure control.
                self.assertEqual(child.returncode, 2, (optimized, streams, args))
                self.assertEqual(child.stdout, b"")
                self.assertNotIn(b"Traceback", child.stderr)

    def test_actual_barrier_closed_sinks_normal_optimized(self):
        # Input barrier ensures pipes close before any help/usage/report/error output.
        bootstrap = "import sys;sys.path.insert(0,sys.argv[1]);import serial_lab;sys.stdin.buffer.read(1);raise SystemExit(serial_lab.main(sys.argv[2:]))"
        for optimized in (False, True):
            for args, payload, close_out, close_err in (
                (["--help"], b"", True, False), (["--help"], b"", True, True),
                (["--bad-PRIVATE-MARKER"], b"", False, True), ([], b"", True, True),
                (["-"], raw([]), True, False), (["-"], raw([compare(0, 128)]), True, True),
                (["-"], b"{}", False, True), ([str(ROOT / "MISSING-PRIVATE-MARKER")], b"", True, True)):
                command = [sys.executable, *( ["-O"] if optimized else []), "-c", bootstrap, str(ROOT), *args]
                child = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)  # nosec B603: fixed owned module/barrier, no shell.
                try:
                    if close_out:
                        child.stdout.close()
                    if close_err:
                        child.stderr.close()
                    child.stdin.write(b"!" + payload)
                    child.stdin.close()
                    self.assertEqual(child.wait(timeout=10), 2, (optimized, args, close_out, close_err))
                    if not close_out:
                        self.assertEqual(child.stdout.read(), b"")
                    if not close_err:
                        self.assertNotIn(b"PRIVATE-MARKER", child.stderr.read())
                finally:
                    if child.poll() is None:
                        child.kill()
                        child.wait(timeout=10)
                    for stream in (child.stdin, child.stdout, child.stderr):
                        stream.close()


if __name__ == "__main__":
    unittest.main()
