"""TV1 - flat 16-byte column-major state: idx = 4*c + r (conventions.md)."""
import unittest

from lex.core.matrix_state import bytes_to_state, get, idx, state_to_bytes


class TestMatrixState(unittest.TestCase):
    def test_idx_column_major(self):
        self.assertEqual(idx(0, 0), 0)
        self.assertEqual(idx(1, 0), 1)       # next row = next byte
        self.assertEqual(idx(0, 1), 4)       # next column = +4
        self.assertEqual(idx(3, 3), 15)
        self.assertEqual(sorted(idx(r, c) for r in range(4) for c in range(4)), list(range(16)))

    def test_get_matches_idx(self):
        s = bytearray(range(16))
        for r in range(4):
            for c in range(4):
                self.assertEqual(get(s, r, c), 4 * c + r)

    def test_roundtrip_and_types(self):
        raw = bytes(range(16))
        s = bytes_to_state(raw)
        self.assertIsInstance(s, bytearray)
        self.assertEqual(state_to_bytes(s), raw)
        self.assertIs(type(state_to_bytes(s)), bytes)

    def test_copy_not_alias(self):
        src = bytearray(range(16))
        s = bytes_to_state(src)
        src[0] = 0xFF
        self.assertEqual(s[0], 0)

    def test_wrong_length(self):
        for n in (0, 15, 17, 32):
            with self.assertRaises(ValueError):
                bytes_to_state(bytes(n))


if __name__ == "__main__":
    unittest.main()
