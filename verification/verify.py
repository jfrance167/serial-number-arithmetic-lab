"""Repeat owned checks with installed Python/Bandit; no installation or network.

Run: python verification/verify.py from any directory. Inputs: frozen schema/oracles/
examples and own source/tests. Outputs: logs, receipt, stress metrics, latest-run.
Mutants restore exact source in finally; no concurrent edits or forced termination.
Adapted from Jake's verified MIT packet-budget helper; no sibling runtime imports.
"""

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess  # nosec B404: fixed local owned checks, no shell or foreign code.
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "verification"
SOURCE = ROOT / "serial_lab.py"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(name, args):
    child = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True,
                           timeout=60)  # nosec B603: fixed installed Python, owned scripts, no shell.
    (OUT / (name + ".log")).write_bytes(child.stdout + child.stderr)
    return child


def clear_cache():
    for optimization in (None, "1", "2"):
        Path(importlib.util.cache_from_source(str(SOURCE), optimization=optimization)).unlink(missing_ok=True)


def verify():
    frozen = json.loads((OUT / "frozen-contract.json").read_text(encoding="utf-8-sig"))
    for name, expected in frozen["sha256"].items():
        if sha(ROOT / name) != expected:
            raise RuntimeError("frozen contract/oracle mismatch")
    original = SOURCE.read_bytes()
    results = {}
    test_args = ["-B", "-m", "unittest", "discover", "-s", "tests", "-v"]
    mutations = (
        ("half-forced-order", b'if distance == half:\n        return "undefined"',
         b'if distance == half:\n        return "greater"', "test_mandatory_half_boundary"),
        ("increment-half-admitted", b"0 <= increment < modulus // 2", b"0 <= increment <= modulus // 2",
         "test_mandatory_increment_boundary"),
        ("chain-collapsed-to-sum", b"    final = current\n",
         b"    if total >= modulus // 2:\n        return result, False, True\n    final = current\n",
         "test_mandatory_chain_not_single_sum"))
    try:
        for name, old, new, intended in mutations:
            if original.count(old) != 1:
                raise RuntimeError("mutation target must occur exactly once")
            SOURCE.write_bytes(original.replace(old, new))
            clear_cache()
            child = run("mutation-" + name, test_args)
            text = (child.stdout + child.stderr).decode("utf-8", errors="replace")
            assertions = len(re.findall(r"^FAIL: ", text, re.MULTILINE))
            intended_failed = bool(re.search(r"^FAIL: " + re.escape(intended) + r"\b", text, re.MULTILINE))
            results[name] = {"exit": child.returncode, "assertion_failures": assertions,
                             "intended_assertion_failed": intended_failed}
            if child.returncode == 0 or not intended_failed:
                raise RuntimeError("mutation did not trigger its intended assertion")
            SOURCE.write_bytes(original)
    finally:
        SOURCE.write_bytes(original)
        clear_cache()
    for name, args in (("normal", test_args), ("optimized", ["-O", *test_args]),
                       ("compile", ["-m", "compileall", "-q", "serial_lab.py", "tests", "verification/verify.py"]),
                       ("bandit", ["-m", "bandit", "-q", "-r", "serial_lab.py", "tests", "verification/verify.py",
                                   "-f", "json", "-o", str(OUT / "bandit.json")])):
        child = run(name, args)
        results[name] = {"exit": child.returncode}
        if child.returncode:
            raise RuntimeError(name + " failed; see log")
    demos = {}
    for path in sorted((ROOT / "examples").glob("*.json")):
        expected = {"defined": 0, "empty": 0, "mixed": 3, "invalid-late": 2}[path.stem]
        child = run("demo-" + path.stem, [str(SOURCE), str(path)])
        if child.returncode != expected or (expected == 2 and child.stdout):
            raise RuntimeError("demo status/output mismatch")
        report = json.loads(child.stdout) if expected != 2 else None
        demos[path.name] = {"exit": child.returncode, "rows": len(report["rows"]) if report else None,
                            "status": report["status"] if report else None}
    # Largest allocated shape, not a proof of exact serialized maximum.
    sys.path.insert(0, str(ROOT))
    import serial_lab
    cases = [{"id": "X" * 30 + f"{i:02}", "operation": "chain", "width": 32,
              "start": 4294967295, "increments": [2147483647] * 16} for i in range(16)]
    cases += [{"id": "Y" * 30 + f"{i:02}", "operation": "compare", "width": 32,
               "left": 4294967295, "right": 2147483647} for i in range(48)]
    data = json.dumps({"version": 1, "cases": cases}).encode()
    output = serial_lab._encode(serial_lab.analyze(data))
    stress = {"input_bytes": len(data), "output_bytes": len(output), "rows": 64,
              "chain_steps": 256, "output_cap": 262144, "within_cap": len(output) <= 262144}
    (OUT / "output-stress.json").write_text(json.dumps(stress, indent=2) + "\n", encoding="utf-8")
    paths = [SOURCE, ROOT / "tests/test_serial_lab.py", Path(__file__).resolve(), ROOT / "SCHEMA.md",
             ROOT / "tests/hand-oracles.json", OUT / "frozen-contract.json", *sorted((ROOT / "examples").glob("*.json"))]
    receipt = {"python": sys.version, "checks": results, "demos": demos, "stress": stress,
               "frozen_verified": True, "source_restored": SOURCE.read_bytes() == original,
               "sha256": {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p) for p in paths}}
    (OUT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


def main():
    status = OUT / "latest-run.json"
    status.write_text('{"status":"running"}\n', encoding="utf-8")
    try:
        verify()
    except Exception:
        status.write_text('{"status":"failed","prior_receipt_is_historical":true}\n', encoding="utf-8")
        raise
    status.write_text('{"status":"passed"}\n', encoding="utf-8")


if __name__ == "__main__":
    main()
