"""Mở rộng khóa AES-128: 16 byte -> 11 khóa vòng K0..K10 (FIPS-197 mục 5.2)."""
from __future__ import annotations

from .sbox import RCON, SBOX

RoundKeys = list[bytes]


def expand_key(key: bytes) -> RoundKeys:
    """Sinh 11 khóa vòng, mỗi khóa 16 byte."""
    if len(key) != 16:
        raise ValueError(f"khóa AES-128 phải đúng 16 byte, nhận {len(key)}")
    words: list[bytes] = [bytes(key[4 * i:4 * i + 4]) for i in range(4)]
    for i in range(4, 44):
        temp = words[i - 1]
        if i % 4 == 0:
            rot = temp[1:] + temp[:1]                               # RotWord
            sub = bytes(SBOX[b] for b in rot)                        # SubWord
            temp = bytes([sub[0] ^ RCON[i // 4 - 1]]) + sub[1:]
        words.append(bytes(a ^ b for a, b in zip(words[i - 4], temp)))
    return [b"".join(words[4 * r:4 * r + 4]) for r in range(11)]
