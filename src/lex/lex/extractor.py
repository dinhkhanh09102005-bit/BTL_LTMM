"""Trích 4 byte rò rỉ sau AddRoundKey của mỗi vòng (đối chiếu mã C LEX-v2, conventions.md T3/T8).

Chỉ số là vị trí phẳng idx = 4*cột + hàng, liệt kê theo đúng thứ tự ghi vào keystream.
Theo ký hiệu S[hàng][cột]:
  vòng lẻ  : S[2][2], S[2][0], S[0][2], S[0][0]  (byte 10, 2, 8, 0)
  vòng chẵn: S[3][2], S[3][0], S[1][2], S[1][0]  (byte 11, 3, 9, 1)
"""
from __future__ import annotations

State = bytearray

LEAK_INDICES_ODD: tuple[int, int, int, int] = (10, 2, 8, 0)      # vòng 1, 3, 5, 7, 9
LEAK_INDICES_EVEN: tuple[int, int, int, int] = (11, 3, 9, 1)     # vòng 2, 4, 6, 8, 10


def extract_leak(state: State, round_no: int) -> bytes:
    """Trả về 4 byte rò rỉ của vòng round_no (1..10); không sửa state."""
    if not isinstance(round_no, int) or isinstance(round_no, bool):
        raise TypeError(f"round_no phải là int, nhận {type(round_no).__name__}")
    if not 1 <= round_no <= 10:
        raise ValueError(f"round_no phải trong [1, 10], nhận {round_no}")
    if len(state) != 16:
        raise ValueError(f"trạng thái phải đúng 16 byte, nhận {len(state)}")
    indices = LEAK_INDICES_ODD if round_no % 2 == 1 else LEAK_INDICES_EVEN
    return bytes(state[i] for i in indices)
