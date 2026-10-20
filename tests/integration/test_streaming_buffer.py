"""Independent TV5 test; no implementation required from TV1-TV4."""
import sys
import types
import unittest
from unittest.mock import patch

from lex.lex.keystream import KeystreamBuffer

class Key:
    round_keys = [bytes(16)] * 11

class TestKeystreamBuffer(unittest.TestCase):
    def test_chunks_and_boundaries(self):
        position = [0]
        def fake_cycle(state, keys):
            start = position[0]
            position[0] += 40
            return bytes((start + i) % 256 for i in range(40)), bytearray([position[0] % 256] * 16)

        fake_module = types.ModuleType("lex.lex.round_engine")
        fake_module.lex_cycle = fake_cycle
        with patch.dict(sys.modules, {"lex.lex.round_engine": fake_module}):
            buf = KeystreamBuffer(Key(), bytearray(16))
            self.assertEqual(buf.read(7), bytes(range(7)))
            self.assertEqual(buf.read(10), bytes(range(7,17)))
            self.assertEqual(buf.read(30), bytes(range(17,47)))
            self.assertEqual(len(buf._buf), 33)
            self.assertEqual(buf.read(0), b"")
            self.assertEqual(buf.read(53), bytes(range(47,100)))
            self.assertEqual(len(buf._buf), 20)
            self.assertEqual(position[0], 120)

    def test_bad_requests(self):
        buf = KeystreamBuffer(Key(), bytearray(16))
        for n in (True, 1.5, "5", None):
            with self.subTest(n=n), self.assertRaises(TypeError):
                buf.read(n)
        with self.assertRaises(ValueError):
            buf.read(-1)
        with self.assertRaises(ValueError):
            KeystreamBuffer(Key(), bytearray(15))

if __name__ == "__main__":
    unittest.main()
