"""Bai 5: test loi va ranh gioi cho TV5; TV3/TV4 van la mock."""
import importlib
import sys
import types
import unittest
from unittest.mock import patch

from lex.lex.keystream import KeystreamBuffer
from tests.support.mock_lex_dependencies import install_mock_dependencies


class FakeKeyContext:
    round_keys = [bytes(16)] * 11


def engine_module(cycle):
    module = types.ModuleType("lex.lex.round_engine")
    module.lex_cycle = cycle
    return module


class TestBufferErrorsAndBoundaries(unittest.TestCase):
    def test_invalid_read_arguments(self):
        buffer = KeystreamBuffer(FakeKeyContext(), bytearray(16))
        for bad in ("5", 1.5, True, None):
            with self.subTest(bad=bad):
                with self.assertRaises(TypeError):
                    buffer.read(bad)
        with self.assertRaises(ValueError):
            buffer.read(-5)
        self.assertEqual(len(buffer._buf), 0)

    def test_invalid_initial_state(self):
        for size in (15, 17):
            with self.subTest(size=size):
                with self.assertRaises(ValueError):
                    KeystreamBuffer(FakeKeyContext(), bytearray(size))

    def test_engine_returns_39_instead_of_40(self):
        def bad_cycle(state, keys):
            return bytes(39), bytearray(16)

        with patch.dict(sys.modules, {
            "lex.lex.round_engine": engine_module(bad_cycle)
        }):
            buffer = KeystreamBuffer(FakeKeyContext(), bytearray(16))
            with self.assertRaisesRegex(ValueError, "exactly 40"):
                buffer.read(1)

    def test_engine_returns_invalid_state(self):
        def bad_cycle(state, keys):
            return bytes(40), bytearray(15)

        with patch.dict(sys.modules, {
            "lex.lex.round_engine": engine_module(bad_cycle)
        }):
            buffer = KeystreamBuffer(FakeKeyContext(), bytearray(16))
            with self.assertRaisesRegex(ValueError, "16-byte state"):
                buffer.read(1)

    def test_boundaries_39_40_41(self):
        for n in (39, 40, 41):
            calls = []

            def cycle(state, keys):
                start = len(calls) * 40
                calls.append(start)
                return bytes(range(start, start + 40)), bytearray(16)

            with self.subTest(n=n):
                with patch.dict(sys.modules, {
                    "lex.lex.round_engine": engine_module(cycle)
                }):
                    buffer = KeystreamBuffer(FakeKeyContext(), bytearray(16))
                    self.assertEqual(buffer.read(n), bytes(range(n)))
                    expected_cycles = (n + 39) // 40
                    self.assertEqual(len(calls), expected_cycles)
                    self.assertEqual(len(buffer._buf), expected_cycles * 40 - n)

    def test_split_reads_preserve_position(self):
        calls = []

        def cycle(state, keys):
            start = len(calls) * 40
            calls.append(start)
            return bytes(range(start, start + 40)), bytearray(16)

        with patch.dict(sys.modules, {
            "lex.lex.round_engine": engine_module(cycle)
        }):
            buffer = KeystreamBuffer(FakeKeyContext(), bytearray(16))
            output = buffer.read(39) + buffer.read(2) + buffer.read(39)
            self.assertEqual(output, bytes(range(80)))
            self.assertEqual(len(calls), 2)
            self.assertEqual(len(buffer._buf), 0)

    def test_zero_bytes_does_not_run_engine(self):
        def forbidden_cycle(state, keys):
            raise AssertionError("Engine must not run for read(0)")

        with patch.dict(sys.modules, {
            "lex.lex.round_engine": engine_module(forbidden_cycle)
        }):
            buffer = KeystreamBuffer(FakeKeyContext(), bytearray(16))
            self.assertEqual(buffer.read(0), b"")


class TestAPIErrorCases(unittest.TestCase):
    def setUp(self):
        self.patcher = patch.dict(sys.modules, {})
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        # install_mock_dependencies is safe only inside this test's scope.
        install_mock_dependencies()
        sys.modules.pop("lex.lex.api", None)
        self.addCleanup(lambda: sys.modules.pop("lex.lex.api", None))
        self.api = importlib.import_module("lex.lex.api")

    def test_api_rejects_wrong_key_iv_and_data(self):
        zero = bytes(16)
        with self.assertRaises(TypeError):
            self.api.LEX("not bytes", zero)
        with self.assertRaises(ValueError):
            self.api.LEX(bytes(15), zero)
        with self.assertRaises(ValueError):
            self.api.LEX(zero, bytes(17))
        with self.assertRaises(TypeError):
            self.api.LEX(zero, zero).process("HELLO")


if __name__ == "__main__":
    unittest.main()
