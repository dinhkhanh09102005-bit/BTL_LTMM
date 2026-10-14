"""Run the whole suite from the repo root:  python run_tests.py [--fast] [-v]

--fast  skips the 8 long (131072-byte) eSTREAM vectors (use while iterating;
        the acceptance run at gate G4/G6 must be WITHOUT --fast).
Modules that are not implemented yet make their tests ERROR (ImportError) - that is
the expected TDD state, not a bug in the tests.
"""
import argparse
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT / "src")]

ap = argparse.ArgumentParser()
ap.add_argument("--fast", action="store_true")
ap.add_argument("--require-reference-trace", action="store_true",
                help="strict gate G4-G6: vector files must exist, no --fast, no skipped test")
ap.add_argument("-v", "--verbose", action="store_true")
args = ap.parse_args()

if args.require_reference_trace:
    if args.fast:
        sys.exit("--require-reference-trace cannot be combined with --fast")
    for name in ("reference_trace.json", "estream_lex_kat.json"):
        f = ROOT / "tests" / "vectors" / name
        if not f.is_file() or f.stat().st_size == 0:
            sys.exit(f"missing reference fixture: {f}")

suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT))

def flatten(s):
    for t in s:
        yield from flatten(t) if isinstance(t, unittest.TestSuite) else [t]

tests = [t for t in flatten(suite) if not (args.fast and t.id().endswith("test_kat_long"))]
res = unittest.TextTestRunner(verbosity=2 if args.verbose else 1).run(unittest.TestSuite(tests))
if args.require_reference_trace and res.skipped:
    print(f"STRICT GATE FAILED: {len(res.skipped)} skipped test(s)")
    sys.exit(1)
sys.exit(0 if res.wasSuccessful() else 1)
