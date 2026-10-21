"""TV3 - Vong va chu ky sinh dong cua LEX-128 v2.

Mot chu ky (docs/spec_lex.md, muc 4), dau vao la trang thai S (lan dau la S0):

    for r in 1..10:
        S = SubBytes(S)
        S = ShiftRows(S)
        S = MixColumns(S)        # co o CA 10 vong, ke ca vong 10 (T1)
        S = S xor K_r            # K_r = round_keys[r]; KHONG co K_0 (muc 7)
        keystream += extract_leak(S, r)     # leak sau ARK (T2, T3)

    -> 40 byte keystream, va S10 lam dau vao TRUC TIEP cua chu ky sau (T4).

Khac AES chuan (aes/standard_aes.py, chi dung o pha IV setup):
khong pre-whitening K0, vong 10 van co MixColumns, co trich leak.

Phu thuoc: aes/transforms.py (TV1). Goi qua ten module `transforms.xxx`
de tham so `mix_columns` khong che ten ham, va de test thay duoc bang fake.
"""

from __future__ import annotations

from typing import Sequence, Union

from lex.aes import transforms
from lex.lex.extractor import (
    LEAK_BYTES_PER_ROUND,
    ROUNDS_PER_CYCLE,
    _as_block16,
    extract_leak,
)

ByteData = Union[bytes, bytearray, memoryview]
State = bytearray
RoundKeys = Sequence[bytes]

ROUND_KEY_COUNT = 11
KEYSTREAM_BYTES_PER_CYCLE = ROUNDS_PER_CYCLE * LEAK_BYTES_PER_ROUND  # 40


def _check_round_keys(round_keys: object) -> tuple[bytes, ...]:
    """Kiem tra 11 round key K0..K10, moi khoa 16 byte; tra ve tuple bytes."""
    if not isinstance(round_keys, (list, tuple)):
        raise TypeError(
            f"round_keys phai la list/tuple, nhan {type(round_keys).__name__}"
        )
    if len(round_keys) != ROUND_KEY_COUNT:
        raise ValueError(
            f"round_keys phai co {ROUND_KEY_COUNT} khoa (K0..K10), nhan {len(round_keys)}"
        )
    return tuple(_as_block16(k, f"round_keys[{i}]") for i, k in enumerate(round_keys))


def lex_round(state: ByteData, round_key: ByteData, *, mix_columns: bool) -> State:
    """Mot vong: SubBytes -> ShiftRows -> (MixColumns neu mix_columns) -> AddRoundKey.

    Ham thuan: tra ve bytearray moi 16 byte, khong sua `state`.
    Chu ky LEX luon goi voi mix_columns=True; tham so de tuong minh theo hop dong.
    """
    if not isinstance(mix_columns, bool):
        raise TypeError(f"mix_columns phai la bool, nhan {type(mix_columns).__name__}")
    s = bytearray(_as_block16(state, "state"))  # ban sao -> state goc an toan
    key = _as_block16(round_key, "round_key")

    s = transforms.sub_bytes(s)
    s = transforms.shift_rows(s)
    if mix_columns:
        s = transforms.mix_columns(s)
    s = transforms.add_round_key(s, key)
    return bytearray(s)


def lex_cycle(state: ByteData, round_keys: RoundKeys) -> tuple[bytes, State]:
    """Chay mot chu ky 10 vong tu `state`.

    Tra ve (keystream, next_state):
      - keystream: 40 byte = leak_1 || leak_2 || ... || leak_10
      - next_state: S10 (sau MC va ARK K10 cua vong 10), dung nguyen cho
        chu ky ke tiep, khong cong them khoa nao.
    round_keys[0] (K0) duoc kiem tra nhung KHONG dung trong chu ky.
    """
    keys = _check_round_keys(round_keys)
    s = bytearray(_as_block16(state, "state"))

    keystream = bytearray()
    for r in range(1, ROUNDS_PER_CYCLE + 1):
        s = lex_round(s, keys[r], mix_columns=True)
        keystream += extract_leak(s, r)

    return bytes(keystream), s
