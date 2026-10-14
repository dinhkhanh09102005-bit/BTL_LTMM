"""Bộ đệm keystream: sinh theo chu kỳ 40 byte, cấp phát chunk độ dài tùy ý."""
from __future__ import annotations

from .context import KeyContext, StreamContext
from .round_engine import lex_cycle

State = bytearray


class KeystreamBuffer:
    """Nguồn keystream liên tục. Phần dư của chu kỳ hiện tại được giữ cho lần đọc sau."""

    def __init__(self, key_ctx: KeyContext, s0: State) -> None:
        self._key_ctx = key_ctx
        self._stream = StreamContext(state=bytearray(s0))
        self._buf = bytearray()          # keystream đã sinh nhưng chưa tiêu thụ

    def read(self, n_bytes: int) -> bytes:
        """Trả về n_bytes byte keystream kế tiếp (n_bytes >= 0)."""
        if not isinstance(n_bytes, int) or isinstance(n_bytes, bool):
            raise TypeError(f"n_bytes phải là int, nhận {type(n_bytes).__name__}")
        if n_bytes < 0:
            raise ValueError(f"n_bytes phải >= 0, nhận {n_bytes}")
        while len(self._buf) < n_bytes:
            chunk, self._stream.state = lex_cycle(self._stream.state, self._key_ctx.round_keys)
            self._buf += chunk
        out = bytes(self._buf[:n_bytes])
        del self._buf[:n_bytes]
        return out
