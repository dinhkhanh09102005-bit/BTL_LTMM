"""TV4 - tính chất của lex_round / lex_cycle độc lập với trace C."""
import unittest

from lex.aes.key_schedule import expand_key
from lex.aes.transforms import add_round_key, mix_columns, shift_rows, sub_bytes
from lex.lex.round_engine import KEYSTREAM_BYTES_PER_CYCLE, lex_cycle, lex_round

RK = expand_key(bytes(range(16)))
S = bytearray(range(16, 32))


class TestLexRound(unittest.TestCase):
    def test_with_mix_columns_is_aes_round(self):
        want = add_round_key(mix_columns(shift_rows(sub_bytes(S))), RK[3])
        self.assertEqual(lex_round(S, RK[3], mix_columns=True), want)

    def test_without_mix_columns_is_aes_last_round(self):
        want = add_round_key(shift_rows(sub_bytes(S)), RK[3])
        self.assertEqual(lex_round(S, RK[3], mix_columns=False), want)

    def test_flag_changes_result(self):
        self.assertNotEqual(lex_round(S, RK[3], mix_columns=True), lex_round(S, RK[3], mix_columns=False))

    def test_does_not_mutate(self):
        before = bytes(S)
        lex_round(S, RK[1], mix_columns=True)
        self.assertEqual(bytes(S), before)


class TestLexCycle(unittest.TestCase):
    def test_output_sizes(self):
        ks, s10 = lex_cycle(S, RK)
        self.assertEqual(len(ks), KEYSTREAM_BYTES_PER_CYCLE)
        self.assertEqual(KEYSTREAM_BYTES_PER_CYCLE, 40)
        self.assertEqual(len(s10), 16)

    def test_all_ten_rounds_have_mix_columns_and_no_k0(self):
        state = bytearray(S)
        for r in range(1, 11):
            state = add_round_key(mix_columns(shift_rows(sub_bytes(state))), RK[r])
        self.assertEqual(lex_cycle(S, RK)[1], state)

    def test_chaining_is_deterministic_and_state_feeds_forward(self):
        ks1, s10 = lex_cycle(S, RK)
        ks2, _ = lex_cycle(s10, RK)
        self.assertNotEqual(ks1, ks2)
        self.assertEqual(lex_cycle(s10, RK)[0], ks2)

    def test_requires_eleven_round_keys(self):
        with self.assertRaises(ValueError):
            lex_cycle(S, RK[:10])


if __name__ == "__main__":
    unittest.main()
