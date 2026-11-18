"""TV5 streaming-buffer contract tests."""

from __future__ import annotations

import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from lex.lex.keystream import KeystreamBuffer


def _engine_module(cycle):
    module = types.ModuleType("lex.lex.round_engine")
    module.lex_cycle = cycle
    return module


def _key_context():
    return SimpleNamespace(round_keys=(bytes(16),) * 11)


class TestKeystreamBuffer(unittest.TestCase):
    def test_chunks_and_boundaries(self):
        calls: list[int] = []

        def fake_cycle(state, keys):
            del state, keys
            start = len(calls) * 40
            calls.append(start)
            return bytes((start + i) % 256 for i in range(40)), bytes(16)

        with patch.dict(
            sys.modules, {"lex.lex.round_engine": _engine_module(fake_cycle)}
        ):
            buffer = KeystreamBuffer(_key_context(), bytes(16))
            self.assertEqual(buffer.read(7), bytes(range(7)))
            self.assertEqual(buffer.read(10), bytes(range(7, 17)))
            self.assertEqual(buffer.read(30), bytes(range(17, 47)))
            self.assertEqual(len(buffer._buf), 33)
            self.assertEqual(buffer.read(0), b"")
            self.assertEqual(buffer.read(53), bytes(range(47, 100)))
            self.assertEqual(len(buffer._buf), 20)
            self.assertEqual(len(calls), 3)

    def test_split_reads_equal_one_contiguous_read(self):
        def fake_cycle(state, keys):
            del keys
            counter = int.from_bytes(state[:4], "big")
            output = bytes((counter * 40 + i) % 256 for i in range(40))
            next_state = bytearray(state)
            next_state[:4] = (counter + 1).to_bytes(4, "big")
            return output, next_state

        with patch.dict(
            sys.modules, {"lex.lex.round_engine": _engine_module(fake_cycle)}
        ):
            split = KeystreamBuffer(_key_context(), bytes(16))
            contiguous = KeystreamBuffer(_key_context(), bytes(16))
            actual = split.read(7) + split.read(10) + split.read(83)
            self.assertEqual(actual, contiguous.read(100))

    def test_zero_read_does_not_call_engine(self):
        def forbidden_cycle(state, keys):
            del state, keys
            raise AssertionError("read(0) must not generate a cycle")

        with patch.dict(
            sys.modules, {"lex.lex.round_engine": _engine_module(forbidden_cycle)}
        ):
            buffer = KeystreamBuffer(_key_context(), bytes(16))
            self.assertEqual(buffer.read(0), b"")

    def test_invalid_read_lengths_are_rejected_without_consuming(self):
        def fake_cycle(state, keys):
            del state, keys
            return bytes(range(40)), bytes(16)

        with patch.dict(
            sys.modules, {"lex.lex.round_engine": _engine_module(fake_cycle)}
        ):
            buffer = KeystreamBuffer(_key_context(), bytes(16))
            for invalid in (True, 1.5, "5", None):
                with self.subTest(invalid=invalid), self.assertRaises(TypeError):
                    buffer.read(invalid)
            with self.assertRaises(ValueError):
                buffer.read(-1)
            self.assertEqual(buffer.read(3), bytes(range(3)))

    def test_bad_engine_output_does_not_commit_state(self):
        def bad_cycle(state, keys):
            del keys
            state[0] = 99
            return "bad", bytes(16)

        with patch.dict(
            sys.modules, {"lex.lex.round_engine": _engine_module(bad_cycle)}
        ):
            buffer = KeystreamBuffer(_key_context(), bytes(16))
            with self.assertRaises(TypeError):
                buffer.read(1)
            self.assertEqual(buffer._state, bytearray(16))
            self.assertEqual(buffer._buf, bytearray())

    def test_bad_next_state_is_rejected(self):
        def bad_cycle(state, keys):
            del state, keys
            return bytes(40), bytes(15)

        with patch.dict(
            sys.modules, {"lex.lex.round_engine": _engine_module(bad_cycle)}
        ):
            buffer = KeystreamBuffer(_key_context(), bytes(16))
            with self.assertRaises(ValueError):
                buffer.read(1)
            self.assertEqual(buffer._state, bytearray(16))
            self.assertEqual(buffer._buf, bytearray())

    def test_initial_state_is_copied(self):
        initial = bytearray(16)
        buffer = KeystreamBuffer(_key_context(), initial)
        initial[0] = 99
        self.assertEqual(buffer._state[0], 0)

    def test_round_keys_are_validated(self):
        with self.assertRaises(TypeError):
            KeystreamBuffer(SimpleNamespace(), bytes(16))
        with self.assertRaises(ValueError):
            KeystreamBuffer(
                SimpleNamespace(round_keys=(bytes(16),)), bytes(16)
            )
        bad_keys = (bytes(16),) * 10 + (bytes(15),)
        with self.assertRaises(ValueError):
            KeystreamBuffer(
                SimpleNamespace(round_keys=bad_keys), bytes(16)
            )


if __name__ == "__main__":
    unittest.main()
