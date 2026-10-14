"""TV2 - SBOX and the four AES transforms.
Expected values: FIPS-197 Appendix C.1, round 1 (input 00102030...f0 after AddRoundKey K0)."""
import unittest

from lex.aes.sbox import SBOX
from lex.aes.transforms import add_round_key, mix_columns, shift_rows, sub_bytes

H = bytes.fromhex
R1_START = H("00102030405060708090a0b0c0d0e0f0")
R1_SBOX = H("63cab7040953d051cd60e0e7ba70e18c")
R1_SROW = H("6353e08c0960e104cd70b751bacad0e7")
R1_MCOL = H("5f72641557f5bc92f7be3b291db9f91a")
R1_KEY = H("d6aa74fdd2af72fadaa678f1d6ab76fe")
R1_NEXT = H("89d810e8855ace682d1843d8cb128fe4")


class TestSbox(unittest.TestCase):
    def test_shape_and_known_entries(self):
        self.assertEqual(len(SBOX), 256)
        self.assertEqual(sorted(SBOX), list(range(256)))          # permutation
        self.assertEqual((SBOX[0x00], SBOX[0x01], SBOX[0x53], SBOX[0xFF]), (0x63, 0x7C, 0xED, 0x16))

    def test_no_fixed_points(self):
        self.assertTrue(all(SBOX[i] != i and SBOX[i] != i ^ 0xFF for i in range(256)))


class TestTransforms(unittest.TestCase):
    def test_sub_bytes(self):
        self.assertEqual(bytes(sub_bytes(bytearray(R1_START))), R1_SBOX)

    def test_shift_rows(self):
        self.assertEqual(bytes(shift_rows(bytearray(R1_SBOX))), R1_SROW)

    def test_shift_rows_direction_by_index(self):
        out = shift_rows(bytearray(range(16)))
        # row r moves left by r columns: new[r, c] = old[r, (c + r) % 4]
        for r in range(4):
            for c in range(4):
                self.assertEqual(out[4 * c + r], 4 * ((c + r) % 4) + r)

    def test_mix_columns(self):
        self.assertEqual(bytes(mix_columns(bytearray(R1_SROW))), R1_MCOL)

    def test_mix_columns_fips_columns(self):                 # well-known single-column vectors
        for col, want in (("db135345", "8e4da1bc"), ("f20a225c", "9fdc589d"),
                          ("01010101", "01010101"), ("c6c6c6c6", "c6c6c6c6"),
                          ("d4d4d4d5", "d5d5d7d6"), ("2d26314c", "4d7ebdf8")):
            with self.subTest(col=col):
                self.assertEqual(bytes(mix_columns(bytearray(H(col) * 4)))[:4], H(want))

    def test_add_round_key(self):
        self.assertEqual(bytes(add_round_key(bytearray(R1_MCOL), R1_KEY)), R1_NEXT)

    def test_add_round_key_is_involution(self):
        s = bytearray(R1_START)
        self.assertEqual(add_round_key(add_round_key(s, R1_KEY), R1_KEY), s)

    def test_add_round_key_bad_key_length(self):
        for n in (0, 15, 17):
            with self.assertRaises(ValueError):
                add_round_key(bytearray(16), bytes(n))

    def test_pure_functions_do_not_mutate(self):
        for fn in (sub_bytes, shift_rows, mix_columns):
            s = bytearray(R1_START); before = bytes(s)
            fn(s)
            self.assertEqual(bytes(s), before, fn.__name__)
        s = bytearray(R1_START); before = bytes(s)
        add_round_key(s, R1_KEY)
        self.assertEqual(bytes(s), before)

    def test_outputs_are_16_byte_bytearrays(self):
        for out in (sub_bytes(bytearray(16)), shift_rows(bytearray(16)),
                    mix_columns(bytearray(16)), add_round_key(bytearray(16), bytes(16))):
            self.assertIsInstance(out, bytearray)
            self.assertEqual(len(out), 16)


if __name__ == "__main__":
    unittest.main()
