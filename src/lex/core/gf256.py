"""Phép toán trên trường GF(2^8) với đa thức tối giản x^8 + x^4 + x^3 + x + 1 (0x11B).

Chỉ dùng XOR, dịch bit và AND; không dùng phép nhân/cộng số nguyên thông thường
trên các phần tử của trường.
"""
from __future__ import annotations

POLY: int = 0x11B


def _check_byte(a: int) -> None:
    if not isinstance(a, int) or isinstance(a, bool):
        raise TypeError(f"phần tử GF(2^8) phải là int, nhận {type(a).__name__}")
    if not 0 <= a <= 0xFF:
        raise ValueError(f"phần tử GF(2^8) phải nằm trong [0, 255], nhận {a}")


def xtime(a: int) -> int:
    """Nhân a với x (tức 0x02) trong GF(2^8)."""
    _check_byte(a)
    a <<= 1
    if a & 0x100:
        a ^= POLY
    return a


def gmul(a: int, b: int) -> int:
    """Nhân hai phần tử của GF(2^8) (phép nhân nông dân Nga)."""
    _check_byte(a)
    _check_byte(b)
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        if a & 0x100:
            a ^= POLY
        b >>= 1
    return result
