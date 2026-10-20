"""TV5 - Buffer keystream lien tuc, moi chu ky LEX sinh 40 byte."""
from __future__ import annotations

class KeystreamBuffer:
    def __init__(self, key_ctx, s0: bytearray) -> None:
        if len(s0) != 16:
            raise ValueError("s0 must contain 16 bytes")
        self._key_ctx = key_ctx
        self._state = bytearray(s0)
        self._buf = bytearray()

    def read(self, n_bytes: int) -> bytes:
        if not isinstance(n_bytes, int) or isinstance(n_bytes, bool):
            raise TypeError("n_bytes must be an integer")
        if n_bytes < 0:
            raise ValueError("n_bytes must be nonnegative")
        while len(self._buf) < n_bytes:
            # TV3 se cung cap lex_cycle theo hop dong da thong nhat.
            from .round_engine import lex_cycle
            chunk, next_state = lex_cycle(self._state, self._key_ctx.round_keys)
            if not isinstance(chunk, (bytes, bytearray)) or len(chunk) != 40:
                raise ValueError("lex_cycle must return exactly 40 keystream bytes")
            if len(next_state) != 16:
                raise ValueError("lex_cycle must return a 16-byte state")
            self._state = bytearray(next_state)
            self._buf.extend(chunk)
        result = bytes(self._buf[:n_bytes])
        del self._buf[:n_bytes]
        return result
