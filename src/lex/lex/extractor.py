"""TV3 - Trich byte ro ri (leak) cua LEX-128 v2.

Moi vong r (1..10) cua chu ky sinh dong, sau AddRoundKey, LEX lay 4 byte
cua trang thai lam keystream (docs/conventions.md, T2/T3/T8):

    vong le  (1,3,5,7,9) : byte 10, 2, 8, 0   (S[2][2], S[2][0], S[0][2], S[0][0])
    vong chan(2,4,...,10): byte 11, 3, 9, 1   (S[3][2], S[3][0], S[1][2], S[1][0])

Chi so byte theo column-major: idx = 4*c + r. Thu tu trong tuple chinh la
thu tu ghi ra keystream (ma C gom 4 byte thanh tu 32 bit roi ghi little-endian).
"""

from __future__ import annotations

from typing import Union

ByteData = Union[bytes, bytearray, memoryview]

STATE_BYTES = 16
ROUNDS_PER_CYCLE = 10
LEAK_BYTES_PER_ROUND = 4

LEAK_INDICES_ODD: tuple[int, ...] = (10, 2, 8, 0)
LEAK_INDICES_EVEN: tuple[int, ...] = (11, 3, 9, 1)


def _as_block16(value: object, name: str) -> bytes:
    """Kiem tra mot khoi 16 byte (state/round key) va tra ve ban sao bytes.

    Sai kieu -> TypeError, sai do dai -> ValueError (docs/conventions.md, muc 8).
    Dung chung cho extractor.py va round_engine.py (cung thuoc TV3).
    """
    if not isinstance(value, (bytes, bytearray, memoryview)):
        raise TypeError(
            f"{name} phai la bytes/bytearray/memoryview, nhan {type(value).__name__}"
        )
    data = bytes(value)
    if len(data) != STATE_BYTES:
        raise ValueError(f"{name} phai dai {STATE_BYTES} byte, nhan {len(data)}")
    return data


def _check_round_no(round_no: object) -> int:
    # bool la lop con cua int trong Python nen phai loai rieng.
    if isinstance(round_no, bool) or not isinstance(round_no, int):
        raise TypeError(f"round_no phai la int, nhan {type(round_no).__name__}")
    if not 1 <= round_no <= ROUNDS_PER_CYCLE:
        raise ValueError(f"round_no phai trong 1..{ROUNDS_PER_CYCLE}, nhan {round_no}")
    return round_no


def leak_indices(round_no: int) -> tuple[int, ...]:
    """Chi so byte ro ri cua vong round_no, dung thu tu ghi ra keystream."""
    round_no = _check_round_no(round_no)
    return LEAK_INDICES_ODD if round_no % 2 == 1 else LEAK_INDICES_EVEN


def extract_leak(state: ByteData, round_no: int) -> bytes:
    """Tra ve 4 byte ro ri cua state sau AddRoundKey cua vong round_no.

    Ham thuan: khong sua state dau vao.

    >>> extract_leak(bytes(range(16)), 1).hex()
    '0a020800'
    >>> extract_leak(bytes(range(16)), 2).hex()
    '0b030901'
    """
    data = _as_block16(state, "state")
    return bytes(data[i] for i in leak_indices(round_no))
