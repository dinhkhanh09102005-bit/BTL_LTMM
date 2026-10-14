"""Ngữ cảnh khóa (bất biến) và ngữ cảnh luồng (trạng thái chạy)."""
from __future__ import annotations

from dataclasses import dataclass

State = bytearray
RoundKeys = list[bytes]


@dataclass(frozen=True)
class KeyContext:
    """11 khóa vòng K0..K10 sinh từ khóa bí mật."""
    round_keys: RoundKeys


@dataclass
class StreamContext:
    """Trạng thái đầu vào cho chu kỳ kế tiếp."""
    state: State
