from collections.abc import Sequence
from typing import Union
from .transforms import sub_bytes, shift_rows, mix_columns, add_round_key

ByteData = Union[bytes, bytearray, memoryview]

def encrypt_block(round_keys: Sequence[bytes], block: ByteData) -> bytes:
    """Ma hoa mot khoi 16 byte bang AES-128 chuan."""
    # 1. Kiem tra khoi du lieu dau vao.
    if not isinstance(block, (bytes, bytearray, memoryview)):
        raise TypeError("block must be bytes, bytearray, or memoryview")
    block = bytes(block)
    if len(block) != 16:
        raise ValueError("block length must be exactly 16 bytes")

    # 2. Kiem tra danh sach khoa vong.
    if not isinstance(round_keys, Sequence):
        raise TypeError("round_keys must be a sequence of 11 keys")
    if len(round_keys) != 11:
        raise ValueError("AES-128 requires exactly 11 round keys")

    checked_keys = []
    for index, key in enumerate(round_keys):
        if not isinstance(key, (bytes, bytearray, memoryview)):
            raise TypeError(f"round_keys[{index}] must be bytes-like")
        key = bytes(key)
        if len(key) != 16:
            raise ValueError(f"round_keys[{index}] must be exactly 16 bytes")
        checked_keys.append(key)

    # 3. Chuyen khoi dau vao thanh state 16 byte.
    state = bytearray(block)

    # 4. Buoc khoi dau: AddRoundKey voi K0.
    state = add_round_key(state, checked_keys[0])
    # 5. Chay cac vong AES tu 1 den 9.
    for round_no in range(1, 10):
        state = sub_bytes(state)
        state = shift_rows(state)
        state = mix_columns(state)
        state = add_round_key(state, checked_keys[round_no])

    # 6. Vong cuoi: khong thuc hien MixColumns.
    state = sub_bytes(state)
    state = shift_rows(state)
    state = add_round_key(state, checked_keys[10])

    # 7. Tra ve khoi ban ma 16 byte.
    return bytes(state)
