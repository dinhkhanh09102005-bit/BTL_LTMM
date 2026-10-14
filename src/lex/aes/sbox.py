"""S-box AES và hằng số vòng RCON, sinh từ định nghĩa toán học (không chép bảng).

S(a) = M * a^-1 + 0x63 trong GF(2^8), với a^-1 = a^254 và S(0) = 0x63.
"""
from __future__ import annotations

from ..core.gf256 import gmul, xtime


def _inverse(a: int) -> int:
    """Nghịch đảo nhân a^254 (0 ánh xạ về 0)."""
    result, power, exp = 1, a, 254
    while exp:
        if exp & 1:
            result = gmul(result, power)
        power = gmul(power, power)
        exp >>= 1
    return result if a else 0


def _rotl8(x: int, n: int) -> int:
    return ((x << n) | (x >> (8 - n))) & 0xFF


def _sbox_entry(a: int) -> int:
    x = _inverse(a)
    return x ^ _rotl8(x, 1) ^ _rotl8(x, 2) ^ _rotl8(x, 3) ^ _rotl8(x, 4) ^ 0x63


def _make_rcon(n: int) -> tuple[int, ...]:
    out, r = [], 1
    for _ in range(n):
        out.append(r)
        r = xtime(r)
    return tuple(out)


SBOX: tuple[int, ...] = tuple(_sbox_entry(a) for a in range(256))
RCON: tuple[int, ...] = _make_rcon(10)     # 01 02 04 08 10 20 40 80 1B 36
