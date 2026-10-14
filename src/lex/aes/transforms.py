"""Bốn phép biến đổi AES trên trạng thái 16 byte (column-major). Tất cả là hàm thuần."""
from __future__ import annotations

from ..core.gf256 import gmul
from .sbox import SBOX

State = bytearray

# Bảng nhân sẵn cho MixColumns, tính một lần từ gmul.
_MUL2: tuple[int, ...] = tuple(gmul(a, 2) for a in range(256))
_MUL3: tuple[int, ...] = tuple(gmul(a, 3) for a in range(256))


def _check_state(state: bytes | bytearray) -> None:
    if len(state) != 16:
        raise ValueError(f"trạng thái phải đúng 16 byte, nhận {len(state)}")


def sub_bytes(state: State) -> State:
    """Thay từng byte qua S-box."""
    _check_state(state)
    return bytearray(SBOX[b] for b in state)


def shift_rows(state: State) -> State:
    """Hàng r dịch trái r cột: new[r][c] = old[r][(c + r) % 4]."""
    _check_state(state)
    out = bytearray(16)
    for c in range(4):
        for r in range(4):
            out[4 * c + r] = state[4 * ((c + r) % 4) + r]
    return out


def mix_columns(state: State) -> State:
    """Nhân từng cột với ma trận MDS circ(2, 3, 1, 1) trong GF(2^8)."""
    _check_state(state)
    out = bytearray(16)
    for c in range(0, 16, 4):
        a0, a1, a2, a3 = state[c], state[c + 1], state[c + 2], state[c + 3]
        out[c] = _MUL2[a0] ^ _MUL3[a1] ^ a2 ^ a3
        out[c + 1] = a0 ^ _MUL2[a1] ^ _MUL3[a2] ^ a3
        out[c + 2] = a0 ^ a1 ^ _MUL2[a2] ^ _MUL3[a3]
        out[c + 3] = _MUL3[a0] ^ a1 ^ a2 ^ _MUL2[a3]
    return out


def add_round_key(state: State, round_key: bytes) -> State:
    """XOR trạng thái với khóa vòng 16 byte."""
    _check_state(state)
    if len(round_key) != 16:
        raise ValueError(f"khóa vòng phải đúng 16 byte, nhận {len(round_key)}")
    return bytearray(a ^ b for a, b in zip(state, round_key))
