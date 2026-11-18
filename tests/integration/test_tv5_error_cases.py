"""TV5 negative tests for input validation and cycle boundaries."""

from __future__ import annotations

import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from lex.lex.keystream import KeystreamBuffer
from tests.support.mock_lex_dependencies import install_mock_dependencies


def _engine_module(cycle):
    module = types.ModuleType("lex.lex.round_engine")
    module.lex_cycle = cycle
    return module


class TestBufferErrorsAndBoundaries(unittest.TestCase):
    def test_invalid_initial_state(self):
        context = SimpleNamespace(round_keys=(bytes(16),) * 11)
        for invalid in ("not bytes", None):
            with self.subTest(invalid=invalid), self.assertRaises(TypeError):
                KeystreamBuffer(context, invalid)
        for invalid in (bytes(15), bytes(17)):
            with self.subTest(length=len(invalid)), self.assertRaises(ValueError):
                KeystreamBuffer(context, invalid)

    def test_boundaries_39_40_41(self):
        for n in (39, 40, 41):
            calls: list[int] = []

            def cycle(state, keys):
                del state, keys
                start = len(calls) * 40
                calls.append(start)
                return bytes((start + i) % 256 for i in range(40)), bytes(16)

            with self.subTest(n=n), patch.dict(
                sys.modules, {"lex.lex.round_engine": _engine_module(cycle)}
            ):
                buffer = KeystreamBuffer(
                    SimpleNamespace(round_keys=(bytes(16),) * 11), bytes(16)
                )
                self.assertEqual(
                    buffer.read(n), bytes(i % 256 for i in range(n))
                )
                self.assertEqual(len(calls), (n + 39) // 40)
                self.assertEqual(
                    len(buffer._buf), len(calls) * 40 - n
                )

    def test_engine_returns_39_instead_of_40(self):
        def bad_cycle(state, keys):
            del state, keys
            return bytes(39), bytes(16)

        with patch.dict(
            sys.modules, {"lex.lex.round_engine": _engine_module(bad_cycle)}
        ):
            buffer = KeystreamBuffer(
                SimpleNamespace(round_keys=(bytes(16),) * 11), bytes(16)
            )
            with self.assertRaisesRegex(ValueError, "exactly 40"):
                buffer.read(1)

    def test_engine_returns_invalid_state(self):
        def bad_cycle(state, keys):
            del state, keys
            return bytes(40), bytes(15)

        with patch.dict(
            sys.modules, {"lex.lex.round_engine": _engine_module(bad_cycle)}
        ):
            buffer = KeystreamBuffer(
                SimpleNamespace(round_keys=(bytes(16),) * 11), bytes(16)
            )
            with self.assertRaisesRegex(ValueError, "16 bytes"):
                buffer.read(1)

    def test_bad_read_arguments(self):
        buffer = KeystreamBuffer(
            SimpleNamespace(round_keys=(bytes(16),) * 11), bytes(16)
        )
        for invalid in (True, 1.5, "5", None):
            with self.subTest(invalid=invalid), self.assertRaises(TypeError):
                buffer.read(invalid)
        with self.assertRaises(ValueError):
            buffer.read(-1)

    def test_split_reads_preserve_position(self):
        calls: list[int] = []

        def cycle(state, keys):
            del state, keys
            start = len(calls) * 40
            calls.append(start)
            return bytes((start + i) % 256 for i in range(40)), bytes(16)

        with patch.dict(
            sys.modules, {"lex.lex.round_engine": _engine_module(cycle)}
        ):
            buffer = KeystreamBuffer(
                SimpleNamespace(round_keys=(bytes(16),) * 11), bytes(16)
            )
            output = buffer.read(39) + buffer.read(2) + buffer.read(39)
            self.assertEqual(output, bytes(range(80)))
            self.assertEqual(len(calls), 2)
            self.assertEqual(len(buffer._buf), 0)


class TestAPIErrorCases(unittest.TestCase):
    def setUp(self):
        self.patcher = patch.dict(sys.modules, {})
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
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
