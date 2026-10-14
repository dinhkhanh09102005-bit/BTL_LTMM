"""Động cơ 10 vòng của LEX. Khác AES chuẩn: không có K0 và vòng 10 VẪN có MixColumns."""
from __future__ import annotations

from ..aes.transforms import add_round_key, shift_rows, sub_bytes
from ..aes.transforms import mix_columns as _mix_columns
from .extractor import extract_leak

State = bytearray
RoundKeys = list[bytes]

ROUNDS = 10
KEYSTREAM_BYTES_PER_CYCLE = 4 * ROUNDS      # 40


def lex_round(state: State, round_key: bytes, *, mix_columns: bool) -> State:
    """Một vòng: SubBytes -> ShiftRows -> [MixColumns] -> AddRoundKey. Trả về trạng thái mới."""
    s = shift_rows(sub_bytes(state))
    if mix_columns:
        s = _mix_columns(s)
    return add_round_key(s, round_key)


def lex_cycle(state: State, round_keys: RoundKeys) -> tuple[bytes, State]:
    """Chạy 10 vòng giống hệt nhau từ `state`.

    Trả về (40 byte keystream, S10). S10 là đầu vào của vòng 1 ở chu kỳ kế tiếp.
    Không sửa `state` đầu vào.
    """
    if len(round_keys) != 11:
        raise ValueError(f"cần 11 khóa vòng, nhận {len(round_keys)}")
    current = bytearray(state)
    leaked = bytearray()
    for r in range(1, ROUNDS + 1):
        current = lex_round(current, round_keys[r], mix_columns=True)
        leaked += extract_leak(current, r)
    return bytes(leaked), current
