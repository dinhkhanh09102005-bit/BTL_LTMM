"""TV3 - key schedule and standard AES-128 (last round WITHOUT MixColumns).
All vectors from NIST FIPS-197 (Appendix A.1, B, C.1): independent of the LEX C code."""
import unittest

from lex.aes.key_schedule import expand_key
from lex.aes.standard_aes import encrypt_block

H = bytes.fromhex
KEY_B = H("2b7e151628aed2a6abf7158809cf4f3c")
KEY_C = H("000102030405060708090a0b0c0d0e0f")


class TestExpandKey(unittest.TestCase):
    def test_shape(self):
        rk = expand_key(KEY_B)
        self.assertEqual(len(rk), 11)
        self.assertTrue(all(isinstance(k, bytes) and len(k) == 16 for k in rk))
        self.assertEqual(rk[0], KEY_B)

    def test_fips197_appendix_a1(self):
        rk = expand_key(KEY_B)
        self.assertEqual(rk[1], H("a0fafe1788542cb123a339392a6c7605"))
        self.assertEqual(rk[10], H("d014f9a8c9ee2589e13f0cc8b6630ca6"))

    def test_fips197_appendix_c1(self):
        rk = expand_key(KEY_C)
        self.assertEqual(rk[1], H("d6aa74fdd2af72fadaa678f1d6ab76fe"))
        self.assertEqual(rk[10], H("13111d7fe3944a17f307a78b4d2b30c5"))

    def test_zero_key(self):
        self.assertEqual(expand_key(bytes(16))[1], H("62636363626363636263636362636363"))

    def test_bad_length(self):
        for n in (0, 15, 17, 24, 32):
            with self.assertRaises(ValueError):
                expand_key(bytes(n))


class TestEncryptBlock(unittest.TestCase):
    def test_fips197_appendix_b(self):
        self.assertEqual(encrypt_block(expand_key(KEY_B), H("3243f6a8885a308d313198a2e0370734")),
                         H("3925841d02dc09fbdc118597196a0b32"))

    def test_fips197_appendix_c1(self):
        self.assertEqual(encrypt_block(expand_key(KEY_C), H("00112233445566778899aabbccddeeff")),
                         H("69c4e0d86a7b0430d8cdb78070b4c55a"))

    def test_zero_key_zero_block(self):               # also S0 of LEX for Key=0, IV=0
        self.assertEqual(encrypt_block(expand_key(bytes(16)), bytes(16)),
                         H("66e94bd4ef8a2c3b884cfa59ca342b2e"))

    def test_returns_bytes_and_does_not_mutate(self):
        rk = expand_key(KEY_C); blk = bytearray(16)
        out = encrypt_block(rk, bytes(blk))
        self.assertIs(type(out), bytes)
        self.assertEqual(len(out), 16)
        self.assertEqual(rk, expand_key(KEY_C))


if __name__ == "__main__":
    unittest.main()
