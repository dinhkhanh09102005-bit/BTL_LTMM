"""TV5 - unit tests for lex.lex.validation (type and length checks at the API boundary)."""
import unittest

from lex.lex.validation import validate_iv, validate_key


class TestValidation(unittest.TestCase):
    def test_accepts_bytes_like_and_returns_bytes(self):
        raw = bytes(range(16))
        for fn in (validate_key, validate_iv):
            for value in (raw, bytearray(raw), memoryview(raw)):
                with self.subTest(fn=fn.__name__, type=type(value).__name__):
                    out = fn(value)
                    self.assertIs(type(out), bytes)
                    self.assertEqual(out, raw)

    def test_rejects_wrong_types(self):
        for fn in (validate_key, validate_iv):
            for bad in ("0123456789abcdef", 0, 12345, [0] * 16, None, 1.5, (0,) * 16):
                with self.subTest(fn=fn.__name__, value=repr(bad)):
                    with self.assertRaises(TypeError):
                        fn(bad)

    def test_rejects_wrong_lengths(self):
        for fn in (validate_key, validate_iv):
            for n in (0, 1, 15, 17, 24, 32):
                with self.subTest(fn=fn.__name__, n=n):
                    with self.assertRaises(ValueError):
                        fn(bytes(n))

    def test_copy_is_independent_of_mutable_input(self):
        src = bytearray(16)
        out = validate_key(src)
        src[0] = 0xFF
        self.assertEqual(out[0], 0)


if __name__ == "__main__":
    unittest.main()
