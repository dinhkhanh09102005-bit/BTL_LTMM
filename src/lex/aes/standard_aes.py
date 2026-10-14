"""Mã hóa một khối AES-128 chuẩn (vòng 10 KHÔNG có MixColumns). Chỉ dùng cho IV setup."""
from __future__ import annotations

from .key_schedule import RoundKeys
from .transforms import add_round_key, mix_columns, shift_rows, sub_bytes


def encrypt_block(round_keys: RoundKeys, block: bytes) -> bytes:
    """AES-128: ARK(K0); 9 vòng SB-SR-MC-ARK; vòng 10 SB-SR-ARK."""
    if len(round_keys) != 11:
        raise ValueError(f"cần 11 khóa vòng, nhận {len(round_keys)}")
    if len(block) != 16:
        raise ValueError(f"khối phải đúng 16 byte, nhận {len(block)}")
    state = add_round_key(bytearray(block), round_keys[0])
    for r in range(1, 10):
        state = add_round_key(mix_columns(shift_rows(sub_bytes(state))), round_keys[r])
    state = add_round_key(shift_rows(sub_bytes(state)), round_keys[10])
    return bytes(state)
