"""TV5 - integration tests for lex.lex.context / lex.lex.iv_setup.

S0 = AES-128_K(swap32(IV)); no leak is extracted in this phase.
Expected values come from tests/vectors/reference_trace.json (official LEX-v2 C code).
"""
import dataclasses
import unittest

from lex.lex.context import KeyContext
from lex.lex.iv_setup import compute_s0, make_key_context
from tests.support.kat import load_trace


def swap32(b: bytes) -> bytes:
    return b"".join(b[i:i + 4][::-1] for i in range(0, 16, 4))


class TestKeyContext(unittest.TestCase):
    def test_round_keys_shape(self):
        ctx = make_key_context(bytes(16))
        self.assertIsInstance(ctx, KeyContext)
        self.assertEqual(len(ctx.round_keys), 11)
        self.assertTrue(all(len(k) == 16 for k in ctx.round_keys))
        self.assertEqual(ctx.round_keys[0], bytes(16))
        self.assertEqual(ctx.round_keys[1].hex().upper(), "62636363626363636263636362636363")

    def test_context_is_immutable(self):
        ctx = make_key_context(bytes(16))
        with self.assertRaises(dataclasses.FrozenInstanceError):
            ctx.round_keys = ()


class TestComputeS0(unittest.TestCase):
    def test_all_zero(self):
        s0 = compute_s0(make_key_context(bytes(16)), bytes(16))
        self.assertEqual(bytes(s0).hex().upper(), "66E94BD4EF8A2C3B884CFA59CA342B2E")

    def test_matches_reference_for_all_cases(self):
        for case in load_trace()["cases"]:
            with self.subTest(case=case["name"]):
                ctx = make_key_context(bytes.fromhex(case["key"]))
                s0 = compute_s0(ctx, bytes.fromhex(case["iv"]))
                self.assertEqual(bytes(s0).hex().upper(), case["s0"])

    def test_iv_word_swap_is_applied(self):
        # An all-zero IV cannot reveal a missing swap; this IV can.
        key = bytes(16)
        iv = bytes.fromhex("00112233445566778899AABBCCDDEEFF")
        ctx = make_key_context(key)
        with_swap = compute_s0(ctx, iv)
        no_swap_input = compute_s0(ctx, swap32(iv))       # what a missing swap would have produced for iv
        self.assertNotEqual(bytes(with_swap), bytes(no_swap_input))
        case = next(c for c in load_trace()["cases"] if c["name"] == "iv_byte_order_probe")
        self.assertEqual(case["aes_input_block"], swap32(iv).hex().upper())
        self.assertEqual(bytes(with_swap).hex().upper(), case["s0"])

    def test_does_not_mutate_inputs_and_returns_16_bytes(self):
        ctx = make_key_context(bytes(range(16)))
        iv = bytearray(range(16)); before = bytes(iv)
        s0 = compute_s0(ctx, iv)
        self.assertEqual(len(s0), 16)
        self.assertEqual(bytes(iv), before)


if __name__ == "__main__":
    unittest.main()
