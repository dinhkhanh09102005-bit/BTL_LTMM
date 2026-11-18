"""TV5 public API contract tests with deterministic TV3/TV4 mocks."""

from __future__ import annotations

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
                self.assertEqual(
                    self.api.decrypt(ZERO, ZERO, encrypted), raw
                )

    def test_streaming_process_equals_one_shot(self):
        raw = bytes(i % 256 for i in range(301))
        expected = self.api.encrypt(ZERO, ZERO, raw)
        session = self.api.LEX(ZERO, ZERO)
        actual = (
            session.process(raw[:39])
            + session.process(raw[39:40])
            + session.process(raw[40:181])
            + session.process(raw[181:])
        )
        self.assertEqual(actual, expected)

    def test_keystream_and_process_share_one_position(self):
        session = self.api.LEX(ZERO, ZERO)
        prefix = session.keystream(7)
        encrypted = session.process(b"AB")
        recovered_stream = bytes(a ^ b for a, b in zip(encrypted, b"AB"))
        self.assertEqual(prefix + recovered_stream, bytes(range(9)))

    def test_sessions_have_independent_positions(self):
        first = self.api.LEX(ZERO, ZERO)
        second = self.api.LEX(ZERO, ZERO)
        self.assertEqual(first.keystream(7), bytes(range(7)))
        self.assertEqual(second.keystream(3), bytes(range(3)))
        self.assertEqual(first.keystream(3), bytes(range(7, 10)))
        self.assertEqual(second.keystream(7), bytes(range(3, 10)))

    def test_empty_operations_do_not_consume_stream(self):
        session = self.api.LEX(ZERO, ZERO)
        self.assertEqual(session.process(b""), b"")
        self.assertEqual(session.keystream(0), b"")
        self.assertEqual(session.keystream(5), bytes(range(5)))

    def test_bytes_like_inputs_are_supported(self):
        ciphertext = self.api.encrypt(
            bytearray(ZERO), memoryview(ZERO), memoryview(b"LEX TV5")
        )
        self.assertIsInstance(ciphertext, bytes)
        self.assertEqual(self.api.decrypt(ZERO, ZERO, ciphertext), b"LEX TV5")

    def test_invalid_inputs_do_not_advance_stream(self):
        session = self.api.LEX(ZERO, ZERO)
        with self.assertRaises(TypeError):
            session.process("not bytes")
        with self.assertRaises(ValueError):
            session.keystream(-1)
        self.assertEqual(session.keystream(6), bytes(range(6)))


if __name__ == "__main__":
    unittest.main()
