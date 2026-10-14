"""TV4 - unit tests for lex.lex.extractor (leak positions, order, after-ARK timing).

Expected values come from tests/vectors/reference_trace.json (official LEX-v2 C code).
State convention: bytearray(16), idx = 4*c + r.
"""
import unittest

from lex.lex.extractor import LEAK_INDICES_EVEN, LEAK_INDICES_ODD, extract_leak
from tests.support.kat import load_trace


class TestLeakIndices(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(tuple(LEAK_INDICES_ODD), (10, 2, 8, 0))
        self.assertEqual(tuple(LEAK_INDICES_EVEN), (11, 3, 9, 1))

    def test_position_and_order(self):
        state = bytearray(range(16))                      # state[i] == i
        for r in (1, 3, 5, 7, 9):
            self.assertEqual(extract_leak(state, r), bytes([10, 2, 8, 0]))
        for r in (2, 4, 6, 8, 10):
            self.assertEqual(extract_leak(state, r), bytes([11, 3, 9, 1]))

    def test_returns_four_bytes_and_does_not_mutate(self):
        state = bytearray(range(16)); before = bytes(state)
        out = extract_leak(state, 1)
        self.assertIsInstance(out, bytes); self.assertEqual(len(out), 4)
        self.assertEqual(bytes(state), before)

    def test_invalid_round(self):
        for bad in (0, 11, -1):
            with self.assertRaises(ValueError):
                extract_leak(bytearray(16), bad)


class TestAgainstReferenceTrace(unittest.TestCase):
    def test_every_round_of_every_case(self):
        for case in load_trace()["cases"]:
            for ci, cyc in enumerate(case["cycles"], 1):
                for rd in cyc["rounds"]:
                    with self.subTest(case=case["name"], cycle=ci, round=rd["round"]):
                        state = bytearray.fromhex(rd["state_after_ark"])
                        self.assertEqual(extract_leak(state, rd["round"]).hex().upper(), rd["leak"])


if __name__ == "__main__":
    unittest.main()
