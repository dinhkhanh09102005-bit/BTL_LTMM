"""Trạng thái 4x4 byte lưu phẳng 16 byte theo thứ tự cột: ô (hàng r, cột c) ở chỉ số 4*c + r."""
from __future__ import annotations

State = bytearray


def idx(r: int, c: int) -> int:
    """Chỉ số phẳng của ô (r, c)."""
    if not (0 <= r < 4 and 0 <= c < 4):
        raise ValueError(f"hàng/cột phải trong [0, 3], nhận ({r}, {c})")
    return 4 * c + r


def get(state: State, r: int, c: int) -> int:
    """Đọc ô (r, c) của trạng thái."""
    return state[idx(r, c)]


def bytes_to_state(data: bytes) -> State:
    """Sao chép 16 byte thành trạng thái mới (không dùng chung bộ nhớ với đầu vào)."""
    if len(data) != 16:
        raise ValueError(f"trạng thái phải đúng 16 byte, nhận {len(data)}")
    return bytearray(data)


def state_to_bytes(state: State) -> bytes:
    """Xuất trạng thái thành bytes bất biến."""
    return bytes(state)
