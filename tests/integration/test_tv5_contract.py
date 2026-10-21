"""Additional TV5 contract tests independent of unfinished TV1-TV4 modules."""
import importlib
import sys
import unittest
from unittest.mock import patch

from tests.support.mock_lex_dependencies import install_mock_dependencies

ZERO = bytes(16)


class TestTV5PublicContract(unittest.TestCase):
    def setUp(self):
        self.modules = patch.dict(sys.modules, {})
        self.modules.start()
        self.addCleanup(self.modules.stop)
        install_mock_dependencies()
        sys.modules.pop("lex.lex.api", None)
        self.addCleanup(lambda: sys.modules.pop("lex.lex.api", None))
        self.api = importlib.import_module("lex.lex.api")

    def test_roundtrip_multiple_lengths(self):
        for n in (0, 1, 39, 40, 41, 79, 80, 81, 255, 512):
            with self.subTest(length=n):
                raw = bytes(i % 256 for i in range(n))
                encrypted = self.api.encrypt(ZERO, ZERO, raw)
                self.assertEqual(len(encrypted), n)
                self.assertEqual(self.api.decrypt(ZERO, ZERO, encrypted), raw)

    def test_streaming_process_equals_one_shot(self):
        raw = bytes(i % 256 for i in range(301))
        expected = self.api.encrypt(ZERO, ZERO, raw)
        for sizes in ((39, 1, 261), (1, 40, 260), (0, 80, 221)):
            with self.subTest(sizes=sizes):
                session = self.api.LEX(ZERO, ZERO)
                result = bytearray()
                index = 0
                for size in sizes:
                    result.extend(session.process(raw[index:index + size]))
                    index += size
                self.assertEqual(index, len(raw))
                self.assertEqual(bytes(result), expected)

    def test_independent_sessions_have_independent_positions(self):
        first = self.api.LEX(ZERO, ZERO)
        second = self.api.LEX(ZERO, ZERO)
        self.assertEqual(first.keystream(7), bytes(range(7)))
        self.assertEqual(second.keystream(3), bytes(range(3)))
        self.assertEqual(first.keystream(3), bytes(range(7, 10)))
        self.assertEqual(second.keystream(7), bytes(range(3, 10)))

    def test_keystream_consistent_with_encrypting_zero_bytes(self):
        n = 121
        self.assertEqual(
            self.api.LEX(ZERO, ZERO).keystream(n),
            self.api.encrypt(ZERO, ZERO, bytes(n)),
        )

    def test_public_helpers_accept_bytes_like_inputs(self):
        key = bytearray(16)
        iv = memoryview(bytes(16))
        data = memoryview(b"LEX TV5")
        ciphertext = self.api.encrypt(key, iv, data)
        self.assertIsInstance(ciphertext, bytes)
        self.assertEqual(self.api.decrypt(key, iv, ciphertext), b"LEX TV5")

    def test_invalid_inputs_do_not_advance_stream(self):
        obj = self.api.LEX(ZERO, ZERO)
        with self.assertRaises(TypeError):
            obj.process("not bytes")
        with self.assertRaises(ValueError):
            obj.keystream(-1)
        self.assertEqual(obj.keystream(6), bytes(range(6)))


if __name__ == "__main__":
    unittest.main()
