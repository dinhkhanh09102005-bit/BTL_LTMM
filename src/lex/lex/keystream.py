"""Stateful buffering for the 40-byte output cycles produced by LEX."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from .context import KeyContext

State: TypeAlias = bytes | bytearray | memoryview
_ROUND_KEY_SIZE = 16
_ROUND_KEY_COUNT = 11
_STATE_SIZE = 16
_CYCLE_SIZE = 40


class KeystreamBuffer:
    """Expose LEX's 40-byte cycles as one continuous byte stream.

    The buffer owns a copy of the initial/current state. A call to read()
    consumes exactly the requested number of bytes and retains any unused
    bytes for the next call.
    """

    def __init__(self, key_ctx: KeyContext, s0: State) -> None:
        self._state = self._coerce_state(s0, name="s0")

        round_keys = getattr(key_ctx, "round_keys", None)
        if not isinstance(round_keys, Sequence):
            raise TypeError("key_ctx.round_keys must be a sequence")
        if len(round_keys) != _ROUND_KEY_COUNT:
            raise ValueError("key_ctx.round_keys must contain 11 round keys")

        normalized_keys: list[bytes] = []
        for index, round_key in enumerate(round_keys):
            if not isinstance(round_key, (bytes, bytearray, memoryview)):
                raise TypeError(f"round key {index} must be bytes-like")
            if len(round_key) != _ROUND_KEY_SIZE:
                raise ValueError(f"round key {index} must contain 16 bytes")
            normalized_keys.append(bytes(round_key))

        self._round_keys = tuple(normalized_keys)
        self._buf = bytearray()

    @staticmethod
    def _coerce_state(value: State, *, name: str) -> bytearray:
        if not isinstance(value, (bytes, bytearray, memoryview)):
            raise TypeError(f"{name} must be bytes-like")
        if len(value) != _STATE_SIZE:
            raise ValueError(f"{name} must contain 16 bytes")
        return bytearray(value)

    @staticmethod
    def _coerce_chunk(value: object) -> bytes:
        if not isinstance(value, (bytes, bytearray, memoryview)):
            raise TypeError("lex_cycle keystream output must be bytes-like")
        if len(value) != _CYCLE_SIZE:
            raise ValueError("lex_cycle must return exactly 40 keystream bytes")
        return bytes(value)

    def read(self, n_bytes: int) -> bytes:
        """Return exactly n_bytes next keystream bytes."""
        if not isinstance(n_bytes, int) or isinstance(n_bytes, bool):
            raise TypeError("n_bytes must be an integer")
        if n_bytes < 0:
            raise ValueError("n_bytes must be nonnegative")
        if n_bytes == 0:
            return b""

        while len(self._buf) < n_bytes:
            from .round_engine import lex_cycle

            cycle_input = bytearray(self._state)
            chunk, next_state = lex_cycle(cycle_input, self._round_keys)

            chunk_bytes = self._coerce_chunk(chunk)
            normalized_state = self._coerce_state(
                next_state, name="lex_cycle next_state"
            )

            # Commit only after both outputs are valid.
            self._state = normalized_state
            self._buf.extend(chunk_bytes)

        result = bytes(self._buf[:n_bytes])
        del self._buf[:n_bytes]
        return result
