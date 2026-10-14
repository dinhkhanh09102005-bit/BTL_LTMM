"""TV6 - integration tests for the public API (lex.lex.api).

Expected keystream comes from tests/vectors/reference_trace.json; a bare
decrypt(encrypt(m)) == m round-trip is NOT accepted as evidence of correctness.
"""
import unittest

from lex.lex.api import LEX, decrypt, encrypt
from tests.support.kat import load_trace

KS40_ZERO = bytes.fromhex(
    "FF27889A64BBC76D9D9548F2E50FCB4F5BC4F94DEDC76FC23347ED94AB279CE4F5F608648D8B5EE8")
K0 = bytes(16)


class TestKeystream(unittest.TestCase):
    def test_first_40_bytes(self):
        self.assertEqual(LEX(K0, K0).keystream(40), KS40_ZERO)

    def test_matches_reference_cycles(self):
        for case in load_trace()["cases"]:
            with self.subTest(case=case["name"]):
                want = b"".join(bytes.fromhex(c["keystream40"]) for c in case["cycles"])
                got = LEX(bytes.fromhex(case["key"]), bytes.fromhex(case["iv"])).keystream(len(want))
                self.assertEqual(got, want)

    def test_zero_length(self):
        self.assertEqual(LEX(K0, K0).keystream(0), b"")

    def test_invalid_length_argument(self):
        c = LEX(K0, K0)
        with self.assertRaises(ValueError):
            c.keystream(-1)
        for bad in (1.5, "4", None):
            with self.assertRaises(TypeError):
                c.keystream(bad)


class TestProcess(unittest.TestCase):
    def test_encrypt_is_xor_with_reference_keystream(self):
        pt = bytes(range(40))
        want = bytes(a ^ b for a, b in zip(pt, KS40_ZERO))
        self.assertEqual(encrypt(K0, K0, pt), want)
        self.assertEqual(decrypt(K0, K0, want), pt)

    def test_accepts_bytes_like(self):
        pt = bytes(range(10))
        ref = encrypt(K0, K0, pt)
        self.assertEqual(encrypt(bytearray(K0), memoryview(K0), bytearray(pt)), ref)
        self.assertEqual(encrypt(K0, K0, memoryview(pt)), ref)

    def test_empty_message(self):
        self.assertEqual(encrypt(K0, K0, b""), b"")

    def test_split_calls_equal_single_call(self):
        pt = bytes(range(256)) * 2
        one = LEX(K0, K0).process(pt)
        c = LEX(K0, K0)
        parts = b"".join(c.process(pt[i:j]) for i, j in ((0, 1), (1, 8), (8, 100), (100, 101), (101, 512)))
        self.assertEqual(parts, one)

    def test_rejects_bad_inputs(self):
        with self.assertRaises(TypeError):
            LEX("0123456789abcdef", K0)
        with self.assertRaises(TypeError):
            LEX(K0, 0)
        with self.assertRaises(ValueError):
            LEX(bytes(15), K0)
        with self.assertRaises(ValueError):
            LEX(K0, bytes(17))
        with self.assertRaises(TypeError):
            encrypt(K0, K0, "text")

    def test_different_iv_gives_different_stream(self):
        iv2 = bytes(15) + b"\x01"
        self.assertNotEqual(LEX(K0, K0).keystream(40), LEX(K0, iv2).keystream(40))


if __name__ == "__main__":
    unittest.main()
