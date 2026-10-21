"""Gia lap CHI de test/demo TV5. KHONG phai thuat toan mat ma LEX."""
from __future__ import annotations

import sys
import types
from types import SimpleNamespace


def _check_bytes(value):
    if not isinstance(value, (bytes, bytearray, memoryview)):
        raise TypeError("Expected bytes-like input")
    return bytes(value)


def _check_16(value):
    result = _check_bytes(value)
    if len(result) != 16:
        raise ValueError("Key and IV must each contain 16 bytes")
    return result


def _make_key_context(key):
    return SimpleNamespace(round_keys=[key] * 11)


def _compute_s0(key_ctx, iv):
    return bytearray(iv)


def _fake_lex_cycle(state, round_keys):
    """40 byte gia lap va state 16 byte tiep theo."""
    count = int.from_bytes(state[:4], "big")
    offset = (sum(state[4:]) + round_keys[0][0]) % 256
    stream = bytes((offset + count * 40 + i) % 256 for i in range(40))
    next_state = bytearray(state)
    next_state[:4] = (count + 1).to_bytes(4, "big")
    return stream, next_state


def install_mock_dependencies() -> None:
    """Dang ky mock trong sys.modules TRUOC KHI import lex.lex.api."""
    validation = types.ModuleType("lex.lex.validation")
    validation.validate_key = _check_16
    validation.validate_iv = _check_16
    validation.validate_data = _check_bytes

    iv_setup = types.ModuleType("lex.lex.iv_setup")
    iv_setup.make_key_context = _make_key_context
    iv_setup.compute_s0 = _compute_s0

    round_engine = types.ModuleType("lex.lex.round_engine")
    round_engine.lex_cycle = _fake_lex_cycle

    sys.modules["lex.lex.validation"] = validation
    sys.modules["lex.lex.iv_setup"] = iv_setup
    sys.modules["lex.lex.round_engine"] = round_engine
