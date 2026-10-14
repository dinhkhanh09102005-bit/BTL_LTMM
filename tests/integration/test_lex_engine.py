"""TV4 - integration tests for lex.lex.round_engine.lex_cycle against the C trace.

Contract: lex_cycle(state: bytearray, round_keys: list[bytes]) -> (keystream40: bytes, next_state: bytearray)
Round keys are taken from the trace (independent of TV3's key schedule).
"""
import unittest

from lex.lex.round_engine import lex_cycle
from tests.support.kat import load_trace


class TestLexCycle(unittest.TestCase):
    def test_cycles_match_reference(self):
        for case in load_trace()["cases"]:
            rks = [bytes.fromhex(k) for k in case["round_keys"]]
            state = bytearray.fromhex(case["s0"])
            for ci, cyc in enumerate(case["cycles"], 1):
                with self.subTest(case=case["name"], cycle=ci):
                    ks, state = lex_cycle(state, rks)
                    self.assertEqual(len(ks), 40)
                    self.assertEqual(ks.hex().upper(), cyc["keystream40"])
                    # S10 (after MixColumns and K10) feeds the next cycle unchanged
                    self.assertEqual(bytes(state).hex().upper(), cyc["rounds"][-1]["state_after_ark"])

    def test_key0_iv0_first_40_bytes(self):
        case = next(c for c in load_trace()["cases"] if c["name"] == "key0_iv0")
        rks = [bytes.fromhex(k) for k in case["round_keys"]]
        ks, _ = lex_cycle(bytearray.fromhex("66E94BD4EF8A2C3B884CFA59CA342B2E"), rks)
        self.assertEqual(ks.hex().upper(),
            "FF27889A64BBC76D9D9548F2E50FCB4F5BC4F94DEDC76FC23347ED94AB279CE4F5F608648D8B5EE8")

    def test_input_state_not_mutated(self):
        case = load_trace()["cases"][0]
        rks = [bytes.fromhex(k) for k in case["round_keys"]]
        state = bytearray.fromhex(case["s0"]); before = bytes(state)
        lex_cycle(state, rks)
        self.assertEqual(bytes(state), before)


if __name__ == "__main__":
    unittest.main()
